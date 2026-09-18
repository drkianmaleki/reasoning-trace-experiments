#!/usr/bin/env python3
"""s3_judge_continuations.py -- pipeline v2 step (8/9): the judge on the continuations of a
resampling run (pre-registration v2, Sections 4 and 8.1).

  python scripts/s3_judge_continuations.py --run runs/experiments/resample_blocks_<stamp>/ [--dry-run]
      [--out <run>/judge_<stamp>/] [--wave-size 4] [--claude-ceiling 80] [--noise-cuts c004:9,e036:6] [--no-noise]
      [--poll-seconds 60]

Labeling order (v2, 8.1): cut-0 first, then the two traces' cuts interleaved by m (C-B00, E-B00,
C-B01, E-B01, ...).  The cut groups are labeled in waves of --wave-size consecutive groups (one
Message Batch per wave, about 100 continuations at 25 per cut, so that a batch ends in minutes);
before each wave the cumulative Claude cost plus the wave's projected cost (safety factor 1.3)
is checked against the ceiling ($80): when it would be exceeded, labeling stops, the unlabeled
cuts are listed in unlabeled_cuts.csv, and a line goes to the run's DEPARTURES.md.  Sampling is
independent of this ceiling.  A wave: every continuation split with s0_split (thinking part
only, decision 19) into sentences_continuations_w<k>.jsonl; s1_judge in batch mode -- prompt v3,
Sonnet 5, adaptive thinking low, the prefix shown with its reviewed labels (listing v4; for
cut(B_m) the sentences 0 ... block-end index) -- with one follow-up batch for failures, then the
formatted third attempt (--retry-failed); the derivation with R1-R4.  After the waves the pnext
rows are merged into pnext_<run_id>.csv keyed by trace and m, and the noise subset of
registration 4.2 -- the continuations of the C-trace cut with the largest Delta_m (from
pcut.csv) and of cut(E-B06) -- is labeled a second time (inside the same ceiling) and the two
labelings' agreement (Level 1 kappa over sentences, first-new-node agreement) is written to
noise_subset.csv / .md.  A finished wave folder (s3_wave_done.json) is skipped on a re-run.
--dry-run builds the documents of every wave and projects the cost from the measured rates.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import derivation as D  # noqa: E402
import s0_split as S0  # noqa: E402
import s1_judge as S  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
RATES = {"thinking_per_sentence": 34.0, "label_per_sentence": 7.0, "text_per_sentence": 23.9, "prefix_code_factor": 1.6,
         "system_prompt_tokens": 5820}
SAFETY = 1.3  # the smoke batch billed 1.3 x the projection (56 output tokens per sentence instead of 41)
CLAUDE_CEILING_USD = 80.0
WAVE_SIZE = 4
NOISE_E_CUT = 6  # cut(E-B06), registration 4.2
PNEXT_FIELDS = ["trace_id", "m", "prefix_id", "block_end_s", "last_node_label", "n", "n_labeled", "n_failed"] + [f"next_{x}" for x in D.L1_ORDER] + ["opens_block", "first_is_wait"]


def read_jsonl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def load_run(run_dir: Path) -> tuple[list[dict], list[dict]]:
    """(continuations of the cut conditions, pcut rows) of a resampling run."""
    recs = [r for r in read_jsonl(run_dir / "continuations.jsonl") if r.get("condition") in ("cut0", "cut")]
    pcut = []
    if (run_dir / "pcut.csv").exists():
        with open(run_dir / "pcut.csv", encoding="utf-8") as fh:
            pcut = list(csv.DictReader(fh))
    return recs, pcut


def cut_groups(recs: list[dict]) -> list[tuple[str, list[dict]]]:
    """[(group key, records)] in the registered labeling order: cut-0, then the two traces'
    cuts interleaved by m (C-B00, E-B00, C-B01, E-B01, ...)."""
    by_key: dict[tuple, list[dict]] = {}
    for r in recs:
        key = ("cut0", None) if r["condition"] == "cut0" else (r["trace_arm"], int(r["block"]))
        by_key.setdefault(key, []).append(r)
    groups: list[tuple[str, list[dict]]] = []
    if ("cut0", None) in by_key:
        groups.append(("cut0", sorted(by_key[("cut0", None)], key=lambda r: r["seq"])))
    ms = sorted({k[1] for k in by_key if k[0] != "cut0"})
    for m in ms:
        for arm in ("c004", "e036"):
            if (arm, m) in by_key:
                groups.append((f"{arm}_B{m:02d}", sorted(by_key[(arm, m)], key=lambda r: r["seq"])))
    return groups


def waves_of(groups: list[tuple[str, list[dict]]], wave_size: int) -> list[list[tuple[str, list[dict]]]]:
    return [groups[i:i + wave_size] for i in range(0, len(groups), wave_size)]


def split_collection(name: str, recs: list[dict], out_dir: Path) -> tuple[Path, dict[str, dict], int]:
    """sentences_<name>.jsonl (thinking part only) and the continuation meta per record."""
    path = out_dir / f"sentences_{name}.jsonl"
    meta: dict[str, dict] = {}
    n_sent = 0
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for r in recs:
            rows = S0.split_records(r["id"], r["cont_text"], continuation=True)
            for s in rows:
                s["cut_block"] = r.get("block")
                fh.write(json.dumps(s, ensure_ascii=False) + "\n")
            n_sent += len(rows)
            meta[r["id"]] = {"prefix_id": r["prefix_id"], "trace_arm": "shared" if r["condition"] == "cut0" else r["trace_arm"],
                             "cut": r.get("cut"), "prefix_end_s": None if r["condition"] == "cut0" else r["cut"], "m": r.get("block"), "seq": r.get("seq")}
    return path, meta, n_sent


def project_cost(collection_stats: list[dict], prefix_sentences: dict[str, int] | None = None) -> dict:
    """Batch-price projection from the measured rates (registration 4; pipeline Section 8)."""
    total = 0.0
    rows = []
    for c in collection_stats:
        n_docs, n_sent, pre = c["documents"], c["sentences"], c["prefix_sentences"]
        inp = n_sent * RATES["text_per_sentence"] + pre * RATES["text_per_sentence"] * RATES["prefix_code_factor"] + n_docs * 200
        cache = n_docs * RATES["system_prompt_tokens"]
        out = n_sent * (RATES["thinking_per_sentence"] + RATES["label_per_sentence"])
        cost = (inp * S.BATCH_PRICES["sonnet"]["input"] + cache * S.BATCH_PRICES["sonnet"]["cache_read"] + out * S.BATCH_PRICES["sonnet"]["output"]) / 1e6
        rows.append({**c, "input_tokens_est": round(inp), "cache_read_tokens_est": cache, "output_tokens_est": round(out), "cost_est_usd": round(cost, 3)})
        total += cost
    return {"collections": rows, "total_cost_est_usd": round(total, 2), "rates": RATES, "prices": S.BATCH_PRICES["sonnet"]}


def merge_pnext(run_id: str, judge_dirs: dict[str, Path], out_path: Path) -> list[dict]:
    """pnext_<run_id>.csv: one row per cut (trace, m) from the waves' pnext files."""
    rows = []
    meta_of: dict[str, dict] = {}
    for name, d in judge_dirs.items():
        p = d / f"pnext_{name}.csv"
        if p.exists():
            with open(p, encoding="utf-8") as fh:
                rows.extend(csv.DictReader(fh))
        mp = d / "continuation_meta.json"
        if mp.exists():
            for tid, m in json.loads(mp.read_text(encoding="utf-8")).items():
                meta_of[m["prefix_id"]] = m
    out = []
    for r in rows:
        m = meta_of.get(r["prefix_id"], {})
        out.append({"trace_id": "shared" if m.get("trace_arm") == "shared" else m.get("trace_arm", r.get("trace_arm")), "m": "cut0" if m.get("m") is None else m["m"],
                    "prefix_id": r["prefix_id"], "block_end_s": m.get("prefix_end_s"), "last_node_label": r.get("last_node_label"),
                    "n": r["n"], "n_labeled": r["n_labeled"], "n_failed": r["n_failed"], **{f"next_{x}": r[f"next_{x}"] for x in D.L1_ORDER},
                    "opens_block": r["opens_block"], "first_is_wait": r["first_is_wait"]})
    order = {"shared": 0, "c004": 1, "e036": 2}
    out.sort(key=lambda r: (order.get(r["trace_id"], 9), -1 if r["m"] == "cut0" else int(r["m"])))
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=PNEXT_FIELDS)
        w.writeheader()
        w.writerows(out)
    return out


def noise_cuts_from_pcut(pcut: list[dict]) -> dict[str, int]:
    """The C-trace cut with the largest Delta_m (Delta_0 against cut-0) and cut(E-B06)."""
    rows = {(r["trace_id"], r["m"]): r for r in pcut}
    prev = float(rows[("shared", "cut0")]["count_C"]) / float(rows[("shared", "cut0")]["n"]) if ("shared", "cut0") in rows else None
    best, best_m = None, None
    for m in range(46):
        r = rows.get(("c004", str(m)))
        if r is None or not r.get("p_hat"):
            break
        p = float(r["p_hat"])
        if prev is not None:
            d = p - prev
            if best is None or d > best:
                best, best_m = d, m
        prev = p
    return {"c004": best_m, "e036": NOISE_E_CUT}


def first_node_agreement(blocks_a: list[dict], blocks_b: list[dict]) -> dict:
    a = {b["trace_id"]: b["first_new_node"]["L1"] for b in blocks_a}
    b = {x["trace_id"]: x["first_new_node"]["L1"] for x in blocks_b}
    common = sorted(set(a) & set(b))
    agree = sum(1 for t in common if a[t] == b[t])
    return {"n": len(common), "agree": agree, "rate": agree / len(common) if common else float("nan"),
            "confusions": Counter((a[t], b[t]) for t in common if a[t] != b[t]).most_common()}


def _labels_by_trace(path: Path, ids: set[str]) -> dict[str, list[list[str]]]:
    out: dict[str, list[list[str]]] = {}
    for r in read_jsonl(path):
        if r["trace_id"] in ids:
            out.setdefault(r["trace_id"], []).append([S.path_of(l) for l in r["labels"]])
    return out


def write_noise(out_dir: Path, noise: dict) -> None:
    rows = ["# Noise subset (pre-registration 4.2): a second labeling of two cuts' continuations", "",
            "| collection | cut | documents | sentences | Level 1 kappa | Level 1 exact | full-path kappa | first new node agree / n (rate) | cost |", "|---|---|---|---|---|---|---|---|---|"]
    with open(out_dir / "noise_subset.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["collection", "trace_id", "m", "documents", "sentences", "level1_kappa", "level1_exact", "full_path_kappa", "first_node_agree", "first_node_n", "first_node_rate", "cost_usd"])
        for name, c in noise.get("collections", {}).items():
            fa = c["first_node"]
            w.writerow([name, c["cut"]["trace_id"], c["cut"]["m"], c["documents"], c["sentences"], c["level1_kappa"], c["level1_exact"], c["full_path_kappa"], fa["agree"], fa["n"], fa["rate"], c["cost_usd"]])
            rows.append(f"| {name} | {c['cut']['trace_id']} m={c['cut']['m']} | {c['documents']} | {c['sentences']} | {c['level1_kappa']} | {c['level1_exact']} | {c['full_path_kappa']} | {fa['agree']} / {fa['n']} ({fa['rate']:.3f}) | ${c['cost_usd']:.4f} |")
    if noise.get("skipped"):
        rows.append(f"\nSkipped: {noise['skipped']}")
    (out_dir / "noise_subset.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def run(run_dir: Path, out_dir: Path | None = None, dry_run: bool = False, client=None, log=print, noise_cuts: dict[str, int] | None = None,
        no_noise: bool = False, poll_seconds: int = S.BATCH_POLL_SECONDS, max_wait_seconds: int = S.BATCH_MAX_WAIT_SECONDS, sleep=None,
        listing_path: Path | str = D.LISTING, sentences_source: Path | str = S.SENTENCES_SOURCE, wave_size: int = WAVE_SIZE,
        claude_ceiling: float = CLAUDE_CEILING_USD) -> dict:
    sleep = sleep or time.sleep
    run_dir = Path(run_dir)
    out_dir = Path(out_dir) if out_dir else run_dir / f"judge_{datetime.now():%Y-%m-%d_%H%M}"
    out_dir.mkdir(parents=True, exist_ok=True)
    dep_path = run_dir / "DEPARTURES.md"

    def departure(msg: str):
        line = f"- {datetime.now().isoformat(timespec='seconds')} judge: {msg}"
        with open(dep_path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(line + "\n")
        summary["departures"].append(msg)
        log("DEPARTURE " + msg)

    recs, pcut = load_run(run_dir)
    groups = cut_groups(recs)
    waves = waves_of(groups, wave_size)
    summary = {"run_dir": str(run_dir), "out_dir": str(out_dir), "dry_run": dry_run, "wave_size": wave_size, "claude_ceiling_usd": claude_ceiling,
               "order": [g for g, _ in groups], "waves": [], "cost_usd": 0.0, "noise": None, "departures": [], "unlabeled_cuts": [], "stopped": None}
    src = S.load_sentences(Path(sentences_source))

    def wave_stats(k: int, wave: list[tuple[str, list[dict]]]) -> tuple[str, list[dict], dict, dict]:
        name = f"continuations_w{k:02d}"
        rs = [r for _, rs_ in wave for r in rs_]
        path, meta, n_sent = split_collection(name, rs, out_dir)
        pre = 0
        for m in meta.values():
            if m["prefix_end_s"] is not None:
                pre += sum(1 for r in src[m["trace_arm"]] if r["s"] <= m["prefix_end_s"])
        stats = {"collection": name, "wave": k, "cuts": [g for g, _ in wave], "documents": len(rs), "sentences": n_sent, "prefix_sentences": pre}
        return name, rs, meta, stats

    # ---- projection of every wave (dry run stops here) --------------------------------------------
    all_stats = []
    prepared = []
    for k, wave in enumerate(waves):
        name, rs, meta, stats = wave_stats(k, wave)
        proj = project_cost([stats])
        stats["cost_est_usd"] = proj["total_cost_est_usd"]
        all_stats.append(stats)
        prepared.append((k, wave, name, rs, meta, stats))
    summary["projection"] = {"waves": all_stats, "total_cost_est_usd": round(sum(s["cost_est_usd"] for s in all_stats), 2), "rates": RATES, "safety": SAFETY,
                             "prices": S.BATCH_PRICES["sonnet"]}
    (out_dir / "projection.json").write_text(json.dumps(summary["projection"], indent=2) + "\n", encoding="utf-8")
    log(f"{len(recs)} continuations in {len(groups)} cut groups, {len(waves)} waves of {wave_size}; projected judge cost ${summary['projection']['total_cost_est_usd']:.2f} at batch prices (ceiling ${claude_ceiling:.0f})")
    if dry_run:
        for k, wave, name, rs, meta, stats in prepared:
            S.run_judge(out_dir / f"sentences_{name}.jsonl", out_dir / name, dry_run=True, log=lambda s: None, model_key="sonnet", prompt_version="v3",
                        thinking_mode="low", mode="batch", collection=name, continuation_meta=meta, listing_path=listing_path,
                        sentences_source=sentences_source, archived_meta_path=None)
        return summary

    # ---- the waves, in order, under the ceiling ---------------------------------------------------
    if client is None:
        client = S.make_client()
    judge_dirs: dict[str, Path] = {}
    labeled_groups: list[str] = []
    for k, wave, name, rs, meta, stats in prepared:
        d = out_dir / name
        done_marker = d / "s3_wave_done.json"
        if done_marker.exists():
            prior = json.loads(done_marker.read_text(encoding="utf-8"))
            summary["cost_usd"] += prior["cost_usd"]
            summary["waves"].append(prior)
            judge_dirs[name] = d
            labeled_groups += stats["cuts"]
            log(f"{name}: already done (${prior['cost_usd']:.2f}), skipped")
            continue
        projected = stats["cost_est_usd"] * SAFETY
        if summary["cost_usd"] + projected > claude_ceiling:
            remaining = [g for _, w2, *_ in prepared[k:] for g in [x for x, _ in w2]]
            summary["unlabeled_cuts"] = remaining
            summary["stopped"] = f"Claude ceiling: ${summary['cost_usd']:.2f} spent + ${projected:.2f} projected for wave {k} > ${claude_ceiling:.0f}"
            departure(f"Claude ceiling ${claude_ceiling:.0f} would be exceeded by wave {k} (${summary['cost_usd']:.2f} spent, ${projected:.2f} projected with safety {SAFETY}); "
                      f"labeling stopped; unlabeled cuts (latest blocks by the registered order): {', '.join(remaining)}")
            break
        log(f"wave {k}: cuts {stats['cuts']}, {stats['documents']} documents, {stats['sentences']} sentences, projected ${stats['cost_est_usd']:.2f}")
        s = S.run_judge(out_dir / f"sentences_{name}.jsonl", d, client=client, log=log, model_key="sonnet", prompt_version="v3", thinking_mode="low",
                        mode="batch", collection=name, continuation_meta=meta, listing_path=listing_path, sentences_source=sentences_source,
                        archived_meta_path=None, poll_seconds=poll_seconds, max_wait_seconds=max_wait_seconds, sleep=sleep)
        wave_rec = {"wave": k, "collection": name, "cuts": stats["cuts"], "documents": stats["documents"], "sentences": stats["sentences"],
                    "valid": s.get("n_valid"), "failed_after_follow_up": len(s.get("failures") or {}), "batches": s.get("batches"),
                    "cost_usd": s["total_cost_usd"], "usage": s.get("usage"), "thinking_tokens_per_labeled_sentence": s.get("thinking_tokens_per_labeled_sentence"),
                    "stopped": s["stopped"], "retry": None}
        summary["cost_usd"] += s["total_cost_usd"]
        if s["stopped"]:
            summary["stopped"] = f"{name}: {s['stopped']}"
            summary["waves"].append(wave_rec)
            departure(f"wave {k} stopped: {s['stopped']}")
            break
        if s.get("failures"):
            r = S.retry_failed(d, client=client, log=log, poll_seconds=poll_seconds, max_wait_seconds=max_wait_seconds, sleep=sleep)
            wave_rec["retry"] = {"parsed": r["parsed"], "failed": [f["trace_id"] for f in r["failed"]], "cost_usd": r["cost_usd"], "batches": r["batches"]}
            summary["cost_usd"] += r["cost_usd"]
            if r["failed"]:
                departure(f"wave {k}: {len(r['failed'])} continuations unlabeled after three attempts: {', '.join(f['trace_id'] for f in r['failed'])}")
        done_marker.write_text(json.dumps({**wave_rec, "cost_usd": wave_rec["cost_usd"] + (wave_rec["retry"] or {}).get("cost_usd", 0.0)}, indent=1, default=str) + "\n", encoding="utf-8")
        wave_rec["cost_usd"] += (wave_rec["retry"] or {}).get("cost_usd", 0.0)
        summary["waves"].append(wave_rec)
        judge_dirs[name] = d
        labeled_groups += stats["cuts"]
        log(f"wave {k} done: valid {wave_rec['valid']} of {stats['documents']}, cost ${wave_rec['cost_usd']:.2f}, cumulative ${summary['cost_usd']:.2f}")
    with open(out_dir / "unlabeled_cuts.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["cut_group", "reason"])
        for g in summary["unlabeled_cuts"]:
            w.writerow([g, "Claude ceiling (v2, 8.1)"])
    pn = merge_pnext(run_dir.name, judge_dirs, out_dir / f"pnext_{run_dir.name}.csv")
    summary["pnext_rows"] = len(pn)
    summary["labeled_cut_groups"] = labeled_groups

    # ---- the noise subset (registration 4.2), inside the same ceiling ------------------------------
    if not no_noise and judge_dirs:
        cuts = noise_cuts or noise_cuts_from_pcut(pcut)
        summary["noise"] = {"cuts": cuts, "collections": {}, "skipped": None}
        blocks_by_id: dict[str, tuple[dict, Path]] = {}
        for name, d in judge_dirs.items():
            for b in read_jsonl(d / f"blocks_{name}_judge.jsonl"):
                blocks_by_id[b["trace_id"]] = (b, d)
        for tid, m in cuts.items():
            if m is None or f"{tid}_B{m:02d}" not in labeled_groups:
                summary["noise"]["skipped"] = (summary["noise"]["skipped"] or "") + f"{tid} m={m} not labeled; "
                continue
            subset = [r for r in recs if r["condition"] == "cut" and r["trace_arm"] == tid and r.get("block") == m]
            nname = f"noise_{tid}_B{m:02d}"
            path, meta, n_sent = split_collection(nname, subset, out_dir)
            proj = project_cost([{"collection": nname, "documents": len(subset), "sentences": n_sent, "prefix_sentences": 0}])["total_cost_est_usd"] * SAFETY
            if summary["cost_usd"] + proj > claude_ceiling:
                departure(f"noise subset {nname} skipped: ${summary['cost_usd']:.2f} spent + ${proj:.2f} projected > ceiling ${claude_ceiling:.0f}")
                summary["noise"]["skipped"] = (summary["noise"]["skipped"] or "") + f"{nname} (ceiling); "
                continue
            d = out_dir / nname
            s = S.run_judge(path, d, client=client, log=log, model_key="sonnet", prompt_version="v3", thinking_mode="low", mode="batch", collection=nname,
                            continuation_meta=meta, listing_path=listing_path, sentences_source=sentences_source, archived_meta_path=None,
                            poll_seconds=poll_seconds, max_wait_seconds=max_wait_seconds, sleep=sleep)
            cost = s["total_cost_usd"]
            if s.get("failures"):
                r = S.retry_failed(d, client=client, log=log, poll_seconds=poll_seconds, max_wait_seconds=max_wait_seconds, sleep=sleep)
                cost += r["cost_usd"]
            summary["cost_usd"] += cost
            second = [b for b in read_jsonl(d / f"blocks_{nname}_judge.jsonl") if b["trace_id"] in blocks_by_id]
            first = [blocks_by_id[b["trace_id"]][0] for b in second]
            fa = first_node_agreement(first, second)
            ids = {b["trace_id"] for b in second}
            labels1: dict[str, list[list[str]]] = {}
            for wname in {blocks_by_id[t][1].name for t in ids}:
                labels1.update(_labels_by_trace(out_dir / wname / f"labels_{wname}_judge.jsonl", ids))
            labels2 = _labels_by_trace(d / f"labels_{nname}_judge.jsonl", ids)
            j1 = S.load_sentences(path)
            common = [t for t in labels2 if t in labels1 and len(labels1[t]) == len(labels2[t])]
            agr = S.agreement({t: labels2[t] for t in common}, {t: labels1[t] for t in common}, {t: [r["text"] for r in j1[t]] for t in common}) if common else None
            summary["noise"]["collections"][nname] = {"cut": {"trace_id": tid, "m": m}, "documents": len(subset), "cost_usd": cost,
                                                     "first_node": fa, "level1_kappa": agr["levels"][0]["kappa"] if agr else None,
                                                     "level1_exact": agr["levels"][0]["exact_match"] if agr else None,
                                                     "full_path_kappa": agr["levels"][2]["kappa"] if agr else None, "sentences": agr["n"] if agr else 0,
                                                     "batches": s.get("batches")}
        write_noise(out_dir, summary["noise"])
    (out_dir / "s3_summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
    log(f"judge done: ${summary['cost_usd']:.2f} of the ${claude_ceiling:.0f} ceiling; {len(labeled_groups)} of {len(groups)} cut groups labeled")
    return summary


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Pipeline step (8/9): the judge on the continuations of a resampling run.")
    ap.add_argument("--run", required=True, help="the resampling run folder (continuations.jsonl, pcut.csv)")
    ap.add_argument("--out", help="judge folder (default <run>/judge_<stamp>/; re-running on an existing folder skips the finished waves)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--wave-size", type=int, default=WAVE_SIZE)
    ap.add_argument("--claude-ceiling", type=float, default=CLAUDE_CEILING_USD)
    ap.add_argument("--noise-cuts", help="override, e.g. c004:9,e036:6")
    ap.add_argument("--no-noise", action="store_true")
    ap.add_argument("--poll-seconds", type=int, default=S.BATCH_POLL_SECONDS)
    args = ap.parse_args(argv)
    noise = None
    if args.noise_cuts:
        noise = {kv.split(":")[0]: int(kv.split(":")[1]) for kv in args.noise_cuts.split(",")}
    s = run(Path(args.run), Path(args.out) if args.out else None, dry_run=args.dry_run, noise_cuts=noise, no_noise=args.no_noise, poll_seconds=args.poll_seconds,
            wave_size=args.wave_size, claude_ceiling=args.claude_ceiling)
    print(json.dumps({k: v for k, v in s.items() if k != "projection"}, indent=2, default=str))
    return 0 if not s.get("stopped") else 1


if __name__ == "__main__":
    sys.exit(main())
