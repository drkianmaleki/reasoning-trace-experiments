#!/usr/bin/env python3
"""transitions.py -- the transition tables of pipeline v2, step (5/9) (labeling scheme v6,
Section 0d), computed from blocks records of the derivation.  Offline, standard library only.

- pcorpus_L1.csv (5a/9): the corpus transition matrix at Level 1 -- counts of consecutive node
  pairs (Level 1 of node i -> Level 1 of node i+1) over the traces of a collection, a combined
  node counted under its first path; a row-normalized copy (P_corpus(Y | X)) in
  pcorpus_L1_rownorm.csv; the marginal counts of node labels and the blocks per trace.
- psource_<trace>.csv (5b/9): from the reviewed labels under R4, for every block-end cut m
  (every block but the last): the Level 1 label of the node that ends block m and the Level 1
  label of the node that follows it in the source (the opener of block m+1).
- pnext_<collection>.csv (5c/9): one row per archived cut (prefix_id): trace arm, cut, the
  number of continuations, the counts of the Level 1 label of the first new node after the cut
  (one column per label), the count of continuations whose first new node opens a block under
  R1-R4, the count whose first sentence is an R4 "Wait" sentence, and the failures.

Every CSV has a Markdown twin (markdown_* functions) for the run's summary.
"""
from __future__ import annotations

import csv
import statistics
from collections import Counter
from pathlib import Path

import derivation as D

L1 = D.L1_ORDER


def node_l1(node: dict) -> str:
    return D.node_level1(node)


# ----------------------------------------------------------------------------
# P_corpus
# ----------------------------------------------------------------------------

def pcorpus(blocks_records: list[dict]) -> dict:
    """blocks_records: one derivation record per trace with "nodes" and "blocks"."""
    counts = {x: {y: 0 for y in L1} for x in L1}
    marginal = Counter()
    per_trace = []
    pairs = 0
    for rec in blocks_records:
        seq = [node_l1(n) for n in rec["nodes"]]
        for x, y in zip(seq, seq[1:]):
            counts[x][y] += 1
            pairs += 1
        marginal.update(seq)
        per_trace.append({"trace_id": rec["trace_id"], "nodes": len(seq), "blocks": len(rec["blocks"])})
    rownorm = {x: {y: (counts[x][y] / sum(counts[x].values()) if sum(counts[x].values()) else float("nan")) for y in L1} for x in L1}
    nb = [t["blocks"] for t in per_trace]
    nn = [t["nodes"] for t in per_trace]
    return {"counts": counts, "rownorm": rownorm, "marginal": {x: marginal.get(x, 0) for x in L1}, "pairs": pairs,
            "traces": len(per_trace), "per_trace": per_trace,
            "blocks_per_trace": {"min": min(nb) if nb else None, "median": statistics.median(nb) if nb else None, "max": max(nb) if nb else None},
            "nodes_per_trace": {"min": min(nn) if nn else None, "median": statistics.median(nn) if nn else None, "max": max(nn) if nn else None}}


def write_pcorpus(out_dir: Path | str, res: dict, stem: str = "pcorpus_L1") -> tuple[Path, Path]:
    out_dir = Path(out_dir)
    p1 = out_dir / f"{stem}.csv"
    with open(p1, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["X_current_node"] + [f"Y_{y}" for y in L1] + ["row_total", "nodes_with_label_X"])
        for x in L1:
            w.writerow([x] + [res["counts"][x][y] for y in L1] + [sum(res["counts"][x].values()), res["marginal"][x]])
    p2 = out_dir / f"{stem}_rownorm.csv"
    with open(p2, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["X_current_node"] + [f"P_next_{y}" for y in L1] + ["row_total"])
        for x in L1:
            w.writerow([x] + [f"{res['rownorm'][x][y]:.4f}" for y in L1] + [sum(res["counts"][x].values())])
    return p1, p2


def markdown_pcorpus(res: dict, title: str) -> str:
    abbr = D.L1_ABBR
    out = [f"### {title}", "",
           f"{res['traces']} traces, {sum(res['marginal'].values())} nodes, {res['pairs']} consecutive node pairs; a combined node counts under its first path. "
           f"Blocks per trace min / median / max: {res['blocks_per_trace']['min']} / {res['blocks_per_trace']['median']} / {res['blocks_per_trace']['max']}; "
           f"nodes per trace {res['nodes_per_trace']['min']} / {res['nodes_per_trace']['median']} / {res['nodes_per_trace']['max']}.", "",
           "Counts (row X = current node, column Y = next node):", "",
           "| X \\ Y | " + " | ".join(abbr[y] for y in L1) + " | row total | nodes X |", "|---|" + "---|" * (len(L1) + 2)]
    for x in L1:
        out.append(f"| {x} | " + " | ".join(str(res["counts"][x][y]) for y in L1) + f" | {sum(res['counts'][x].values())} | {res['marginal'][x]} |")
    out += ["", "Row-normalized, P_corpus(Y | X):", "", "| X \\ Y | " + " | ".join(abbr[y] for y in L1) + " |", "|---|" + "---|" * len(L1)]
    for x in L1:
        out.append(f"| {x} | " + " | ".join("nan" if res["rownorm"][x][y] != res["rownorm"][x][y] else f"{res['rownorm'][x][y]:.3f}" for y in L1) + " |")
    out += ["", "Marginal node counts: " + ", ".join(f"{x} {res['marginal'][x]}" for x in L1) + "."]
    return "\n".join(out)


# ----------------------------------------------------------------------------
# P_source
# ----------------------------------------------------------------------------

def psource(derived: dict) -> list[dict]:
    """derived: a derivation record of a source trace (reviewed labels under R4)."""
    nodes, blocks = derived["nodes"], derived["blocks"]
    rows = []
    for m in range(len(blocks) - 1):
        last = max((n for n in nodes if n["block"] == m), key=lambda n: n["s_end"])
        first_next = min((n for n in nodes if n["block"] == m + 1), key=lambda n: n["s_start"])
        rows.append({"m": m, "s_cut": blocks[m]["s_end"], "last_node": last["name"], "last_node_label": node_l1(last),
                     "source_next_node": first_next["name"], "source_next_label": node_l1(first_next),
                     "next_opener_rule": blocks[m + 1]["opener_rule"]})
    return rows


def write_psource(path: Path | str, rows: list[dict]) -> Path:
    path = Path(path)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["m", "s_cut", "last_node", "last_node_label", "source_next_node", "source_next_label", "next_opener_rule"])
        w.writeheader()
        w.writerows(rows)
    return path


def markdown_psource(rows: list[dict], title: str) -> str:
    out = [f"### {title}", "", "| m | cut after s | last node (label) | source next node (label) | opener rule |", "|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['m']} | s{r['s_cut']} | {r['last_node']} ({r['last_node_label']}) | {r['source_next_node']} ({r['source_next_label']}) | {r['next_opener_rule']} |")
    c = Counter((r["last_node_label"], r["source_next_label"]) for r in rows)
    out += ["", "Pairs (last → next): " + "; ".join(f"{a} → {b} {n}" for (a, b), n in c.most_common()) + "."]
    return "\n".join(out)


# ----------------------------------------------------------------------------
# P_next after the archived cuts
# ----------------------------------------------------------------------------

PNEXT_FIELDS = ["prefix_id", "trace_arm", "cut", "last_node_label", "n", "n_labeled", "n_failed"] + [f"next_{x}" for x in L1] + ["opens_block", "first_is_wait"]


def pnext(blocks_records: list[dict], failures: dict[str, dict] | None = None, meta: dict[str, dict] | None = None) -> list[dict]:
    """blocks_records: continuation derivation records (with prefix_id, trace_arm, cut,
    last_prefix_node_label, first_new_node {L1, opens_block}, first_sentence_r4); failures:
    {trace_id: meta} of continuations without labels."""
    groups: dict[str, dict] = {}
    for rec in blocks_records:
        g = groups.setdefault(rec["prefix_id"], {"prefix_id": rec["prefix_id"], "trace_arm": rec["trace_arm"], "cut": rec["cut"],
                                                 "last_node_label": rec.get("last_prefix_node_label"), "n": 0, "n_labeled": 0, "n_failed": 0,
                                                 **{f"next_{x}": 0 for x in L1}, "opens_block": 0, "first_is_wait": 0})
        g["n"] += 1
        g["n_labeled"] += 1
        fn = rec["first_new_node"]
        g[f"next_{fn['L1']}"] += 1
        g["opens_block"] += int(bool(fn["opens_block"]))
        g["first_is_wait"] += int(bool(rec.get("first_sentence_r4")))
    for tid, m in (failures or {}).items():
        g = groups.setdefault(m["prefix_id"], {"prefix_id": m["prefix_id"], "trace_arm": m["trace_arm"], "cut": m["cut"],
                                               "last_node_label": m.get("last_prefix_node_label"), "n": 0, "n_labeled": 0, "n_failed": 0,
                                               **{f"next_{x}": 0 for x in L1}, "opens_block": 0, "first_is_wait": 0})
        g["n"] += 1
        g["n_failed"] += 1
    arm_order = {"shared": 0, "c004": 1, "e036": 2}
    return sorted(groups.values(), key=lambda g: (arm_order.get(g["trace_arm"], 9), g["cut"], g["prefix_id"]))


def write_pnext(path: Path | str, rows: list[dict]) -> Path:
    path = Path(path)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=PNEXT_FIELDS)
        w.writeheader()
        w.writerows(rows)
    return path


def markdown_pnext(rows: list[dict], title: str, limit: int | None = None) -> str:
    abbr = D.L1_ABBR
    out = [f"### {title}", "", "| prefix_id | arm | cut | last node label | n | labeled | failed | " + " | ".join(abbr[x] for x in L1) + " | opens block | first is Wait |",
           "|---|---|---|---|---|---|---|" + "---|" * len(L1) + "---|---|"]
    for r in rows[:limit] if limit else rows:
        out.append(f"| {r['prefix_id']} | {r['trace_arm']} | {r['cut']} | {r['last_node_label']} | {r['n']} | {r['n_labeled']} | {r['n_failed']} | "
                   + " | ".join(str(r[f'next_{x}']) for x in L1) + f" | {r['opens_block']} | {r['first_is_wait']} |")
    return "\n".join(out)
