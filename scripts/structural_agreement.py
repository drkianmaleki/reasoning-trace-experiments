#!/usr/bin/env python3
"""structural_agreement.py -- structural discrepancy metrics between the reviewed labels and a
judge's labels of the same traces (Kian, 2026-09-17).  Both labelings run through
scripts/derivation.py; the metrics compare what the pipeline actually uses:

1. Block boundaries: opener sentence indices in both derivations -- hits, misses (reviewed
   openers without a judge opener), extras (judge openers without a reviewed one), near misses
   (a miss whose nearest judge opener is within one sentence), precision, recall, F1, and for
   each hit whether the opener rule (R1/R2/R3/R4) agrees; under R4 also the R4 openers of both
   sides (they must coincide, since R4 reads the sentence text).
2. Next node after the reviewed cuts: for every reviewed block except the last, the first
   sentence of the following block; the Level 1 label of that sentence in the judge's labels
   (first path of a combined sentence) against the reviewed one -- agreement rate and the
   confusion pairs.  This is the quantity the transition tree is built from.
3. Node boundaries and labels: node end indices in both derivations -- hits, misses, extras,
   F1; then every reviewed node is matched to the judge node with the largest overlap (ties: the
   earlier judge node) -- the Level 1 agreement rate of matched nodes, the reviewed nodes the
   judge splits (a reviewed node intersecting two or more judge nodes) and merges (a reviewed
   node whose matched judge node is also the match of another reviewed node).
4. Sentence-level decomposition of the disagreements on label sets: Level 1 wrong; Level 1
   right but Level 2 wrong; Levels 1 and 2 right but Level 3 wrong; all right.

With `texts` (rule R4, 2026-09-17) both derivations take the sentence texts; the judge labels
are expected to be R4-enforced already (derivation.apply_r4_labels).  Pooled numbers sum the
counts over the traces and recompute the rates.  Standard library only.
"""
from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path

import derivation as D

LEVEL1_OF = D.level1


def _truncate(path: str, level: int) -> str:
    return " > ".join(D.split_path(path)[:level])


def _rates(hits: int, n_ref: int, n_oth: int) -> tuple[float, float, float]:
    p = hits / n_oth if n_oth else 0.0
    r = hits / n_ref if n_ref else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


def judge_labels_from_file(path: Path | str, raw: bool = False) -> dict[str, list[list[str]]]:
    """{trace_id: [[path, ...] per sentence]} from a labels file.  With raw=True the labels as
    the judge gave them (`labels_before_r4` where R4 enforcement changed them)."""
    out: dict[str, list[list[str]]] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                labels = r["labels"]
                if raw and r.get("labels_before_r4"):
                    labels = r["labels_before_r4"]
                out.setdefault(r["trace_id"], []).append([" > ".join(x for x in (l["L1"], l["L2"], l["L3"]) if x) for l in labels])
    return out


# ----------------------------------------------------------------------------
# The four metric groups
# ----------------------------------------------------------------------------

def block_metrics(ref_rec: dict, oth_rec: dict) -> dict:
    ref = {b["s_start"]: b["opener_rule"] for b in ref_rec["blocks"]}
    oth = {b["s_start"]: b["opener_rule"] for b in oth_rec["blocks"]}
    hits = sorted(set(ref) & set(oth))
    misses = sorted(set(ref) - set(oth))
    extras = sorted(set(oth) - set(ref))
    near = [m for m in misses if any(abs(m - o) <= 1 for o in oth)]
    rule_agree = sum(1 for h in hits if ref[h] == oth[h])
    p, r, f = _rates(len(hits), len(ref), len(oth))
    ref_r4 = sorted(s for s, rule in ref.items() if rule == "R4")
    oth_r4 = sorted(s for s, rule in oth.items() if rule == "R4")
    return {"n_reviewed": len(ref), "n_judge": len(oth), "hits": len(hits), "misses": len(misses), "extras": len(extras),
            "near_misses": len(near), "precision": p, "recall": r, "f1": f, "rule_agree": rule_agree,
            "r4_reviewed": len(ref_r4), "r4_judge": len(oth_r4), "r4_agree": len(set(ref_r4) & set(oth_r4)),
            "misses_idx": misses, "extras_idx": extras}


def next_node_metrics(ref_labels: list[list[str]], oth_labels: list[list[str]], ref_rec: dict) -> dict:
    pairs = []
    for m in range(len(ref_rec["blocks"]) - 1):
        s = ref_rec["blocks"][m + 1]["s_start"]
        pairs.append((LEVEL1_OF(ref_labels[s][0]), LEVEL1_OF(oth_labels[s][0])))
    agree = sum(1 for a, b in pairs if a == b)
    conf = Counter((a, b) for a, b in pairs if a != b)
    return {"n_cuts": len(pairs), "agree": agree, "rate": agree / len(pairs) if pairs else float("nan"),
            "confusions": conf.most_common()}


def node_metrics(ref_rec: dict, oth_rec: dict) -> dict:
    rnodes, onodes = ref_rec["nodes"], oth_rec["nodes"]
    ref_ends = {n["s_end"] for n in rnodes}
    oth_ends = {n["s_end"] for n in onodes}
    hits = len(ref_ends & oth_ends)
    p, r, f = _rates(hits, len(ref_ends), len(oth_ends))

    def overlap(a: dict, b: dict) -> int:
        return max(0, min(a["s_end"], b["s_end"]) - max(a["s_start"], b["s_start"]) + 1)

    best_of: dict[int, int] = {}
    splits = 0
    l1_agree = 0
    for i, rn in enumerate(rnodes):
        overlaps = [(overlap(rn, on), j) for j, on in enumerate(onodes) if overlap(rn, on) > 0]
        if len(overlaps) >= 2:
            splits += 1
        best = max(overlaps, key=lambda x: (x[0], -x[1]))[1]
        best_of[i] = best
        if rn["L1"] == onodes[best]["L1"]:
            l1_agree += 1
    counts = Counter(best_of.values())
    merged = sum(1 for i, j in best_of.items() if counts[j] >= 2)
    return {"n_reviewed": len(rnodes), "n_judge": len(onodes), "end_hits": hits, "end_misses": len(ref_ends - oth_ends),
            "end_extras": len(oth_ends - ref_ends), "precision": p, "recall": r, "f1": f,
            "matched_l1_agree": l1_agree, "matched_l1_rate": l1_agree / len(rnodes) if rnodes else float("nan"),
            "split": splits, "merged": merged}


def sentence_decomposition(ref_labels: list[list[str]], oth_labels: list[list[str]]) -> dict:
    c = Counter()
    for r, o in zip(ref_labels, oth_labels):
        s1r, s1o = {_truncate(p, 1) for p in r}, {_truncate(p, 1) for p in o}
        s2r, s2o = {_truncate(p, 2) for p in r}, {_truncate(p, 2) for p in o}
        s3r, s3o = set(r), set(o)
        if s3r == s3o:
            c["all_right"] += 1
        elif s2r == s2o:
            c["l3_wrong"] += 1
        elif s1r == s1o:
            c["l2_wrong"] += 1
        else:
            c["l1_wrong"] += 1
    n = len(ref_labels)
    out = {k: c.get(k, 0) for k in ("l1_wrong", "l2_wrong", "l3_wrong", "all_right")}
    out["n"] = n
    disagreements = n - out["all_right"]
    for k in ("l1_wrong", "l2_wrong", "l3_wrong", "all_right"):
        out[k + "_share"] = out[k] / n if n else float("nan")
    out["l1_share_of_disagreements"] = out["l1_wrong"] / disagreements if disagreements else float("nan")
    return out


def trace_metrics(trace_id: str, ref_labels: list[list[str]], oth_labels: list[list[str]],
                  texts: list[str] | None = None) -> dict:
    if len(ref_labels) != len(oth_labels):
        raise ValueError(f"{trace_id}: {len(ref_labels)} reviewed vs {len(oth_labels)} judge sentences")
    ref_rec = D.derive(ref_labels, trace_id, "reviewed", texts)
    oth_rec = D.derive(oth_labels, trace_id, "judge", texts)
    return {"trace_id": trace_id, "n": len(ref_labels), "r4": texts is not None,
            "blocks": block_metrics(ref_rec, oth_rec),
            "next_node": next_node_metrics(ref_labels, oth_labels, ref_rec),
            "nodes": node_metrics(ref_rec, oth_rec),
            "sentences": sentence_decomposition(ref_labels, oth_labels)}


def pooled_metrics(per_trace: list[dict]) -> dict:
    b = {k: sum(t["blocks"][k] for t in per_trace) for k in ("n_reviewed", "n_judge", "hits", "misses", "extras", "near_misses", "rule_agree",
                                                            "r4_reviewed", "r4_judge", "r4_agree")}
    b["precision"], b["recall"], b["f1"] = _rates(b["hits"], b["n_reviewed"], b["n_judge"])
    b["misses_idx"], b["extras_idx"] = [], []
    nn = {"n_cuts": sum(t["next_node"]["n_cuts"] for t in per_trace), "agree": sum(t["next_node"]["agree"] for t in per_trace)}
    nn["rate"] = nn["agree"] / nn["n_cuts"] if nn["n_cuts"] else float("nan")
    conf = Counter()
    for t in per_trace:
        for pair, c in t["next_node"]["confusions"]:
            conf[pair] += c
    nn["confusions"] = conf.most_common()
    nd = {k: sum(t["nodes"][k] for t in per_trace) for k in ("n_reviewed", "n_judge", "end_hits", "end_misses", "end_extras", "matched_l1_agree", "split", "merged")}
    nd["precision"], nd["recall"], nd["f1"] = _rates(nd["end_hits"], nd["end_hits"] + nd["end_misses"], nd["end_hits"] + nd["end_extras"])
    nd["matched_l1_rate"] = nd["matched_l1_agree"] / nd["n_reviewed"] if nd["n_reviewed"] else float("nan")
    s = {k: sum(t["sentences"][k] for t in per_trace) for k in ("l1_wrong", "l2_wrong", "l3_wrong", "all_right", "n")}
    dis = s["n"] - s["all_right"]
    for k in ("l1_wrong", "l2_wrong", "l3_wrong", "all_right"):
        s[k + "_share"] = s[k] / s["n"] if s["n"] else float("nan")
    s["l1_share_of_disagreements"] = s["l1_wrong"] / dis if dis else float("nan")
    return {"trace_id": "pooled", "n": s["n"], "r4": all(t.get("r4") for t in per_trace), "blocks": b, "next_node": nn, "nodes": nd, "sentences": s}


def compute(judge: dict[str, list[list[str]]], reviewed: dict[str, list[list[str]]],
            texts: dict[str, list[str]] | None = None) -> dict[str, dict]:
    """{trace_id: metrics, ..., 'pooled': metrics} over the traces present in both.  With
    `texts` ({trace_id: [text, ...]}) rule R4 applies to both derivations."""
    traces = [t for t in reviewed if t in judge]
    out = {t: trace_metrics(t, reviewed[t], judge[t], texts[t] if texts is not None else None) for t in traces}
    out["pooled"] = pooled_metrics([out[t] for t in traces])
    return out


# ----------------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------------

def rows(results: dict[str, dict]) -> list[tuple[str, str, str, object]]:
    out = []
    for scope, m in results.items():
        for group in ("blocks", "next_node", "nodes", "sentences"):
            for k, v in m[group].items():
                if k in ("misses_idx", "extras_idx"):
                    v = " ".join(str(x) for x in v)
                elif k == "confusions":
                    v = "; ".join(f"{a}->{b}:{c}" for (a, b), c in v)
                elif isinstance(v, float):
                    v = f"{v:.4f}"
                out.append((scope, group, k, v))
    return out


def write_csv(path: Path | str, results: dict[str, dict]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["scope", "group", "metric", "value"])
        w.writerows(rows(results))


def _fmt(x) -> str:
    return "nan" if isinstance(x, float) and math.isnan(x) else (f"{x:.3f}" if isinstance(x, float) else str(x))


def markdown(results: dict[str, dict], title: str) -> str:
    r4 = results.get("pooled", {}).get("r4", False)
    out = [f"### {title}", "",
           "| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits |"
           + (" R4 openers reviewed / judge / agree |" if r4 else "")
           + " next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |",
           "|---|---|---|---|---|" + ("---|" if r4 else "") + "---|---|---|---|---|---|---|"]
    for scope, m in results.items():
        b, nn, nd, s = m["blocks"], m["next_node"], m["nodes"], m["sentences"]
        out.append(f"| {scope} | {b['n_reviewed']} / {b['n_judge']} | {b['hits']} / {b['misses']} ({b['near_misses']}) / {b['extras']} | "
                   f"{_fmt(b['precision'])} / {_fmt(b['recall'])} / {_fmt(b['f1'])} | {b['rule_agree']} / {b['hits']} | "
                   + (f"{b['r4_reviewed']} / {b['r4_judge']} / {b['r4_agree']} | " if r4 else "")
                   + f"{nn['agree']} / {nn['n_cuts']} ({_fmt(nn['rate'])}) | {nd['end_hits']} / {nd['end_misses']} / {nd['end_extras']} | {_fmt(nd['f1'])} | "
                   f"{nd['matched_l1_agree']} / {nd['n_reviewed']} ({_fmt(nd['matched_l1_rate'])}) | {nd['split']} / {nd['merged']} | "
                   f"{s['l1_wrong']} / {s['l2_wrong']} / {s['l3_wrong']} / {s['all_right']} | {_fmt(s['l1_share_of_disagreements'])} |")
    conf = results["pooled"]["next_node"]["confusions"]
    if conf:
        out += ["", "Next-node confusions (reviewed → judge, pooled): " + "; ".join(f"{a} → {b} {c}" for (a, b), c in conf)]
    for scope, m in results.items():
        if scope == "pooled":
            continue
        if m["blocks"]["misses_idx"] or m["blocks"]["extras_idx"]:
            out.append(f"{scope}: missed reviewed openers at s{', s'.join(map(str, m['blocks']['misses_idx'])) or '-'}; extra judge openers at s{', s'.join(map(str, m['blocks']['extras_idx'])) or '-'}")
    return "\n".join(out)
