#!/usr/bin/env python3
"""s6_order.py -- the order of three kinds of sentence against the final answer (results v1, Section 8).

Why this script exists.  Section 8 of the stage-one results document was computed ad hoc while the
document was drafted; no script produced it, so its numbers -- among them the two in the abstract --
could not be rerun or checked.  This step recomputes them from the run's own files and writes the
tables the paper cites.  It is an ANALYSIS ADDED AFTER THE PRE-REGISTRATION (the registration's
Section 6 covers the Level 1 order and history tables, `transition_order.csv` and
`transition_history.csv`, which are a different quantity: those are about the next MOVE, this one is
about the final ANSWER).  Everything it produces is reported as exploratory.

The three kinds (leaves of the labeling scheme, decided by Kian as the sentences most likely to
carry the decision):
  algebra  any leaf whose last level is "algebra" -- Reasoning > calculation | logical reasoning |
           defining symbols > algebra, Assumption > branching (case split) > algebra,
           Example > non-exhaustive listing > algebra
  famous   Knowledge > world knowledge > famous problem (CRT)
  hedge    Reasoning > hedge word analysis (with or without a third level)
A combined sentence carries two label paths; the sentence counts for a kind if either path matches.

What is read for one continuation.  The whole text the model saw and wrote: the prefix, with the
reviewed labels of the source trace (labels_source_reviewed_v4.jsonl, sentences 0 .. prefix_n-1 of
that trace), followed by the continuation, with the judge's labels (labels_<collection>_judge.jsonl,
one record per sentence).  The first appearance of each kind is its smallest sentence index in that
combined sequence.  A kind that never appears is left out of the pattern, so the pattern of a
continuation is the sequence of the kinds it does contain, in the order of first appearance:
"algebra --> famous", "famous --> algebra --> hedge", "algebra", "(none)".

The answer.  From the run's continuations.jsonl: --scoring strict (default; decision P6 of
2026-09-19, the paper's canonical reading) reads the letter from the last line of a finished reply
through scripts/s5_rescore.py; --scoring registered uses the `letters` field as the run recorded it.
Unresolved continuations stay in every denominator and are reported as "?".

The pooling caveat, which the tables make visible.  At every cut but cut-0 the order is inherited
from the prefix: the C-trace does its algebra early and recognizes the riddle later, the E-trace the
other way round, so a pooled P(answer | pattern) mixes the order with the source trace.  Therefore
`order_by_cut.csv` gives every pattern separately for each cut, `order_shares.csv` says how many
continuations of each pattern come from which trace, and `order_cut0.csv` is the one comparison
where the model chose the order itself (no prefix at all).

  python scripts/s6_order.py --run runs/experiments/resample_blocks_<stamp>/ [--judge <dir>]
      [--out <dir>] [--scoring strict|registered|both]

Outputs in --out (default: the run folder for --scoring registered, the derived `<run>_strict`
folder for strict, so that neither overwrites the other):
  order_patterns.csv   one row per continuation: cut, trace, answer, first index of each kind, pattern
  order_pooled.csv     one row per pattern: n, the answer distribution, and the share per source trace
  order_pairs.csv      the pairwise question for each of the three pairs: P(answer | X --> Y) against
                       P(answer | Y --> X), pooled, with Wilson intervals and the Newcombe interval
                       of the difference
  order_by_cut.csv     the same patterns counted within each cut
  order_cut0.csv       the cut-0 continuations alone
  order_summary.md     the numbers in sentences, with the caveat stated
Standard library only.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import s5_rescore as S5  # noqa: E402
import stats_utils as ST  # noqa: E402

KINDS = ("algebra", "famous", "hedge")
KIND_TITLE = {"algebra": "algebra", "famous": "famous problem", "hedge": "hedge word"}
LETTERS = "ABCDEF"
REPORT = ("C", "E")


def kind_of(path: list[str]) -> str | None:
    """The kind of one label path ("Level 1 > Level 2 [> Level 3]" as a list), or None."""
    if not path:
        return None
    if path[-1] == "algebra":
        return "algebra"
    if path[-1] == "famous problem (CRT)":
        return "famous"
    if len(path) >= 2 and path[1] == "hedge word analysis":
        return "hedge"
    return None


def path_of(label: dict) -> list[str]:
    return [x for x in (label.get("L1"), label.get("L2"), label.get("L3")) if x]


def kinds_of_sentence(labels: list[dict]) -> set[str]:
    out = set()
    for lab in labels or []:
        k = kind_of(path_of(lab))
        if k:
            out.add(k)
    return out


def read_jsonl(path: Path):
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


def load_prefix_kinds(judge_dir: Path) -> dict[str, dict[int, set[str]]]:
    """{trace_id: {sentence index: kinds}} from the reviewed labels of the source traces."""
    path = next(iter(sorted(Path(judge_dir).rglob("labels_source_reviewed_v4.jsonl"))), None)
    if path is None:
        raise SystemExit(f"no labels_source_reviewed_v4.jsonl under {judge_dir}")
    out: dict[str, dict[int, set[str]]] = defaultdict(dict)
    for d in read_jsonl(path):
        out[d["trace_id"]][int(d["s"])] = kinds_of_sentence(d.get("labels"))
    return out


def load_continuation_kinds(judge_dir: Path) -> tuple[dict[str, dict[int, set[str]]], dict[str, tuple[str, int]]]:
    """({continuation id: {sentence index: kinds}}, {continuation id: (prefix_id, prefix_n)}).

    The noise_* folders (the second labeling of two cuts) are skipped: the first labeling is the one
    the analysis uses, as in the registered step.
    """
    kinds: dict[str, dict[int, set[str]]] = defaultdict(dict)
    meta: dict[str, tuple[str, int]] = {}
    for path in sorted(Path(judge_dir).rglob("labels_*_judge.jsonl")):
        if path.parent.name.startswith("noise_"):
            continue
        for d in read_jsonl(path):
            if not d.get("valid", True):
                continue
            cid = d["trace_id"]
            kinds[cid][int(d["s"])] = kinds_of_sentence(d.get("labels"))
            meta[cid] = (d["prefix_id"], int(d.get("prefix_n") or 0))
    return kinds, meta


def first_indices(prefix_kinds: dict[int, set[str]], prefix_n: int, cont_kinds: dict[int, set[str]]) -> dict[str, int | None]:
    """The first sentence index of each kind in prefix (0 .. prefix_n-1) then continuation."""
    first: dict[str, int | None] = {k: None for k in KINDS}
    for s in range(prefix_n):
        for k in prefix_kinds.get(s, ()):  # the prefix's own sentences
            if first[k] is None:
                first[k] = s
    for s in sorted(cont_kinds):
        for k in cont_kinds[s]:
            if first[k] is None:
                first[k] = prefix_n + s
    return first


def pattern_of(first: dict[str, int | None]) -> str:
    present = [(i, k) for k, i in first.items() if i is not None]
    if not present:
        return "(none)"
    return " --> ".join(KIND_TITLE[k] for _, k in sorted(present))


def answers_of_run(run_dir: Path, scoring: str) -> dict[str, dict]:
    """{continuation id: {answer, cut, trace_arm, block, condition}} under the chosen reading."""
    out = {}
    for r in read_jsonl(Path(run_dir) / "continuations.jsonl"):
        if scoring == "registered":
            letters = r.get("letters_v1") if "letters_v1" in r else (r.get("letters") or [])
            answer = letters[0] if len(letters) == 1 else "?"
        elif scoring == "strict":
            if "cont_text" in r:
                answer = S5.strict_score(r["cont_text"], r.get("finish"), bool(r.get("think_closed")))["answer"]
            else:  # a derived folder: already rescored
                letters = r.get("letters") or []
                answer = letters[0] if len(letters) == 1 else "?"
        else:
            raise SystemExit(f"unknown scoring {scoring!r}")
        out[r["id"]] = {"answer": answer, "prefix_id": r["prefix_id"], "trace_arm": r["trace_arm"],
                        "block": r.get("block"), "condition": r["condition"]}
    return out


def cut_label(rec: dict) -> str:
    if rec["condition"] != "cut":
        return rec["condition"]
    return ("C" if rec["trace_arm"] == "c004" else "E") + f"-B{int(rec['block']):02d}"


def distribution_row(answers: list[str]) -> dict:
    n = len(answers)
    c = Counter(answers)
    row = {"n": n}
    for L in REPORT:
        k = c.get(L, 0)
        lo, hi = ST.wilson(k, n) if n else (float("nan"), float("nan"))
        row.update({f"count_{L}": k, f"p_{L}": round(k / n, 4) if n else "", f"p_{L}_low": round(lo, 4) if n else "",
                    f"p_{L}_high": round(hi, 4) if n else ""})
    row["count_unresolved"] = c.get("?", 0)
    row["count_other"] = n - row["count_unresolved"] - sum(c.get(L, 0) for L in REPORT)
    return row


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def build_rows(run_dir: Path, judge_dir: Path, scoring: str) -> dict:
    prefix_kinds = load_prefix_kinds(judge_dir)
    cont_kinds, meta = load_continuation_kinds(judge_dir)
    answers = answers_of_run(run_dir, scoring)
    rows = []
    for cid, ck in sorted(cont_kinds.items()):
        a = answers.get(cid)
        if a is None:
            continue
        prefix_id, prefix_n = meta[cid]
        pk = prefix_kinds.get(a["trace_arm"], {}) if a["trace_arm"] in prefix_kinds else {}
        first = first_indices(pk, prefix_n, ck)
        rows.append({"id": cid, "cut": cut_label(a), "prefix_id": prefix_id, "trace_arm": a["trace_arm"],
                     "condition": a["condition"], "prefix_n": prefix_n, "answer": a["answer"],
                     **{f"first_{k}": ("" if first[k] is None else first[k]) for k in KINDS},
                     "pattern": pattern_of(first)})
    return {"rows": rows, "labeled": len(rows), "scored": len(answers)}


def pooled_rows(rows: list[dict]) -> list[dict]:
    by_pattern = defaultdict(list)
    for r in rows:
        by_pattern[r["pattern"]].append(r)
    out = []
    for pattern, rs in sorted(by_pattern.items(), key=lambda kv: -len(kv[1])):
        share = Counter(r["trace_arm"] for r in rs)
        out.append({"pattern": pattern, **distribution_row([r["answer"] for r in rs]),
                    "from_c004": share.get("c004", 0), "from_e036": share.get("e036", 0), "from_cut0": share.get("shared", 0)})
    return out


def pair_rows(rows: list[dict]) -> list[dict]:
    """For each pair of kinds: the continuations where X comes first against those where Y comes first."""
    out = []
    for i, x in enumerate(KINDS):
        for y in KINDS[i + 1:]:
            for scope, rs_all in (("all", rows), ("cut-0", [r for r in rows if r["condition"] == "cut0"])):
                xy = [r for r in rs_all if r[f"first_{x}"] != "" and r[f"first_{y}"] != "" and r[f"first_{x}"] < r[f"first_{y}"]]
                yx = [r for r in rs_all if r[f"first_{x}"] != "" and r[f"first_{y}"] != "" and r[f"first_{y}"] < r[f"first_{x}"]]
                row = {"scope": scope, "first": KIND_TITLE[x], "then": KIND_TITLE[y],
                       **{f"XY_{k}": v for k, v in distribution_row([r["answer"] for r in xy]).items()},
                       **{f"YX_{k}": v for k, v in distribution_row([r["answer"] for r in yx]).items()},
                       "XY_from_c004": sum(1 for r in xy if r["trace_arm"] == "c004"),
                       "XY_from_e036": sum(1 for r in xy if r["trace_arm"] == "e036"),
                       "YX_from_c004": sum(1 for r in yx if r["trace_arm"] == "c004"),
                       "YX_from_e036": sum(1 for r in yx if r["trace_arm"] == "e036")}
                for L in REPORT:
                    k1, n1 = sum(1 for r in xy if r["answer"] == L), len(xy)
                    k2, n2 = sum(1 for r in yx if r["answer"] == L), len(yx)
                    if n1 and n2:
                        lo, hi = ST.newcombe(k1, n1, k2, n2)
                        row.update({f"diff_{L}": round(k1 / n1 - k2 / n2, 4), f"diff_{L}_low": round(lo, 4), f"diff_{L}_high": round(hi, 4)})
                    else:
                        row.update({f"diff_{L}": "", f"diff_{L}_low": "", f"diff_{L}_high": ""})
                out.append(row)
    return out


def by_cut_rows(rows: list[dict]) -> list[dict]:
    by = defaultdict(list)
    for r in rows:
        by[(r["cut"], r["pattern"])].append(r)
    out = []
    for (cut, pattern), rs in sorted(by.items()):
        out.append({"cut": cut, "pattern": pattern, **distribution_row([r["answer"] for r in rs])})
    return out


SUMMARY = """# The order of three kinds of sentence against the final answer — {run_id} — {scoring} scoring

Generated by `scripts/s6_order.py` on {stamp}. EXPLORATORY: this analysis was added after the
pre-registration (results v1, Section 8; no script produced those numbers). The answer letters are
read with the {scoring} rule. {labeled} of {scored} continuations carry judge labels and enter the
tables; unresolved answers stay in every denominator.

The three kinds are the leaves `algebra` (any level-three "algebra"), `famous problem (CRT)` and
`hedge word analysis`. For each continuation the prefix (reviewed labels of the source trace) and the
continuation (the judge's labels) are read as one sequence, and each kind is placed at its first
appearance. A kind that never appears is left out of that continuation's pattern.

## The pooled patterns

{pooled}

## The pair the abstract names

{pair}

## Where the order comes from

At every cut but cut-0 the order is inherited from the prefix, so a pooled number mixes the order
with the source trace: {caveat} The cut-0 continuations are the ones where the model chose the order
itself, with no prefix at all: {cut0}

Per-cut counts are in `order_by_cut.csv`, one row per continuation in `order_patterns.csv`.
"""


def summary_text(run_id: str, scoring: str, built: dict, pooled: list[dict], pairs: list[dict], stamp: str) -> str:
    def line(r):
        return (f"- `{r['pattern']}`: {r['n']} continuations (C {r['count_C']}, E {r['count_E']}, other {r['count_other']}, "
                f"unresolved {r['count_unresolved']}); P(C) = {r['p_C']}, P(E) = {r['p_E']}; "
                f"from C-trace cuts {r['from_c004']}, E-trace cuts {r['from_e036']}, cut-0 {r['from_cut0']}")
    top = "\n".join(line(r) for r in pooled[:6])
    af = next((r for r in pairs if r["scope"] == "all" and r["first"] == "algebra" and r["then"] == "famous problem"), None)
    pair = "(the pair does not occur)"
    caveat = "no pooled pattern was computed."
    cut0 = "no cut-0 continuation carries labels."
    if af:
        pair = (f"- `algebra --> famous problem`: {af['XY_n']} continuations, P(C) = {af['XY_p_C']} "
                f"[{af['XY_p_C_low']}, {af['XY_p_C_high']}], P(E) = {af['XY_p_E']}\n"
                f"- `famous problem --> algebra`: {af['YX_n']} continuations, P(C) = {af['YX_p_C']}, "
                f"P(E) = {af['YX_p_E']} [{af['YX_p_E_low']}, {af['YX_p_E_high']}]\n"
                f"- difference in P(C): {af['diff_C']} [{af['diff_C_low']}, {af['diff_C_high']}]; "
                f"in P(E): {af['diff_E']} [{af['diff_E_low']}, {af['diff_E_high']}]")
        caveat = (f"of the {af['XY_n']} `algebra --> famous problem` continuations {af['XY_from_c004']} come from C-trace cuts, "
                  f"and of the {af['YX_n']} `famous problem --> algebra` continuations {af['YX_from_e036']} come from E-trace cuts.")
    c0 = next((r for r in pairs if r["scope"] == "cut-0" and r["first"] == "algebra" and r["then"] == "famous problem"), None)
    if c0:
        cut0 = (f"`algebra --> famous problem` {c0['XY_n']} continuations (C {c0['XY_count_C']}, E {c0['XY_count_E']}), "
                f"`famous problem --> algebra` {c0['YX_n']} (C {c0['YX_count_C']}, E {c0['YX_count_E']}). "
                f"These are small numbers; the direction is what they show.")
    return SUMMARY.format(run_id=run_id, scoring=scoring, stamp=stamp, labeled=built["labeled"], scored=built["scored"],
                          pooled=top, pair=pair, caveat=caveat, cut0=cut0)


def run_one(run_dir: Path, judge_dir: Path, out_dir: Path, scoring: str, log=print) -> dict:
    from datetime import datetime
    out_dir.mkdir(parents=True, exist_ok=True)
    built = build_rows(run_dir, judge_dir, scoring)
    rows = built["rows"]
    pooled = pooled_rows(rows)
    pairs = pair_rows(rows)
    write_csv(out_dir / "order_patterns.csv", rows)
    write_csv(out_dir / "order_pooled.csv", pooled)
    write_csv(out_dir / "order_pairs.csv", pairs)
    write_csv(out_dir / "order_by_cut.csv", by_cut_rows(rows))
    write_csv(out_dir / "order_cut0.csv", [r for r in rows if r["condition"] == "cut0"])
    stamp = datetime.now().isoformat(timespec="minutes")
    (out_dir / "order_summary.md").write_text(summary_text(Path(run_dir).name, scoring, built, pooled, pairs, stamp), encoding="utf-8")
    log(f"{scoring}: {built['labeled']} labeled continuations, {len(pooled)} patterns -> {out_dir}")
    return {"scoring": scoring, "out": str(out_dir), "labeled": built["labeled"], "patterns": len(pooled),
            "pooled": pooled, "pairs": pairs}



# ---------------------------------------------------------------------------------------------------
# Prefix-free texts (added 2026-09-24, Kian's decision of the same day): the order of the judge's
# algebra leaf and famous-problem leaf in the 69 texts written with no prefix -- the 25 continuations
# of cut 0 of the run and the 44 earlier traces of the same prompt (runs/experiments/judge_sweep44_*),
# all labeled by the same judge -- against the completed answer.  Nothing is read from the text; the
# two events are the leaves as the judge applied them.  Supersedes the hand reading of results v2
# Section 8 and the text rule of scripts/s7_order_prefixfree.py.
# ---------------------------------------------------------------------------------------------------
SWEEP_FILE = Path(__file__).resolve().parents[1] / "archive/decided-mid-thought/runs/sweep_items_batball_2026-08-19_1623.jsonl"
SWEEP_CONDITION = "eval0_multi0"
OPTION_TEXT = {"C": "There is not enough information, but the answer is most likely $0.05", "E": "The question is not well posed"}



def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    """Fisher's exact test for [[a, b], [c, d]], two-sided as the sum of the probabilities of every table
    with the same margins whose probability is at most the observed one (the convention of scipy)."""
    from math import comb
    n1, n2, k = a + b, c + d, a + c
    if n1 == 0 or n2 == 0:
        return float("nan")
    total = comb(n1 + n2, k)
    def pr(x: int) -> float:
        return comb(n1, x) * comb(n2, k - x) / total
    p0 = pr(a)
    return sum(pr(x) for x in range(max(0, k - n2), min(k, n1) + 1) if pr(x) <= p0 * (1 + 1e-9))

def load_sweep44_kinds(judge_sweep_dir: Path) -> dict[str, dict[int, set[str]]]:
    """{trace_id: {s: kinds}} from labels_sweep44_judge.jsonl of a judge_sweep44_* run."""
    path = judge_sweep_dir / "labels_sweep44_judge.jsonl"
    kinds: dict[str, dict[int, set[str]]] = defaultdict(dict)
    for d in read_jsonl(path):
        kinds[d["trace_id"]][int(d["s"])] = kinds_of_sentence(d.get("labels"))
    return dict(kinds)


def sweep44_answers(sweep_file: Path = SWEEP_FILE) -> dict[str, str]:
    """{trace_id: 'C' | 'E' | '?'} for the 44 earlier traces, ids numbered in file order as s0_split does."""
    rows = [r for r in read_jsonl(sweep_file) if r.get("condition") == SWEEP_CONDITION]
    out = {}
    for k, r in enumerate(rows, start=1):
        chosen = r.get("chosen") or []
        out[f"s0819_{SWEEP_CONDITION.replace('_', '')}_{k:03d}"] = "C" if OPTION_TEXT["C"] in chosen else "E" if OPTION_TEXT["E"] in chosen else "?"
    return out


def order_arm(first: dict[str, int | None]) -> str:
    a, f = first.get("algebra"), first.get("famous")
    if a is None or f is None:
        return "undefined"
    return "algebra first" if a < f else "famous first" if f < a else "tie"


def prefix_free(run_dir: Path, judge_dir: Path, judge_sweep_dir: Path, out: Path, scoring: str) -> dict:
    """Write order_prefixfree_labels.csv (one row per text) and order_prefixfree_summary.md into out."""
    if out.exists():
        raise SystemExit(f"refusing to overwrite {out}")
    cont_kinds, meta = load_continuation_kinds(judge_dir)
    answers = answers_of_run(run_dir, scoring)
    rows = []
    for cid in sorted(c for c in cont_kinds if c.startswith("rb_cut0_")):
        first = first_indices({}, 0, cont_kinds[cid])
        rows.append({"id": cid, "batch": "cut0", "answer": answers[cid]["answer"], "first_algebra": first["algebra"],
                     "first_famous": first["famous"], "first_hedge": first["hedge"], "arm": order_arm(first), "pattern": pattern_of(first)})
    sweep_kinds = load_sweep44_kinds(judge_sweep_dir)
    sweep_ans = sweep44_answers()
    for tid in sorted(sweep_kinds):
        first = first_indices({}, 0, sweep_kinds[tid])
        rows.append({"id": tid, "batch": "sweep44", "answer": sweep_ans[tid], "first_algebra": first["algebra"],
                     "first_famous": first["famous"], "first_hedge": first["hedge"], "arm": order_arm(first), "pattern": pattern_of(first)})
    assert len(rows) == 69, len(rows)
    out.mkdir(parents=True)
    write_csv(out / "order_prefixfree_labels.csv", rows)

    def counts(rs):
        return {"n": len(rs), "C": sum(r["answer"] == "C" for r in rs), "E": sum(r["answer"] == "E" for r in rs),
                "?": sum(r["answer"] not in ("C", "E") for r in rs)}
    A = [r for r in rows if r["arm"] == "algebra first"]; F = [r for r in rows if r["arm"] == "famous first"]
    U = [r for r in rows if r["arm"] == "undefined"]; T = [r for r in rows if r["arm"] == "tie"]
    cA, cF, cU = counts(A), counts(F), counts(U)
    lo_a, hi_a = ST.wilson(cA["C"], cA["n"]); lo_f, hi_f = ST.wilson(cF["C"], cF["n"])
    d = cA["C"] / cA["n"] - cF["C"] / cF["n"]; dlo, dhi = ST.newcombe(cA["C"], cA["n"], cF["C"], cF["n"])
    p = fisher_two_sided(cA["C"], cA["n"] - cA["C"], cF["C"], cF["n"] - cF["C"])
    p_adverse = fisher_two_sided(cA["C"], cA["n"] - cA["C"], cF["C"] + cF["?"], cF["n"] - cF["C"] - cF["?"])
    p_undef_as_famous = fisher_two_sided(cA["C"], cA["n"] - cA["C"], cF["C"] + cU["C"], cF["n"] + cU["n"] - cF["C"] - cU["C"])
    nA, nF = cA["n"] - cA["?"], cF["n"] - cF["?"]
    p_answered = fisher_two_sided(cA["C"], nA - cA["C"], cF["C"], nF - cF["C"])
    lines = ["# Order of the judge's algebra leaf and famous-problem leaf in the 69 prefix-free texts", "",
             f"run {run_dir.name}, judge {judge_dir.name}, sweep44 judge {judge_sweep_dir.name}, scoring {scoring}", "",
             "| arm | n | C | E | ? | P(C) [Wilson 95%] |", "|---|---|---|---|---|---|",
             f"| algebra first | {cA['n']} | {cA['C']} | {cA['E']} | {cA['?']} | {cA['C']/cA['n']:.2f} [{lo_a:.2f}, {hi_a:.2f}] |",
             f"| famous problem first | {cF['n']} | {cF['C']} | {cF['E']} | {cF['?']} | {cF['C']/cF['n']:.2f} [{lo_f:.2f}, {hi_f:.2f}] |",
             f"| undefined (a leaf absent) | {cU['n']} | {cU['C']} | {cU['E']} | {cU['?']} | |",
             f"| tie | {len(T)} | | | | |", "",
             f"difference {d:+.2f} [{dlo:.2f}, {dhi:.2f}]; Fisher two-sided p = {p:.4f} (unresolved counted as not C); "
             f"most adverse assignment of the unresolved p = {p_adverse:.4f}; undefined texts counted with famous first p = {p_undef_as_famous:.4f}; "
             f"answered only {cA['C']}/{nA} vs {cF['C']}/{nF} p = {p_answered:.4f}", ""]
    for b in ("cut0", "sweep44"):
        rb = [r for r in rows if r["batch"] == b]
        Ab = counts([r for r in rb if r["arm"] == "algebra first"]); Fb = counts([r for r in rb if r["arm"] == "famous first"])
        pb = fisher_two_sided(Ab["C"], Ab["n"] - Ab["C"], Fb["C"], Fb["n"] - Fb["C"]) if Ab["n"] and Fb["n"] else float("nan")
        lines.append(f"{b}: algebra first {Ab['C']}/{Ab['n']} vs famous first {Fb['C']}/{Fb['n']}, p = {pb:.4f}")
    (out / "order_prefixfree_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return {"rows": rows}

def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="The order of three kinds of sentence against the final answer (results v1, Section 8; exploratory).")
    ap.add_argument("--run", required=True, help="the registered run folder")
    ap.add_argument("--judge", help="judge folder of the run; default: the run's newest judge_* folder")
    ap.add_argument("--out", help="output folder; default: the run folder (registered) and <run>_strict (strict)")
    ap.add_argument("--scoring", choices=("strict", "registered", "both"), default="strict")
    ap.add_argument("--prefix-free", metavar="JUDGE_SWEEP44_DIR",
                    help="instead of the pooled tables: the 69 prefix-free texts (cut-0 continuations of --run plus the 44 traces "
                         "labeled in this judge_sweep44_* folder); writes into --out, which must not exist")
    args = ap.parse_args(argv)
    run_dir = Path(args.run)
    judge = Path(args.judge) if args.judge else next(iter(sorted(run_dir.glob("judge_*"), reverse=True)), None)
    if judge is None:
        raise SystemExit(f"no judge folder under {run_dir}")
    if args.prefix_free:
        if not args.out:
            raise SystemExit("--prefix-free needs --out")
        prefix_free(run_dir, judge, Path(args.prefix_free), Path(args.out), "strict" if args.scoring == "both" else args.scoring)
        return 0
    wanted = ("registered", "strict") if args.scoring == "both" else (args.scoring,)
    results = []
    for scoring in wanted:
        if args.out:
            out = Path(args.out) if len(wanted) == 1 else Path(args.out) / scoring
        elif scoring == "strict":
            out = run_dir.parent / (run_dir.name.rstrip("/\\") + "_strict")
            if not out.exists():
                raise SystemExit(f"{out} does not exist; run scripts/s5_rescore.py first, or pass --out")
        else:
            out = run_dir
        results.append(run_one(run_dir, judge, out, scoring))
    for r in results:
        af = next((p for p in r["pairs"] if p["scope"] == "all" and p["first"] == "algebra" and p["then"] == "famous problem"), None)
        if af:
            print(f"{r['scoring']}: algebra --> famous problem: n {af['XY_n']}, P(C) {af['XY_p_C']}; "
                  f"famous problem --> algebra: n {af['YX_n']}, P(E) {af['YX_p_E']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
