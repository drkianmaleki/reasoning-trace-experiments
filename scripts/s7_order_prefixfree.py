#!/usr/bin/env python3
"""s7_order_prefixfree.py -- the order of algebra and constraint import in the 69 prefix-free texts.

Reproduces, from code, the analysis of results v2 Section 8 (2026-09-19), whose numbers were first
computed by hand: on texts written with no prefix -- the 25 continuations of cut 0 of the resampling
run and the 44 earlier traces of the same prompt -- locate in each text
  A  the first algebra sentence: a sentence that sets up, manipulates or draws a conclusion from the
     item's quantities (the two prices, their sum, the inequality, the solution set), and
  K  the first constraint import: a sentence that brings in the missing clause of the classic riddle,
     "the bat costs $1.00 more than the ball", in words or as a relation such as B = b + 1.00,
by regular expressions applied to the sentence text (no labels), and tabulate the completed answer by
order.  A tie (A and K in one sentence) is counted with the constraint-first arm in the main table and
under the other two treatments in the sensitivity block.

Inputs (all committed):
  runs/experiments/resample_blocks_2026-09-17_1759/judge_2026-09-17_2229/sentences_continuations_w00.jsonl
      sentences of the cut-0 continuations rb_cut0_000 .. 024 (s0_split numbering)
  runs/experiments/resample_blocks_2026-09-17_1759_strict/continuations.jsonl
      their answers under the corrected reading (field "answer"; "?" = unresolved)
  runs/experiments/s0_split_2026-09-16_2224/sentences_sweep44.jsonl
      sentences of the 44 earlier traces, ids s0819_eval0multi0_001 .. 044 in file order
  archive/decided-mid-thought/runs/sweep_items_batball_2026-08-19_1623.jsonl
      their answers (field "chosen"; empty = hit the token limit)
  runs/tests/t2_split_2026-09-16_2224/sentences_source.jsonl
      the two source traces, to report their own A and K

Usage:  python scripts/s7_order_prefixfree.py [--out runs/experiments/order_prefixfree_<date>_<hhmm>/]
Writes per_text.csv, summary.md, numbers.json into the run folder.  Never overwrites an existing folder.
"""
from __future__ import annotations
import argparse, csv, json, re, sys
from datetime import datetime
from math import comb, sqrt
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[1] if HERE.parent.name == "scripts" else HERE.parents[2]
RUN = REPO / "runs/experiments/resample_blocks_2026-09-17_1759"
F_CUT0_SENT = RUN / "judge_2026-09-17_2229/sentences_continuations_w00.jsonl"
F_CUT0_ANS = REPO / "runs/experiments/resample_blocks_2026-09-17_1759_strict/continuations.jsonl"
F_SWEEP_SENT = REPO / "runs/experiments/s0_split_2026-09-16_2224/sentences_sweep44.jsonl"
F_SWEEP_ANS = REPO / "archive/decided-mid-thought/runs/sweep_items_batball_2026-08-19_1623.jsonl"
F_SOURCE_SENT = REPO / "runs/tests/t2_split_2026-09-16_2224/sentences_source.jsonl"
SOURCE_SAMPLES = {2: "c004", 40: "e036"}          # sample field of the sweep -> source trace id
OPTION_C = "There is not enough information, but the answer is most likely $0.05"
OPTION_E = "The question is not well posed"

# ------------------------------------------------------------------ the two rules
ONE = r"\$?\s*1(?:\.0{1,2})?(?![\d.])"            # 1, 1.0, 1.00, $1, $1.00 -- not 1.10, 1.05 or 10
K_PATTERNS = [
    ONE + r"\s*(?:dollars?)?\s+more\b",                        # $1.00 more (than), 1 dollar more
    r"\b(?:one|a)\s+dollar\s+more\b",
    r"\bmore\s+(?:than\s+the\s+ball\s+)?by\s+" + ONE,          # more than the ball by $1
    r"\bby\s+(?:exactly\s+)?(?:" + ONE + r"|one\s+dollar|a\s+dollar)\b",   # exceeds the ball by $1
    r"(?:\bx|\by|\bb|\bB|\bball|\bBall|\bprice)\s*\+\s*" + ONE,  # x + 1.00, ball + 1: the relation, not the sum of two prices
    ONE + r"\s*\+\s*(?:x\b|y\b|b\b|B\b|ball\b|Ball\b)",          # 1.00 + x
    r"\bdiffer(?:ence|s|ent)?\b[^.]{0,25}?" + ONE,             # difference of $1 / differ by 1.00
    ONE + r"\s+(?:dollar\s+)?(?:difference|apart|gap)\b",
]
NUM = r"\$?\s*\d+(?:\.\d+)?(?:\s*cents?)?"
VAR = r"(?:\bx\b|\by\b|\bb\b|\bB\b|\bbat\b|\bball\b|\bBat\b|\bBall\b|\btotal\b|\bsum\b)"
OPND = rf"(?:{NUM}|{VAR})[)\]\"']*"                     # an operand may close a bracket or quote before the operator
A_PATTERNS = [
    rf"{OPND}\s*(?:=|≠|<|>|≤|≥|<=|>=|\+|×|\*|/)\s*[(\[]*{OPND}",   # x + y = 1.10, bat > ball, (B) + (b) = 1.10
    rf"{OPND}\s+(?:-|−|–)\s+{OPND}",                          # 1.10 - 0.05 (spaced minus; a hyphen inside a word is not one)
    rf"{NUM}\s*(?:-|−)\s*{NUM}",                              # 1.10-0.55
    r"\b(?:less|lower|smaller|cheaper)\s+than\s+(?:\$?\s*0?\.55|55\s*cents|half)",
    r"\b(?:below|under|at\s+most|up\s+to|no\s+more\s+than|not\s+exceed(?:ing)?)\s+(?:\$?\s*0?\.55|55\s*cents)",
    r"\bbetween\s+(?:\$?\s*0(?:\.00)?|zero)\s+and\s+(?:\$?\s*0?\.55|55\s*cents)",
    r"\bhalf\s+of\s+(?:the\s+total|\$?\s*1\.10)",
    r"\b(?:any|anything|infinitely\s+many|a\s+range\s+of)\b[^.;]{0,50}\b(?:values?|prices?|amounts?|solutions?|numbers?)\b",
    r"\b(?:0?\.55|55\s*cents)\b",                              # the bound of the solution set, named
]
K_RE = [re.compile(p, re.I) for p in K_PATTERNS]
A_RE = [re.compile(p, re.I) for p in A_PATTERNS]

def clean(s: str) -> str:
    """Strip LaTeX dollar delimiters, markdown emphasis, backticks and backslashes, so that "$x$",
    "**Bat**" and "\\$1.00" read as x, Bat and $1.00.  The K rules see the price sign: a dollar
    sign directly before a digit is kept."""
    s = re.sub(r"\\\$", "$", s)                    # \$ -> $
    s = re.sub(r"\$(?!\s*\d)", "", s)                # $ not before a number (LaTeX math delimiter) -> removed
    return re.sub(r"[*`\\]", "", s)
def is_K(s: str) -> bool: s = clean(s); return any(r.search(s) for r in K_RE)
def is_A(s: str) -> bool: s = clean(s); return any(r.search(s) for r in A_RE)

# ------------------------------------------------------------------ inputs
def read_jsonl(p: Path):
    with open(p, encoding="utf-8") as fh:
        for line in fh:
            if line.strip(): yield json.loads(line)

def sentences_by_trace(p: Path, keep=lambda tid: True) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for d in read_jsonl(p):
        if keep(d["trace_id"]): out.setdefault(d["trace_id"], []).append((int(d["s"]), d["text"]))
    return {k: [t for _, t in sorted(v)] for k, v in out.items()}

def cut0_answers() -> dict[str, str]:
    out = {}
    for d in read_jsonl(F_CUT0_ANS):
        if str(d.get("id", "")).startswith("rb_cut0_"):
            a = d.get("answer"); out[d["id"]] = a if a in ("C", "E") else ("?" if a in (None, "", "?") else a)
    return out

def sweep_answers() -> tuple[dict[str, str], dict[str, str]]:
    """{trace_id: answer}, {trace_id: source id if it is a source trace}"""
    rows = [r for r in read_jsonl(F_SWEEP_ANS) if r.get("condition") == "eval0_multi0"]
    ans, src = {}, {}
    for k, r in enumerate(rows, start=1):
        tid = f"s0819_eval0multi0_{k:03d}"
        ch = r.get("chosen") or []
        ans[tid] = "C" if OPTION_C in ch else "E" if OPTION_E in ch else ("?" if not ch else "other")
        if r.get("sample") in SOURCE_SAMPLES: src[tid] = SOURCE_SAMPLES[r["sample"]]
    return ans, src

# ------------------------------------------------------------------ locate and classify
def locate(sents: list[str]) -> dict:
    a = next((i for i, s in enumerate(sents) if is_A(s)), None)
    k = next((i for i, s in enumerate(sents) if is_K(s)), None)
    if a is None or k is None: pat = "missing"
    elif a == k: pat = "tie"
    elif a < k: pat = "A first"
    else: pat = "K first"
    return {"first_A": a, "first_K": k, "A_text": sents[a] if a is not None else "", "K_text": sents[k] if k is not None else "", "pattern": pat}

# ------------------------------------------------------------------ statistics
def wilson(x, n, z=1.959964):
    if n == 0: return (float("nan"), float("nan"))
    ph = x / n; d = 1 + z * z / n; c = ph + z * z / (2 * n); r = z * sqrt(ph * (1 - ph) / n + z * z / (4 * n * n))
    return ((c - r) / d, (c + r) / d)
def newcombe(x1, n1, x2, n2):
    l1, u1 = wilson(x1, n1); l2, u2 = wilson(x2, n2); p1, p2 = x1 / n1, x2 / n2; d = p1 - p2
    return (d, d - sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2))
def fisher(a, b, c, d):
    """two-sided Fisher exact p for [[a, b], [c, d]] (sum of tables with probability <= the observed)"""
    n1, n2, k = a + b, c + d, a + c
    def pr(x): return comb(n1, x) * comb(n2, k - x) / comb(n1 + n2, k)
    p0 = pr(a); lo, hi = max(0, k - n2), min(k, n1)
    return sum(pr(x) for x in range(lo, hi + 1) if pr(x) <= p0 * (1 + 1e-9))

def arm_stats(texts: list[dict], arm_of) -> dict:
    """texts: rows with pattern and answer.  arm_of(row) -> 'A' | 'K' | None"""
    arms = {"A": [], "K": []}
    for r in texts:
        a = arm_of(r)
        if a: arms[a].append(r["answer"])
    def cnt(v): return {"n": len(v), "C": v.count("C"), "E": v.count("E"), "?": v.count("?"), "other": sum(1 for x in v if x not in ("C", "E", "?"))}
    A, K = cnt(arms["A"]), cnt(arms["K"])
    out = {"A": A, "K": K}
    if A["n"] and K["n"]:
        out["pC_A"] = A["C"] / A["n"]; out["pC_K"] = K["C"] / K["n"]
        out["wilson_A"] = wilson(A["C"], A["n"]); out["wilson_K"] = wilson(K["C"], K["n"])
        out["diff_newcombe"] = newcombe(A["C"], A["n"], K["C"], K["n"])
        out["fisher_unresolved_notC"] = fisher(A["C"], A["n"] - A["C"], K["C"], K["n"] - K["C"])
        # most adverse assignment of the unresolved: A's unresolved count as not C (already), K's unresolved as C
        out["fisher_adverse"] = fisher(A["C"], A["n"] - A["C"], K["C"] + K["?"], K["n"] - K["C"] - K["?"])
        nA, nK = A["n"] - A["?"], K["n"] - K["?"]
        out["answered_only"] = {"A": (A["C"], nA), "K": (K["C"], nK), "fisher": fisher(A["C"], nA - A["C"], K["C"], nK - K["C"]) if nA and nK else None,
                                "diff_newcombe": newcombe(A["C"], nA, K["C"], nK) if nA and nK else None}
    return out

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out"); args = ap.parse_args(argv)
    out = Path(args.out) if args.out else REPO / "runs/experiments" / f"order_prefixfree_{datetime.now():%Y-%m-%d_%H%M}"
    if out.exists(): sys.exit(f"refusing to overwrite {out}")
    cut0 = sentences_by_trace(F_CUT0_SENT, lambda t: t.startswith("rb_cut0_"))
    sweep = sentences_by_trace(F_SWEEP_SENT)
    a0 = cut0_answers(); a44, src = sweep_answers()
    assert len(cut0) == 25 and len(sweep) == 44, (len(cut0), len(sweep))
    rows = []
    for tid, sents in sorted(cut0.items()):
        r = locate(sents); r.update({"id": tid, "batch": "cut0", "answer": a0[tid], "n_sentences": len(sents), "source_trace": ""}); rows.append(r)
    for tid, sents in sorted(sweep.items()):
        r = locate(sents); r.update({"id": tid, "batch": "sweep44", "answer": a44[tid], "n_sentences": len(sents), "source_trace": src.get(tid, "")}); rows.append(r)
    # the two source traces, in the paper's sentence numbering
    source = sentences_by_trace(F_SOURCE_SENT)
    src_rows = {tid: locate(sents) for tid, sents in source.items()}

    def arm_ties_K(r): return "A" if r["pattern"] == "A first" else "K" if r["pattern"] in ("K first", "tie") else None
    def arm_ties_A(r): return "A" if r["pattern"] in ("A first", "tie") else "K" if r["pattern"] == "K first" else None
    def arm_ties_out(r): return "A" if r["pattern"] == "A first" else "K" if r["pattern"] == "K first" else None
    numbers = {
        "n_texts": len(rows), "patterns": {p: sum(1 for r in rows if r["pattern"] == p) for p in ("A first", "K first", "tie", "missing")},
        "main_ties_with_K": arm_stats(rows, arm_ties_K),
        "ties_with_A": arm_stats(rows, arm_ties_A),
        "ties_excluded": arm_stats(rows, arm_ties_out),
        "batch_cut0": arm_stats([r for r in rows if r["batch"] == "cut0"], arm_ties_K),
        "batch_sweep44": arm_stats([r for r in rows if r["batch"] == "sweep44"], arm_ties_K),
        "without_source_traces": arm_stats([r for r in rows if not r["source_trace"]], arm_ties_K),
        "source_traces": {tid: {k: v for k, v in d.items() if k != "A_text" and k != "K_text"} | {"A_text": d["A_text"][:120], "K_text": d["K_text"][:120]} for tid, d in src_rows.items()},
    }
    out.mkdir(parents=True)
    with open(out / "per_text.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "batch", "source_trace", "answer", "n_sentences", "first_A", "first_K", "pattern", "A_text", "K_text"])
        w.writeheader(); w.writerows(rows)
    with open(out / "numbers.json", "w", encoding="utf-8") as fh: json.dump(numbers, fh, indent=1, default=str)
    m = numbers["main_ties_with_K"]
    lines = ["# Order of algebra (A) and constraint import (K) in the 69 prefix-free texts", "",
             f"patterns: {numbers['patterns']}", "",
             "| arm | n | C | E | ? | P(C) [Wilson 95%] |", "|---|---|---|---|---|---|"]
    for name, key in (("A first", "A"), ("K first, ties included", "K")):
        c = m[key]; lo, hi = m["wilson_" + key]
        lines.append(f"| {name} | {c['n']} | {c['C']} | {c['E']} | {c['?']} | {c['C']/c['n']:.2f} [{lo:.2f}, {hi:.2f}] |")
    d = m["diff_newcombe"]
    lines += ["", f"difference {d[0]:+.2f} [{d[1]:.2f}, {d[2]:.2f}]; Fisher (unresolved as not C) p = {m['fisher_unresolved_notC']:.4f}; "
              f"most adverse assignment of the unresolved p = {m['fisher_adverse']:.4f}; answered only {m['answered_only']['A']} vs {m['answered_only']['K']} p = {m['answered_only']['fisher']:.4f}", "",
              "sensitivity: ties with A first " + json.dumps({k: numbers['ties_with_A'][k] for k in ('A', 'K')}) + f" p = {numbers['ties_with_A'].get('fisher_unresolved_notC', float('nan')):.4f}",
              "ties excluded " + json.dumps({k: numbers['ties_excluded'][k] for k in ('A', 'K')}) + f" p = {numbers['ties_excluded'].get('fisher_unresolved_notC', float('nan')):.4f}",
              "cut0 only " + json.dumps({k: numbers['batch_cut0'][k] for k in ('A', 'K')}) + f" p = {numbers['batch_cut0'].get('fisher_unresolved_notC', float('nan')):.4f}",
              "sweep44 only " + json.dumps({k: numbers['batch_sweep44'][k] for k in ('A', 'K')}) + f" p = {numbers['batch_sweep44'].get('fisher_unresolved_notC', float('nan')):.4f}",
              "without the two source traces " + json.dumps({k: numbers['without_source_traces'][k] for k in ('A', 'K')}) + f" p = {numbers['without_source_traces'].get('fisher_unresolved_notC', float('nan')):.4f}",
              "", "source traces: " + json.dumps(numbers["source_traces"], default=str)]
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines)); print(f"\nwrote {out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
