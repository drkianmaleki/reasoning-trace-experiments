#!/usr/bin/env python3
"""s4_analyze.py -- pipeline v2 step (9/9): the analysis of a stage-one run, implementing
pre-registration 2026-09-17 v1 Sections 5 (mediation tree, Q1) and 6 (transition tree, Q2, Q3)
exactly.  Offline: numpy for the resampling loops, matplotlib for the plots.

  python scripts/s4_analyze.py --run runs/experiments/resample_blocks_<stamp>/ --judge <run>/judge_<stamp>/
      [--out <run>/analysis/] [--pcorpus runs/experiments/judge_sweep44_2026-09-17_1334/pcorpus_L1.csv]
      [--draws 10000] [--perms 10000] [--seed 0]

Inputs: the run's pcut.csv and continuations.jsonl (answers per continuation); the judge folder's
blocks_<collection>_judge.jsonl files (first new node per continuation, block opening, R4 first
sentence; a folder noise_<trace>_B<m> per relabeled cut); P_corpus (pcorpus_L1.csv, row-normalized
here); the reviewed labels of listing v4 with the sentence texts for X_m, the prefix node
sequences (history forms) and the source's own next label after every cut.

Outputs in --out: mediation_pcut.csv, mediation_delta.csv, mediation_summary.csv,
transition_pnext.csv, transition_permutation.csv, transition_tv_corpus.csv,
transition_psource.csv, transition_history.csv, transition_order.csv, transition_noise.csv,
stage1_summary.md (wording rule 5.5: describe, no verdicts), and the plots
figures/<run_id>_<trace>_phat.png and _delta.png (Section 5.4).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import derivation as D  # noqa: E402
import stats_utils as ST  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
FIGURES = REPO / "figures"
PCORPUS_DEFAULT = REPO / "runs" / "experiments" / "judge_sweep44_2026-09-17_1334" / "pcorpus_L1.csv"
L1 = D.L1_ORDER
LETTERS = "ABCDEF"
A_T = {"c004": "C", "e036": "E"}
TK_TRACE = {"c004": 4740, "e036": 2890}
MIN_CUTS_HISTORY = 3


def read_jsonl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def read_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    if fields is None:  # the union of the rows' keys, in first-seen order (baseline rows lack the cut columns)
        fields = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) and not math.isnan(v) else ("" if (isinstance(v, float) and math.isnan(v)) or v is None else v)) for k, v in r.items()})


def fmt(x, nd=3) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


# ----------------------------------------------------------------------------
# Loading the run
# ----------------------------------------------------------------------------

def load_pcorpus(path: Path) -> dict[str, dict[str, float]]:
    """Row-normalized P_corpus from the counts file (or a _rownorm file)."""
    rows = read_csv(path)
    out = {}
    for r in rows:
        x = r.get("X_current_node")
        if any(k.startswith("Y_") for k in r):
            counts = {y: float(r[f"Y_{y}"]) for y in L1}
            tot = sum(counts.values())
            out[x] = {y: (counts[y] / tot if tot else float("nan")) for y in L1}
        else:
            out[x] = {y: float(r[f"P_next_{y}"]) for y in L1}
    return out


def reviewed_context(listing_path: Path | str = D.LISTING, sentences_source: Path | str = D.SENTENCES_SOURCE) -> dict:
    listing = D.parse_listing(listing_path)
    texts = D.load_sentence_texts(sentences_source)
    out = {}
    for tid in ("c004", "e036"):
        der = D.derive(listing[tid]["labels"], tid, "reviewed_v4", texts[tid])
        out[tid] = {"labels": listing[tid]["labels"], "texts": texts[tid], "derived": der,
                    "openers": {b["s_start"]: b["opener_rule"] for b in der["blocks"]}}
    return out


def cut_context(ctx: dict, tid: str, e: int) -> dict:
    """For a cut after sentence e: the prefix node sequence (Level 1, reviewed labels, prefix
    derivation), X = the last node's label, the source's own next label and whether it opens a
    block (the node containing sentence e+1 in the full-trace derivation)."""
    c = ctx[tid]
    pre = D.derive(c["labels"][: e + 1], tid, "reviewed_v4", c["texts"][: e + 1])
    seq = [D.node_level1(n) for n in pre["nodes"]]
    full = c["derived"]
    nxt = next((n for n in full["nodes"] if n["s_start"] <= e + 1 <= n["s_end"]), None) if e + 1 < len(c["labels"]) else None
    return {"prefix_nodes": seq, "X": seq[-1] if seq else None, "Y_source": D.node_level1(nxt) if nxt else None,
            "source_opens": (e + 1) in c["openers"] if nxt else None, "source_open_rule": c["openers"].get(e + 1)}


def load_run(run_dir: Path, judge_dir: Path | None, ctx: dict) -> dict:
    """{trace: {"cut0": cut, "nothink": cut, "cuts": [cut, ...]}} with answers, labels and context."""
    pcut = read_csv(run_dir / "pcut.csv")
    conts = read_jsonl(run_dir / "continuations.jsonl")
    answers: dict[str, list[str]] = defaultdict(list)
    for r in conts:
        answers[r["prefix_id"]].append(r.get("answer") or ("?" if len(r.get("letters") or []) != 1 else r["letters"][0]))
    judged: dict[str, list[dict]] = defaultdict(list)
    noise: dict[str, list[dict]] = defaultdict(list)
    judge_meta = {}
    if judge_dir is not None:
        for p in sorted(Path(judge_dir).rglob("blocks_*_judge.jsonl")):
            target = noise if p.parent.name.startswith("noise_") else judged
            for b in read_jsonl(p):
                if "first_new_node" in b:
                    target[b["prefix_id"]].append({"id": b["trace_id"], "L1": b["first_new_node"]["L1"], "opens": bool(b["first_new_node"]["opens_block"]),
                                                   "wait": bool(b.get("first_sentence_r4")), "rule": b["first_new_node"].get("opener_rule")})
        cfg = next(iter(sorted(Path(judge_dir).rglob("config.json"))), None)
        if cfg:
            c = json.loads(cfg.read_text(encoding="utf-8"))
            judge_meta = {"model": c.get("model"), "prompt": c.get("prompt"), "prompt_sha256": c.get("prompt_sha256"), "thinking_mode": c.get("thinking_mode")}
        ns = Path(judge_dir) / "noise_subset.csv"
        if ns.exists():
            judge_meta["noise_subset"] = read_csv(ns)
    run = {"c004": {"cuts": []}, "e036": {"cuts": []}, "shared": {}, "judge_meta": judge_meta, "run_id": run_dir.name}
    for r in pcut:
        cut = {"trace_id": r["trace_id"], "condition": r.get("condition") or ("cut" if r["m"] not in ("nothink", "cut0") else r["m"]),
               "m": r["m"] if r["m"] in ("nothink", "cut0") else int(r["m"]), "prefix_id": r["prefix_id"],
               "block_end_s": int(r["block_end_s"]) if r.get("block_end_s") else None, "n": int(r["n"]),
               "counts": {L: int(r.get(f"count_{L}") or 0) for L in LETTERS}, "unresolved": int(r.get("count_unresolved") or 0),
               "tk": int(r["tk_block"]) if r.get("tk_block") else None, "prompt_tokens": int(r["prompt_tokens"]) if r.get("prompt_tokens") else None,
               "answers": answers.get(r["prefix_id"], []), "judged": judged.get(r["prefix_id"], []), "noise": noise.get(r["prefix_id"], [])}
        if cut["condition"] == "cut":
            cut.update(cut_context(ctx, cut["trace_id"], cut["block_end_s"]))
            run[cut["trace_id"]]["cuts"].append(cut)
        else:
            cut.update({"prefix_nodes": [], "X": None, "Y_source": None, "source_opens": None})
            run["shared"][cut["condition"]] = cut
    for tid in ("c004", "e036"):
        run[tid]["cuts"].sort(key=lambda c: c["m"])
        run[tid]["a_T"] = A_T[tid]
        run[tid]["tk_trace"] = TK_TRACE[tid]
    return run


# ----------------------------------------------------------------------------
# Section 5: the mediation tree
# ----------------------------------------------------------------------------

def phat(cut: dict, letter: str) -> tuple[float, tuple[float, float]]:
    k = cut["counts"].get(letter, 0)
    n = cut["n"]
    return (k / n if n else float("nan")), ST.wilson(k, n)


def mediation(run: dict, draws: int, seed: int) -> dict:
    out = {"pcut": [], "delta": [], "summary": []}
    shared = run["shared"]
    for name in ("nothink", "cut0"):
        c = shared.get(name)
        if c:
            row = {"trace_id": "shared", "m": name, "prefix_id": c["prefix_id"], "n": c["n"], **{f"count_{L}": c["counts"][L] for L in LETTERS},
                   "count_unresolved": c["unresolved"]}
            for L in ("C", "E"):
                p, (lo, hi) = phat(c, L)
                row.update({f"p_{L}": p, f"p_{L}_low": lo, f"p_{L}_high": hi})
            out["pcut"].append(row)
    for tid in ("c004", "e036"):
        t = run[tid]
        a_t = t["a_T"]
        cuts = t["cuts"]
        if not cuts:
            continue
        cut0 = shared.get("cut0")
        prev_p, prev_k, prev_n = (phat(cut0, a_t)[0], cut0["counts"][a_t], cut0["n"]) if cut0 else (float("nan"), 0, 0)
        deltas = []
        for c in cuts:
            p, (lo, hi) = phat(c, a_t)
            row = {"trace_id": tid, "m": c["m"], "prefix_id": c["prefix_id"], "block_end_s": c["block_end_s"], "n": c["n"],
                   **{f"count_{L}": c["counts"][L] for L in LETTERS}, "count_unresolved": c["unresolved"], "p_aT": p, "p_aT_low": lo, "p_aT_high": hi}
            for L in ("C", "E"):
                pl, (l, h) = phat(c, L)
                row.update({f"p_{L}": pl, f"p_{L}_low": l, f"p_{L}_high": h})
            out["pcut"].append(row)
            k, n = c["counts"][a_t], c["n"]
            d = p - prev_p
            nlo, nhi = ST.newcombe(k, n, prev_k, prev_n) if prev_n else (float("nan"), float("nan"))
            deltas.append(d)
            out["delta"].append({"trace_id": tid, "m": c["m"], "prefix_id": c["prefix_id"], "block_end_s": c["block_end_s"], "p_aT": p, "p_prev": prev_p,
                                 "delta": d, "delta_low": nlo, "delta_high": nhi, "tk_block": c["tk"], "trivial": d == 0.0})
            prev_p, prev_k, prev_n = p, k, n
        boot = ST.bootstrap_gap(cut0["answers"] if cut0 else [], [c["answers"] for c in cuts], a_t, draws=draws, seed=seed)
        top = int(np.argmax(deltas))
        p_cut0 = phat(cut0, a_t)[0] if cut0 else float("nan")
        total = phat(cuts[-1], a_t)[0] - p_cut0
        ranked = sorted(deltas, reverse=True)
        shares = {k: (sum(ranked[:k]) / total if total > 0 else float("nan")) for k in (1, 2, 3)}
        to_half = None
        if total > 0:
            cum = 0.0
            for i, d in enumerate(ranked, start=1):
                cum += d
                if cum >= total / 2:
                    to_half = i
                    break
        tk_top = cuts[top]["tk"]
        out["summary"].append({"trace_id": tid, "a_T": a_t, "cuts_sampled": len(cuts), "M": cuts[-1]["m"], "p_cut0": p_cut0, "p_M": phat(cuts[-1], a_t)[0],
                               "total_movement": total, "B_top": top, "delta_top": deltas[top], "tk_B_top": tk_top, "tk_trace": t["tk_trace"],
                               "tk_B_top_share": (tk_top / t["tk_trace"]) if tk_top is not None else float("nan"),
                               "gap": boot["gap"], "gap_low": boot["ci_low"], "gap_high": boot["ci_high"], "gap_draws": draws, "seed": seed,
                               "share_top1": shares[1], "share_top2": shares[2], "share_top3": shares[3], "blocks_to_half": to_half,
                               "trivial_blocks": sum(1 for d in deltas if d == 0.0)})
    return out


def plot_trace(run: dict, tid: str, med: dict, out_dir: Path) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t = run[tid]
    if not t["cuts"]:
        return []
    a_t = t["a_T"]
    rows = [r for r in med["pcut"] if r["trace_id"] == tid]
    drows = [r for r in med["delta"] if r["trace_id"] == tid]
    ms = [r["m"] for r in rows]
    p = np.array([r["p_aT"] for r in rows])
    lo = np.array([r["p_aT_low"] for r in rows])
    hi = np.array([r["p_aT_high"] for r in rows])
    FIGURES.mkdir(exist_ok=True)
    paths = []
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.errorbar(ms, p, yerr=[p - lo, hi - p], fmt="o-", color="#1f4e79", ecolor="#9db7d5", capsize=2, label=f"P̂(answer = {a_t} | cut(B_m)), Wilson 95%")
    triv = [r["m"] for r in drows if r["trivial"]]
    if triv:
        ax.plot(triv, [p[ms.index(m)] for m in triv], "o", mfc="white", mec="#1f4e79", label="trivial block (Δ̂ = 0)")
    for name, style in (("nothink", "--"), ("cut0", ":")):
        c = run["shared"].get(name)
        if c:
            ax.axhline(phat(c, a_t)[0], linestyle=style, color="#777777", label=f"{name}: P̂({a_t}) = {phat(c, a_t)[0]:.2f}")
    ax.set_xlabel("block m (cut after B_m)")
    ax.set_ylabel(f"P̂(answer = {a_t})")
    ax.set_ylim(-0.02, 1.02)
    ax.set_title(f"{run['run_id']} — {tid}: P̂_m against m")
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    path = FIGURES / f"{run['run_id']}_{tid}_phat.png"
    fig.savefig(path, dpi=130)
    plt.close(fig)
    paths.append(path)
    fig, ax = plt.subplots(figsize=(9, 4))
    d = np.array([r["delta"] for r in drows])
    dlo = np.array([r["delta_low"] for r in drows])
    dhi = np.array([r["delta_high"] for r in drows])
    ax.axhline(0, color="#777777", linewidth=0.8)
    ax.errorbar(ms, d, yerr=[np.nan_to_num(d - dlo), np.nan_to_num(dhi - d)], fmt="s-", color="#7a2e2e", ecolor="#d9a5a5", capsize=2, label="Δ_m = P̂_m − P̂_{m−1}, Newcombe 95%")
    if triv:
        ax.plot(triv, [0] * len(triv), "s", mfc="white", mec="#7a2e2e", label="trivial block (Δ̂ = 0)")
    ax.set_xlabel("block m")
    ax.set_ylabel("Δ_m")
    ax.set_title(f"{run['run_id']} — {tid}: Δ_m against m")
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    path = FIGURES / f"{run['run_id']}_{tid}_delta.png"
    fig.savefig(path, dpi=130)
    plt.close(fig)
    paths.append(path)
    return paths


# ----------------------------------------------------------------------------
# Section 6: the transition tree
# ----------------------------------------------------------------------------

def cut_labels(cut: dict, second: bool = False) -> list[str]:
    return [j["L1"] for j in (cut["noise"] if second else cut["judged"])]


def pnext_rows(run: dict, pcorpus: dict, pooled_by_x: dict[str, dict[str, float]], draws: int, seed: int) -> list[dict]:
    rows = []
    for tid in ("c004", "e036"):
        for c in run[tid]["cuts"]:
            labels = cut_labels(c)
            dist = ST.distribution(labels, L1)
            row = {"trace_id": tid, "m": c["m"], "prefix_id": c["prefix_id"], "block_end_s": c["block_end_s"], "X": c["X"], "n": c["n"],
                   "n_labeled": len(labels), **{f"p_{y}": dist[y] for y in L1},
                   "opens_block_frac": (sum(j["opens"] for j in c["judged"]) / len(labels)) if labels else float("nan"),
                   "wait_frac": (sum(j["wait"] for j in c["judged"]) / len(labels)) if labels else float("nan"),
                   "Y_source": c["Y_source"], "p_Y_source": dist.get(c["Y_source"], float("nan")) if c["Y_source"] else float("nan"),
                   "source_opens": c["source_opens"], "opens_where_source_did": (sum(j["opens"] for j in c["judged"]) / len(labels)) if (labels and c["source_opens"]) else float("nan")}
            if labels and c["X"] in pcorpus:
                b = ST.bootstrap_tv(labels, pcorpus[c["X"]], L1, draws=min(draws, 2000), seed=seed)
                row.update({"tv_corpus": b["tv"], "tv_corpus_low": b["ci_low"], "tv_corpus_high": b["ci_high"]})
            else:
                row.update({"tv_corpus": float("nan"), "tv_corpus_low": float("nan"), "tv_corpus_high": float("nan")})
            if labels and c["X"] in pooled_by_x:
                b = ST.bootstrap_tv(labels, pooled_by_x[c["X"]], L1, draws=min(draws, 2000), seed=seed)
                row.update({"tv_pooled_X": b["tv"], "tv_pooled_X_low": b["ci_low"], "tv_pooled_X_high": b["ci_high"]})
            else:
                row.update({"tv_pooled_X": float("nan"), "tv_pooled_X_low": float("nan"), "tv_pooled_X_high": float("nan")})
            rows.append(row)
    return rows


def groups_by_x(cuts: list[dict], second: bool = False, replace: dict[str, list[str]] | None = None) -> dict[str, list[list[str]]]:
    g: dict[str, list[list[str]]] = defaultdict(list)
    for c in cuts:
        labels = replace[c["prefix_id"]] if (replace and c["prefix_id"] in replace) else cut_labels(c, second)
        if labels and c["X"]:
            g[c["X"]].append(labels)
    return dict(g)


def permutation_rows(run: dict, n_perm: int, seed: int, replace: dict[str, list[str]] | None = None, tag: str = "") -> list[dict]:
    rows = []
    scopes = {"c004": run["c004"]["cuts"], "e036": run["e036"]["cuts"], "pooled": run["c004"]["cuts"] + run["e036"]["cuts"]}
    for scope, cuts in scopes.items():
        g = groups_by_x(cuts, replace=replace)
        r = ST.permutation_test(g, L1, n_perm=n_perm, seed=seed)
        rows.append({"scope": scope + tag, "S_obs": r["S_obs"], "p": r["p"], "n_perm": r["n_perm"], "seed": r["seed"], "cuts_included": r["cuts"],
                     "groups": r["groups"], "singleton_X_excluded": " ".join(r["singletons"]), "S_perm_mean": r["S_perm_mean"]})
    return rows


def tv_corpus_rows(run: dict, pcorpus: dict, draws: int, seed: int) -> tuple[list[dict], dict[str, dict[str, float]]]:
    rows = []
    pooled: dict[str, dict[str, float]] = {}
    scopes = {"pooled": run["c004"]["cuts"] + run["e036"]["cuts"], "c004": run["c004"]["cuts"], "e036": run["e036"]["cuts"]}
    for scope, cuts in scopes.items():
        g = groups_by_x(cuts)
        for x in L1:
            if x not in g:
                continue
            labels = [l for cut in g[x] for l in cut]
            dist = ST.distribution(labels, L1)
            if scope == "pooled":
                pooled[x] = dist
            row = {"scope": scope, "X": x, "cuts": len(g[x]), "continuations": len(labels), **{f"p_{y}": dist[y] for y in L1}}
            if x in pcorpus:
                b = ST.bootstrap_tv(labels, pcorpus[x], L1, draws=min(draws, 5000), seed=seed)
                row.update({"tv_corpus": b["tv"], "tv_corpus_low": b["ci_low"], "tv_corpus_high": b["ci_high"], **{f"corpus_{y}": pcorpus[x][y] for y in L1}})
            rows.append(row)
    return rows, pooled


def history_rows(run: dict) -> tuple[list[dict], list[dict]]:
    cuts = [c for tid in ("c004", "e036") for c in run[tid]["cuts"] if cut_labels(c) and c["X"]]
    by_x: dict[str, list[dict]] = defaultdict(list)
    for c in cuts:
        by_x[c["X"]].append(c)
    hist, order = [], []
    for x, xs in by_x.items():
        for w in L1:
            with_w = [c for c in xs if w in c["prefix_nodes"][:-1]]
            without = [c for c in xs if w not in c["prefix_nodes"][:-1]]
            if len(with_w) >= MIN_CUTS_HISTORY and len(without) >= MIN_CUTS_HISTORY:
                dw = ST.distribution([l for c in with_w for l in cut_labels(c)], L1)
                dn = ST.distribution([l for c in without for l in cut_labels(c)], L1)
                dx = ST.distribution([l for c in xs for l in cut_labels(c)], L1)
                hist.append({"W": w, "X": x, "cuts_W_before_X": len(with_w), "cuts_without_W": len(without), "cuts_X": len(xs),
                             "n_W_before_X": sum(len(cut_labels(c)) for c in with_w), "n_without_W": sum(len(cut_labels(c)) for c in without),
                             **{f"p_{y}|W->X": dw[y] for y in L1}, **{f"p_{y}|X,noW": dn[y] for y in L1}, **{f"p_{y}|X": dx[y] for y in L1},
                             "tv_with_vs_without": ST.tv(dw, dn), "tv_with_vs_X": ST.tv(dw, dx)})
            # order: W -> X (last node X, W earlier) against X -> W (last node W, X earlier)
            if w != x and w in by_x:
                a = with_w
                b = [c for c in by_x[w] if x in c["prefix_nodes"][:-1]]
                if len(a) >= MIN_CUTS_HISTORY and len(b) >= MIN_CUTS_HISTORY and (w, x) not in {(o["X_first"], o["W_first"]) for o in order}:
                    da = ST.distribution([l for c in a for l in cut_labels(c)], L1)
                    db = ST.distribution([l for c in b for l in cut_labels(c)], L1)
                    order.append({"W_first": w, "X_first": x, "cuts_W_then_X": len(a), "cuts_X_then_W": len(b),
                                  "n_W_then_X": sum(len(cut_labels(c)) for c in a), "n_X_then_W": sum(len(cut_labels(c)) for c in b),
                                  **{f"p_{y}|W->X": da[y] for y in L1}, **{f"p_{y}|X->W": db[y] for y in L1}, "tv_orders": ST.tv(da, db)})
    return hist, order


def noise_rows(run: dict, pcorpus: dict, pooled_by_x: dict, n_perm: int, seed: int) -> tuple[list[dict], list[dict]]:
    rows = []
    replace = {}
    for tid in ("c004", "e036"):
        for c in run[tid]["cuts"]:
            if not c["noise"]:
                continue
            first, second = cut_labels(c), cut_labels(c, True)
            ids1 = {j["id"]: j["L1"] for j in c["judged"]}
            ids2 = {j["id"]: j["L1"] for j in c["noise"]}
            common = sorted(set(ids1) & set(ids2))
            d1, d2 = ST.distribution(first, L1), ST.distribution(second, L1)
            replace[c["prefix_id"]] = second
            rows.append({"trace_id": tid, "m": c["m"], "prefix_id": c["prefix_id"], "X": c["X"], "n_first": len(first), "n_second": len(second),
                         "first_node_agree": sum(1 for i in common if ids1[i] == ids2[i]), "first_node_common": len(common),
                         **{f"p1_{y}": d1[y] for y in L1}, **{f"p2_{y}": d2[y] for y in L1}, "tv_first_vs_second": ST.tv(d1, d2),
                         "opens_frac_first": (sum(j["opens"] for j in c["judged"]) / len(first)) if first else float("nan"),
                         "opens_frac_second": (sum(j["opens"] for j in c["noise"]) / len(second)) if second else float("nan"),
                         "wait_frac_first": (sum(j["wait"] for j in c["judged"]) / len(first)) if first else float("nan"),
                         "wait_frac_second": (sum(j["wait"] for j in c["noise"]) / len(second)) if second else float("nan"),
                         "tv_corpus_first": ST.tv(d1, pcorpus[c["X"]]) if c["X"] in pcorpus and first else float("nan"),
                         "tv_corpus_second": ST.tv(d2, pcorpus[c["X"]]) if c["X"] in pcorpus and second else float("nan"),
                         "tv_pooled_first": ST.tv(d1, pooled_by_x[c["X"]]) if c["X"] in pooled_by_x and first else float("nan"),
                         "tv_pooled_second": ST.tv(d2, pooled_by_x[c["X"]]) if c["X"] in pooled_by_x and second else float("nan")})
    perm = permutation_rows(run, n_perm, seed, replace=replace, tag="_second_labeling") if replace else []
    return rows, perm


# ----------------------------------------------------------------------------
# The summary document
# ----------------------------------------------------------------------------

def markdown_summary(run: dict, med: dict, trans: dict, figures: list[Path], args_info: dict) -> str:
    out = [f"# Stage-one analysis — {run['run_id']}", "",
           f"Generated by scripts/s4_analyze.py on {datetime.now():%Y-%m-%d %H:%M} from pre-registration 2026-09-17 v1, Sections 5 and 6. "
           f"Bootstrap draws {args_info['draws']}, permutations {args_info['perms']}, seed {args_info['seed']}. "
           "Wording rule (5.5): the numbers are described; no threshold is applied and no verdict is given.", ""]
    jm = run.get("judge_meta") or {}
    if jm:
        out += [f"Judge-dependent numbers (Section 6) carry the judge configuration: model `{jm.get('model')}`, prompt `{jm.get('prompt')}` (sha256 `{jm.get('prompt_sha256')}`), thinking {jm.get('thinking_mode')}; "
                "reference noise floor on the source traces Level 1 kappa 0.90 (pipeline v2, decision 17)"
                + ("; noise subset of this run: " + "; ".join(f"{r['collection']} Level 1 kappa {r['level1_kappa']}, first node {r['first_node_agree']}/{r['first_node_n']}" for r in jm["noise_subset"]) if jm.get("noise_subset") else "; noise subset: not run") + ".", ""]
    out += ["## Section 5 — the mediation tree (Q1)", ""]
    for name in ("nothink", "cut0"):
        c = run["shared"].get(name)
        if c:
            pc, (lc, hc) = phat(c, "C")
            pe, (le, he) = phat(c, "E")
            out.append(f"- {name}: n = {c['n']}; counts " + ", ".join(f"{L} {c['counts'][L]}" for L in LETTERS) + f", ? {c['unresolved']}; P̂(C) = {pc:.2f} [{lc:.2f}, {hc:.2f}], P̂(E) = {pe:.2f} [{le:.2f}, {he:.2f}].")
    out.append("")
    for s in med["summary"]:
        tid = s["trace_id"]
        out += [f"### {tid} (a_T = {s['a_T']}): {s['cuts_sampled']} cuts sampled, M = {s['M']}", "",
                f"P̂(cut-0) = {fmt(s['p_cut0'])}, P̂_M = {fmt(s['p_M'])}, total movement {fmt(s['total_movement'])}. "
                f"The largest shift, Δ = {s['delta_top']:+.2f}, sits in B_{s['B_top']:02d} ({fmt(s['tk_B_top'], 0)} tokens, {fmt(100 * s['tk_B_top_share'], 1)}% of the trace's {s['tk_trace']} reasoning tokens). "
                f"Gap between the two largest shifts {fmt(s['gap'])} [{fmt(s['gap_low'])}, {fmt(s['gap_high'])}] (bootstrap, {s['gap_draws']} draws). "
                f"Share of the total movement carried by the top one, two, three blocks: {fmt(s['share_top1'], 2)}, {fmt(s['share_top2'], 2)}, {fmt(s['share_top3'], 2)}; blocks to half of it: {fmt(s['blocks_to_half'])}; trivial blocks (Δ̂ = 0): {s['trivial_blocks']}.", "",
                "| m | block end | n | A | B | C | D | E | F | ? | P̂(a_T) [Wilson 95%] | Δ_m [Newcombe 95%] | Tk(B_m) |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r, d in zip([x for x in med["pcut"] if x["trace_id"] == tid], [x for x in med["delta"] if x["trace_id"] == tid]):
            out.append(f"| {r['m']} | s{r['block_end_s']} | {r['n']} | " + " | ".join(str(r[f'count_{L}']) for L in LETTERS) + f" | {r['count_unresolved']} | "
                       f"{r['p_aT']:.2f} [{r['p_aT_low']:.2f}, {r['p_aT_high']:.2f}] | {d['delta']:+.2f} [{fmt(d['delta_low'], 2)}, {fmt(d['delta_high'], 2)}]{' (trivial)' if d['trivial'] else ''} | {fmt(d['tk_block'], 0)} |")
        out.append("")
    if figures:
        out += ["Figures: " + ", ".join(f"`{p.relative_to(REPO).as_posix()}`" for p in figures), ""]
    out += ["## Section 6 — the transition tree at Level 1 (Q2, Q3)", "",
            "### Per cut: p̂_m over the eight labels of the first new node, opening fraction, Wait fraction, X_m, the source's next label", "",
            "| trace | m | X_m | labeled | " + " | ".join(D.L1_ABBR[y] for y in L1) + " | opens block | Wait | Y_source | p̂_m(Y_source) | TV to P_corpus[X] [boot] | TV to pooled p̂_X [boot] |",
            "|---|---|---|---|" + "---|" * len(L1) + "---|---|---|---|---|---|"]
    for r in trans["pnext"]:
        out.append(f"| {r['trace_id']} | {r['m']} | {r['X']} | {r['n_labeled']} | " + " | ".join(fmt(r[f'p_{y}'], 2) for y in L1)
                   + f" | {fmt(r['opens_block_frac'], 2)} | {fmt(r['wait_frac'], 2)} | {r['Y_source']} | {fmt(r['p_Y_source'], 2)} | "
                   f"{fmt(r['tv_corpus'])} [{fmt(r['tv_corpus_low'])}, {fmt(r['tv_corpus_high'])}] | {fmt(r['tv_pooled_X'])} [{fmt(r['tv_pooled_X_low'])}, {fmt(r['tv_pooled_X_high'])}] |")
    out += ["", "### Q2 — the type-only null (permutation test; S = mean TV between p̂_m and the pooled p̂_X of the cuts sharing X)", "",
            "| scope | cuts included | groups (X with ≥ 2 cuts) | singleton X excluded | S observed | mean S under the null | p |", "|---|---|---|---|---|---|---|"]
    for r in trans["permutation"] + trans.get("permutation_noise", []):
        out.append(f"| {r['scope']} | {r['cuts_included']} | {r['groups']} | {r['singleton_X_excluded'] or '—'} | {fmt(r['S_obs'])} | {fmt(r['S_perm_mean'])} | {fmt(r['p'], 4)} |")
    out += ["", "### Q3 — resampled p̂_X against P_corpus, per X", "",
            "| scope | X | cuts | continuations | " + " | ".join(D.L1_ABBR[y] for y in L1) + " | TV to P_corpus[X] [boot] |", "|---|---|---|---|" + "---|" * len(L1) + "---|"]
    for r in trans["tv_corpus"]:
        out.append(f"| {r['scope']} | {r['X']} | {r['cuts']} | {r['continuations']} | " + " | ".join(fmt(r[f'p_{y}'], 2) for y in L1)
                   + f" | {fmt(r.get('tv_corpus'))} [{fmt(r.get('tv_corpus_low'))}, {fmt(r.get('tv_corpus_high'))}] |")
    ps = [r for r in trans["pnext"] if r["Y_source"]]
    if ps:
        def finite_mean(values):
            v = [x for x in values if isinstance(x, (int, float)) and not math.isnan(x)]
            return float(np.mean(v)) if v else float("nan")
        mean_py = finite_mean([r["p_Y_source"] for r in ps])
        mean_open = finite_mean([r["opens_where_source_did"] for r in ps if r["source_opens"]])
        out += ["", f"Against P_source over {len(ps)} cuts: mean p̂_m(Y_source) = {mean_py:.2f}; where the source opened a block, the mean fraction of continuations opening one is {fmt(mean_open, 2)} (per-cut values in transition_psource.csv).", ""]
    out += ["### History forms — P̂(next | W → X) against P̂(next | X without W) (pairs with at least three cuts on each side)", ""]
    if trans["history"]:
        out += ["| W | X | cuts W→X / without / all X | n W→X / without | TV(with, without) | TV(with, all X) | p̂(next | W→X) | p̂(next | X, no W) |", "|---|---|---|---|---|---|---|---|"]
        for r in trans["history"]:
            out.append(f"| {r['W']} | {r['X']} | {r['cuts_W_before_X']} / {r['cuts_without_W']} / {r['cuts_X']} | {r['n_W_before_X']} / {r['n_without_W']} | {fmt(r['tv_with_vs_without'])} | {fmt(r['tv_with_vs_X'])} | "
                       + " ".join(f"{D.L1_ABBR[y]} {r[f'p_{y}|W->X']:.2f}" for y in L1 if r[f'p_{y}|W->X'] > 0) + " | " + " ".join(f"{D.L1_ABBR[y]} {r[f'p_{y}|X,noW']:.2f}" for y in L1 if r[f'p_{y}|X,noW'] > 0) + " |")
    else:
        out.append("(no pair with at least three cuts on each side)")
    out += ["", "### Order comparison — P̂(next | W → X) against P̂(next | X → W)", ""]
    if trans["order"]:
        out += ["| W then X (last node X) | X then W (last node W) | cuts | n | TV between the orders |", "|---|---|---|---|---|"]
        for r in trans["order"]:
            out.append(f"| {r['W_first']} → {r['X_first']} | {r['X_first']} → {r['W_first']} | {r['cuts_W_then_X']} / {r['cuts_X_then_W']} | {r['n_W_then_X']} / {r['n_X_then_W']} | {fmt(r['tv_orders'])} |")
    else:
        out.append("(no pair with both orders on at least three cuts each)")
    out += ["", "### The second labeling (Section 6.5): the relabeled cuts", ""]
    if trans["noise"]:
        out += ["| trace | m | X | n first / second | first node agree / common | TV(p̂ first, p̂ second) | TV to P_corpus first / second | TV to pooled p̂_X first / second | opens first / second | Wait first / second |", "|---|---|---|---|---|---|---|---|---|---|"]
        for r in trans["noise"]:
            out.append(f"| {r['trace_id']} | {r['m']} | {r['X']} | {r['n_first']} / {r['n_second']} | {r['first_node_agree']} / {r['first_node_common']} | {fmt(r['tv_first_vs_second'])} | "
                       f"{fmt(r['tv_corpus_first'])} / {fmt(r['tv_corpus_second'])} | {fmt(r['tv_pooled_first'])} / {fmt(r['tv_pooled_second'])} | {fmt(r['opens_frac_first'], 2)} / {fmt(r['opens_frac_second'], 2)} | {fmt(r['wait_frac_first'], 2)} / {fmt(r['wait_frac_second'], 2)} |")
        out.append("")
        out.append("The permutation test with the second labeling substituted for these cuts appears above with the suffix `_second_labeling`.")
    else:
        out.append("(no second labeling in the judge folder)")
    out.append("")
    return "\n".join(out)


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def analyze(run_dir: Path, judge_dir: Path | None, out_dir: Path, pcorpus_path: Path = PCORPUS_DEFAULT, draws: int = 10000, perms: int = 10000,
            seed: int = 0, listing_path: Path | str = D.LISTING, sentences_source: Path | str = D.SENTENCES_SOURCE, log=print) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ctx = reviewed_context(listing_path, sentences_source)
    run = load_run(Path(run_dir), Path(judge_dir) if judge_dir else None, ctx)
    pcorpus = load_pcorpus(Path(pcorpus_path))
    med = mediation(run, draws, seed)
    write_csv(out_dir / "mediation_pcut.csv", med["pcut"])
    write_csv(out_dir / "mediation_delta.csv", med["delta"])
    write_csv(out_dir / "mediation_summary.csv", med["summary"])
    figures = []
    for tid in ("c004", "e036"):
        figures += plot_trace(run, tid, med, out_dir)
    trans: dict = {}
    trans["tv_corpus"], pooled = tv_corpus_rows(run, pcorpus, draws, seed)
    trans["pnext"] = pnext_rows(run, pcorpus, pooled, draws, seed)
    trans["permutation"] = permutation_rows(run, perms, seed)
    trans["history"], trans["order"] = history_rows(run)
    trans["noise"], trans["permutation_noise"] = noise_rows(run, pcorpus, pooled, perms, seed)
    write_csv(out_dir / "transition_pnext.csv", trans["pnext"])
    write_csv(out_dir / "transition_permutation.csv", trans["permutation"] + trans["permutation_noise"])
    write_csv(out_dir / "transition_tv_corpus.csv", trans["tv_corpus"])
    write_csv(out_dir / "transition_psource.csv", [{k: r[k] for k in ("trace_id", "m", "prefix_id", "block_end_s", "X", "Y_source", "p_Y_source", "source_opens", "opens_block_frac", "opens_where_source_did")} for r in trans["pnext"]])
    write_csv(out_dir / "transition_history.csv", trans["history"])
    write_csv(out_dir / "transition_order.csv", trans["order"])
    write_csv(out_dir / "transition_noise.csv", trans["noise"])
    text = markdown_summary(run, med, trans, figures, {"draws": draws, "perms": perms, "seed": seed})
    (out_dir / "stage1_summary.md").write_text(text, encoding="utf-8")
    result = {"out_dir": str(out_dir), "figures": [str(p) for p in figures], "mediation": med["summary"], "permutation": trans["permutation"],
              "noise": trans["noise"], "n_pnext_rows": len(trans["pnext"]), "n_history_rows": len(trans["history"]), "n_order_rows": len(trans["order"]),
              "tables": sorted(p.name for p in out_dir.glob("*.csv")) + ["stage1_summary.md"]}
    (out_dir / "analysis_summary.json").write_text(json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8")
    log(f"analysis written to {out_dir}: {len(result['tables'])} tables, {len(figures)} figures")
    return result


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Pipeline step (9/9): the stage-one analysis (registration Sections 5 and 6).")
    ap.add_argument("--run", required=True)
    ap.add_argument("--judge", help="judge folder of the run (s3 output); default: the run's newest judge_* folder")
    ap.add_argument("--out", help="default: the run folder itself (registration 7.1: tables and stage1_summary.md in the run folder)")
    ap.add_argument("--pcorpus", default=str(PCORPUS_DEFAULT))
    ap.add_argument("--draws", type=int, default=10000)
    ap.add_argument("--perms", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)
    run_dir = Path(args.run)
    judge = Path(args.judge) if args.judge else next(iter(sorted(run_dir.glob("judge_*"), reverse=True)), None)
    print(f"s4_analyze: run={run_dir} judge={judge} out={Path(args.out) if args.out else run_dir} pcorpus={args.pcorpus} draws={args.draws} perms={args.perms} seed={args.seed}")
    res = analyze(run_dir, judge, Path(args.out) if args.out else run_dir, Path(args.pcorpus), args.draws, args.perms, args.seed)
    print(json.dumps({k: v for k, v in res.items() if k not in ("noise",)}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
