#!/usr/bin/env python3
"""s3_judge_continuations.py -- pipeline v2 step (8/9): the judge on the continuations of a
resampling run (pre-registration Section 4).

  python scripts/s3_judge_continuations.py --run runs/experiments/resample_blocks_<stamp>/ [--dry-run]
      [--out <run>/judge_<stamp>/] [--noise-cuts c004:9,e036:6] [--no-noise] [--poll-seconds 60]

Steps: (1) every continuation of the run's cut conditions (cut-0 and the block-end cuts; the
no-think baseline has no thinking part) is split with s0_split (thinking part only, decision
19) into sentences_<collection>.jsonl, one collection per trace arm (continuations_cut0,
continuations_c004, continuations_e036); (2) each collection is judged with s1_judge in batch mode -- prompt v3, Sonnet 5,
adaptive thinking low, the prefix shown with its reviewed labels (listing v4; for cut(B_m) the
sentences 0 ... block-end index), one follow-up batch for failures, then the formatted third
attempt (--retry-failed) -- and derived with R1-R4; (3) the pnext rows of all collections are
merged into pnext_<run_id>.csv keyed by trace and m; (4) the noise subset of registration 4.2:
the continuations of the C-trace cut with the largest Delta_m (from pcut.csv) and of cut(E-B06)
are labeled a second time and the two labelings' agreement (Level 1 kappa over sentences,
first-new-node agreement) is written to noise_subset.csv / .md.
--dry-run builds the documents and projects the cost from the measured rates (34 thinking + 7
label tokens per sentence, 23.9 text tokens per sentence, batch prices) without any call.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import derivation as D  # noqa: E402
import s0_split as S0  # noqa: E402
import s1_judge as S  # noqa: E402
import transitions as T  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
RATES = {"thinking_per_sentence": 34.0, "label_per_sentence": 7.0, "text_per_sentence": 23.9, "prefix_code_factor": 1.6,
         "system_prompt_tokens": 5820}
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


def collections_of(recs: list[dict]) -> dict[str, list[dict]]:
    """{collection: records}: continuations_cut0 for the empty prefix, continuations_<trace> for the block-end cuts."""
    out: dict[str, list[dict]] = {}
    for r in recs:
        name = "continuations_cut0" if r["condition"] == "cut0" else f"continuations_{r['trace_arm']}"
        out.setdefault(name, []).append(r)
    return out


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


def project_cost(collection_stats: list[dict], prefix_sentences: dict[str, int]) -> dict:
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
    """pnext_<run_id>.csv: one row per cut (trace, m) from the collections' pnext files."""
    rows = []
    for name, d in judge_dirs.items():
        p = d / f"pnext_{name}.csv"
        if not p.exists():
            continue
        with open(p, encoding="utf-8") as fh:
            rows.extend(csv.DictReader(fh))
    # attach trace/m/block_end_s from the continuation meta of each judge folder
    meta_of: dict[str, dict] = {}
    for name, d in judge_dirs.items():
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


def run(run_dir: Path, out_dir: Path | None = None, dry_run: bool = False, client=None, log=print, noise_cuts: dict[str, int] | None = None,
        no_noise: bool = False, poll_seconds: int = S.BATCH_POLL_SECONDS, max_wait_seconds: int = S.BATCH_MAX_WAIT_SECONDS, sleep=None,
        listing_path: Path | str = D.LISTING, sentences_source: Path | str = S.SENTENCES_SOURCE) -> dict:
    import time
    sleep = sleep or time.sleep
    run_dir = Path(run_dir)
    out_dir = Path(out_dir) if out_dir else run_dir / f"judge_{datetime.now():%Y-%m-%d_%H%M}"
    out_dir.mkdir(parents=True, exist_ok=True)
    recs, pcut = load_run(run_dir)
    colls = collections_of(recs)
    summary = {"run_dir": str(run_dir), "out_dir": str(out_dir), "collections": {}, "dry_run": dry_run, "cost_usd": 0.0, "noise": None}
    stats = []
    metas: dict[str, dict] = {}
    src = S.load_sentences(Path(sentences_source))
    for name, rs in colls.items():
        path, meta, n_sent = split_collection(name, rs, out_dir)
        metas[name] = meta
        pre = 0
        for m in meta.values():
            if m["prefix_end_s"] is not None:
                pre += sum(1 for r in src[m["trace_arm"]] if r["s"] <= m["prefix_end_s"])
        stats.append({"collection": name, "documents": len(rs), "sentences": n_sent, "prefix_sentences": pre})
        summary["collections"][name] = {"sentences_path": str(path), "documents": len(rs), "sentences": n_sent, "prefix_sentences": pre}
    summary["projection"] = project_cost(stats, {})
    (out_dir / "projection.json").write_text(json.dumps(summary["projection"], indent=2) + "\n", encoding="utf-8")
    log(f"{len(recs)} continuations in {len(colls)} collections; projected judge cost ${summary['projection']['total_cost_est_usd']:.2f} at batch prices")
    if dry_run:
        for name in colls:
            S.run_judge(out_dir / f"sentences_{name}.jsonl", out_dir / name, dry_run=True, log=lambda s: None, model_key="sonnet",
                        prompt_version="v3", thinking_mode="low", mode="batch", collection=name, continuation_meta=metas[name],
                        listing_path=listing_path, sentences_source=sentences_source, archived_meta_path=None)
        return summary
    if client is None:
        client = S.make_client()
    judge_dirs: dict[str, Path] = {}
    for name in colls:
        d = out_dir / name
        s = S.run_judge(out_dir / f"sentences_{name}.jsonl", d, client=client, log=log, model_key="sonnet", prompt_version="v3", thinking_mode="low",
                        mode="batch", collection=name, continuation_meta=metas[name], listing_path=listing_path, sentences_source=sentences_source,
                        archived_meta_path=None, poll_seconds=poll_seconds, max_wait_seconds=max_wait_seconds, sleep=sleep)
        summary["collections"][name].update({"valid": s.get("n_valid"), "failed": len(s.get("failures") or {}), "cost_usd": s["total_cost_usd"], "stopped": s["stopped"]})
        summary["cost_usd"] += s["total_cost_usd"]
        if s["stopped"]:
            summary["stopped"] = f"{name}: {s['stopped']}"
            return summary
        if s.get("failures"):
            r = S.retry_failed(d, client=client, log=log, poll_seconds=poll_seconds, max_wait_seconds=max_wait_seconds, sleep=sleep)
            summary["collections"][name].update({"retry_parsed": r["parsed"], "retry_failed": [f["trace_id"] for f in r["failed"]], "retry_cost_usd": r["cost_usd"]})
            summary["cost_usd"] += r["cost_usd"]
        judge_dirs[name] = d
    pn = merge_pnext(run_dir.name, judge_dirs, out_dir / f"pnext_{run_dir.name}.csv")
    summary["pnext_rows"] = len(pn)
    if not no_noise:
        cuts = noise_cuts or noise_cuts_from_pcut(pcut)
        summary["noise"] = {"cuts": cuts, "collections": {}}
        for tid, m in cuts.items():
            name = f"continuations_{tid}"
            if m is None or name not in colls:
                continue
            subset = [r for r in colls[name] if r.get("block") == m]
            if not subset:
                continue
            nname = f"noise_{tid}_B{m:02d}"
            path, meta, n_sent = split_collection(nname, subset, out_dir)
            d = out_dir / nname
            s = S.run_judge(path, d, client=client, log=log, model_key="sonnet", prompt_version="v3", thinking_mode="low", mode="batch", collection=nname,
                            continuation_meta=meta, listing_path=listing_path, sentences_source=sentences_source, archived_meta_path=None,
                            poll_seconds=poll_seconds, max_wait_seconds=max_wait_seconds, sleep=sleep)
            summary["cost_usd"] += s["total_cost_usd"]
            if s.get("failures"):
                r = S.retry_failed(d, client=client, log=log, poll_seconds=poll_seconds, max_wait_seconds=max_wait_seconds, sleep=sleep)
                summary["cost_usd"] += r["cost_usd"]
            first = {b["trace_id"]: b for b in read_jsonl(judge_dirs[name] / f"blocks_{name}_judge.jsonl")}
            second = [b for b in read_jsonl(d / f"blocks_{nname}_judge.jsonl") if b["trace_id"] in first]
            fa = first_node_agreement([first[b["trace_id"]] for b in second], second)
            j1 = S.load_sentences(path)  # the continuation sentences by id (texts for the residue)
            labels1 = _labels_by_trace(judge_dirs[name] / f"labels_{name}_judge.jsonl", set(j1))
            labels2 = _labels_by_trace(d / f"labels_{nname}_judge.jsonl", set(j1))
            common = [t for t in labels2 if t in labels1 and len(labels1[t]) == len(labels2[t])]
            agr = S.agreement({t: labels2[t] for t in common}, {t: labels1[t] for t in common}, {t: [r["text"] for r in j1[t]] for t in common}) if common else None
            summary["noise"]["collections"][nname] = {"cut": {"trace_id": tid, "m": m}, "documents": len(subset), "cost_usd": s["total_cost_usd"],
                                                     "first_node": fa, "level1_kappa": agr["levels"][0]["kappa"] if agr else None,
                                                     "level1_exact": agr["levels"][0]["exact_match"] if agr else None,
                                                     "full_path_kappa": agr["levels"][2]["kappa"] if agr else None, "sentences": agr["n"] if agr else 0}
        write_noise(out_dir, summary["noise"])
    (out_dir / "s3_summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
    return summary


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
    (out_dir / "noise_subset.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Pipeline step (8/9): the judge on the continuations of a resampling run.")
    ap.add_argument("--run", required=True, help="the resampling run folder (continuations.jsonl, pcut.csv)")
    ap.add_argument("--out", help="judge folder (default <run>/judge_<stamp>/)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--noise-cuts", help="override, e.g. c004:9,e036:6")
    ap.add_argument("--no-noise", action="store_true")
    ap.add_argument("--poll-seconds", type=int, default=S.BATCH_POLL_SECONDS)
    args = ap.parse_args(argv)
    noise = None
    if args.noise_cuts:
        noise = {kv.split(":")[0]: int(kv.split(":")[1]) for kv in args.noise_cuts.split(",")}
    s = run(Path(args.run), Path(args.out) if args.out else None, dry_run=args.dry_run, noise_cuts=noise, no_noise=args.no_noise, poll_seconds=args.poll_seconds)
    print(json.dumps(s, indent=2, default=str))
    return 0 if not s.get("stopped") else 1


if __name__ == "__main__":
    sys.exit(main())
