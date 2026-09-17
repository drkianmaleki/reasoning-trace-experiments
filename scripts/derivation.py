#!/usr/bin/env python3
"""derivation.py -- from sentence labels to nodes and blocks (pipeline v2, step 4d/9; labeling
scheme v6, Sections 0a, 6a, 6b; rule R4 added 2026-09-17).  Offline, standard library only.

Input: one trace's labels, one entry per sentence, each entry a list of one or two paths
"Level 1 > Level 2 [> Level 3]".  A sentence with two paths is a combined sentence.  Since R4
the derivation also takes the sentence texts (optional; without them the pre-R4 derivation of
scheme v5 is reproduced).

Openers (block starts), exactly as specified for the pipeline:
- sentence 0 always opens (rule "S0" is recorded when no other rule applies to it);
- R1: the first sentence of every maximal run of consecutive single-path Planning sentences
  that contains at least one path other than "Planning > local plan" (a run of local plans
  opens nothing; a combined sentence is never part of such a run);
- a combined sentence opens if one of its paths is a Planning path other than local plan (R1),
  an "Assumption > branching" path (R2) or a "Conclusion > final answer" path (R3);
- R2/R3: a single-path sentence whose path starts with "Assumption > branching" or
  "Conclusion > final answer" opens unless the previous sentence is a single-path sentence
  with the same Level 1 and Level 2;
- R4 (scheme v6, Section 6b; pipeline v2, decision 20): a sentence whose text, after leading
  whitespace, line-break marks, list markers, markdown, digits with dots and parentheses,
  begins with the word "Wait" -- optionally preceded by "But", "And", "Oh" or "Okay" -- opens a
  block whatever its labels and whatever precedes it (R4_RE below).  R4 is recorded as the
  opener rule even where R1 would also apply.  The R1 run computation is unchanged by R4: an R4
  sentence inside a Planning run adds an opener and thereby ends the node before it.
Blocks run from an opener to the sentence before the next opener; the last block to the end.
Nodes inside a block: maximal runs of consecutive non-combined sentences with the same Level 1;
every combined sentence is a node of its own; a block boundary ends a node.
Names: abbreviation (Pl Re Rf Kn Rs As Ex Co; "[Re+As]" for a combined node, in path order),
subscript block number, superscript ordinal among nodes with the same abbreviation in the
block only when there is more than one, and the sentence count in parentheses only when it is
greater than one: Pl₀(3), Rs₁, Re₃(7), Pl₀¹(4), [Re+As]₂.  Plain form: Pl_0(3), Pl_0^1(4).

Label enforcement for R4 sentences (apply_r4_labels; judge labels only, never the reviewed
ones, which already carry the leaf): a path Planning > initiate verification or > initiate
backtracking gets the Level 3 leaf "Wait (doubt marker)"; otherwise the path
Planning > initiate verification > Wait (doubt marker) is added as the first path, making the
sentence combined (the scheme's C s42 case).  Two resolutions keep the two-path cap: a Planning
path of another leaf is replaced by the R4 path; a sentence that already carries two
non-Planning paths keeps its first path as the content half and drops the second.  The R4 path
is placed first in every case (the listing's order for C s42 and E s19).

parse_listing() reads the reviewed listing (docs/shared/2026-09-17_source_traces_labeled_v4.md):
labels, expected node names, sentence texts and the block headers.  NOTE: the listing writes
the sentence count also when it is 1 ("Rs₁(1)"); the gate strips that "(1)" before comparing.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LISTING = REPO / "docs" / "shared" / "2026-09-17_source_traces_labeled_v4.md"
LISTING_V3 = REPO / "archive" / "docs" / "shared" / "2026-09-16_source_traces_labeled_v3.md"  # pre-R4, read only
SENTENCES_SOURCE = REPO / "runs" / "tests" / "t2_split_2026-09-16_2224" / "sentences_source.jsonl"

L1_ABBR = {"Planning": "Pl", "Reasoning": "Re", "Reflection": "Rf", "Knowledge": "Kn",
           "Restatement": "Rs", "Assumption": "As", "Example": "Ex", "Conclusion": "Co"}
L1_ORDER = list(L1_ABBR)
LOCAL_PLAN = "Planning > local plan"
BRANCHING = "Assumption > branching"
FINAL = "Conclusion > final answer"
WAIT_LEAF = "Wait (doubt marker)"
R4_VERIFY = "Planning > initiate verification"
R4_BACKTRACK = "Planning > initiate backtracking"
R4_PATH = f"{R4_VERIFY} > {WAIT_LEAF}"
# Rule R4: leading whitespace, ⏎ marks, list markers, markdown (* _ # >), digits with dots and
# parentheses, then an optional "But"/"And"/"Oh,"/"Okay," and the whole word "Wait", any case.
R4_RE = re.compile(r"^[\s\u23ce*_#>\d.)(-]*(?:but\s+|and\s+|oh,?\s+|okay,?\s+)?wait\b", re.IGNORECASE)
SUB = str.maketrans("0123456789", "\u2080\u2081\u2082\u2083\u2084\u2085\u2086\u2087\u2088\u2089")
SUP = str.maketrans("0123456789", "\u2070\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078\u2079")


# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------

def split_path(path: str) -> list[str]:
    return [p.strip() for p in path.split(" > ")]


def level1(path: str) -> str:
    return split_path(path)[0]


def level12(path: str) -> str:
    return " > ".join(split_path(path)[:2])


def is_planning(path: str) -> bool:
    return level1(path) == "Planning"


def is_nonlocal_planning(path: str) -> bool:
    return is_planning(path) and path != LOCAL_PLAN


def is_branching(path: str) -> bool:
    return path == BRANCHING or path.startswith(BRANCHING + " ")


def is_final(path: str) -> bool:
    return path == FINAL or path.startswith(FINAL + " ")


def abbreviation(paths: list[str]) -> str:
    abbrs = [L1_ABBR[level1(p)] for p in paths]
    return abbrs[0] if len(abbrs) == 1 else "[" + "+".join(abbrs) + "]"


def node_level1(node: dict) -> str:
    """The Level 1 label a node is counted under: a combined node under its first path."""
    return node["L1"].split(" + ")[0]


# ----------------------------------------------------------------------------
# Rule R4: the sentence text
# ----------------------------------------------------------------------------

def is_r4(text: str) -> bool:
    return bool(R4_RE.match(text or ""))


def r4_flags(n: int, texts: list[str] | None) -> list[bool]:
    if texts is None:
        return [False] * n
    if len(texts) != n:
        raise ValueError(f"{len(texts)} texts for {n} labels")
    return [is_r4(t) for t in texts]


def apply_r4_labels(labels: list[list[str]], texts: list[str]) -> tuple[list[list[str]], list[dict | None]]:
    """Label enforcement for R4 sentences (judge labels).  Returns (new labels, notes): notes[i]
    is None for a sentence that is not an R4 sentence, else {"action", "changed", "before"}."""
    flags = r4_flags(len(labels), texts)
    out: list[list[str]] = []
    notes: list[dict | None] = []
    for i, paths in enumerate(labels):
        if not flags[i]:
            out.append(list(paths))
            notes.append(None)
            continue
        before = list(paths)
        new = list(paths)
        idx = next((k for k, p in enumerate(new) if level12(p) in (R4_VERIFY, R4_BACKTRACK)), None)
        if idx is not None:
            r4_path = f"{level12(new[idx])} > {WAIT_LEAF}"
            new = [r4_path] + [p for k, p in enumerate(new) if k != idx]
            action = "set_level3"
        else:
            pidx = next((k for k, p in enumerate(new) if is_planning(p)), None)
            if pidx is not None:
                new = [R4_PATH] + [p for k, p in enumerate(new) if k != pidx]
                action = "planning_leaf_replaced"
            elif len(new) == 1:
                new = [R4_PATH, new[0]]
                action = "prepended"
            else:
                new = [R4_PATH, new[0]]
                action = "prepended_second_dropped"
        out.append(new)
        notes.append({"action": action, "changed": new != before, "before": before})
    return out, notes


# ----------------------------------------------------------------------------
# Openers and blocks
# ----------------------------------------------------------------------------

def openers(labels: list[list[str]], texts: list[str] | None = None) -> list[tuple[int, str]]:
    """[(sentence index, rule)] in increasing order; sentence 0 is always included."""
    n = len(labels)
    flags = r4_flags(n, texts)
    rule: dict[int, str] = {i: "R4" for i in range(n) if flags[i]}

    def single_planning(i: int) -> bool:
        return len(labels[i]) == 1 and is_planning(labels[i][0])

    i = 0
    while i < n:
        if single_planning(i):
            j = i
            while j + 1 < n and single_planning(j + 1):
                j += 1
            if any(labels[k][0] != LOCAL_PLAN for k in range(i, j + 1)):
                rule.setdefault(i, "R1")
            i = j + 1
            continue
        paths = labels[i]
        if len(paths) == 2:
            if any(is_nonlocal_planning(p) for p in paths):
                rule.setdefault(i, "R1")
            elif any(is_branching(p) for p in paths):
                rule.setdefault(i, "R2")
            elif any(is_final(p) for p in paths):
                rule.setdefault(i, "R3")
        elif is_branching(paths[0]) or is_final(paths[0]):
            prev_same = (i > 0 and len(labels[i - 1]) == 1
                         and level12(labels[i - 1][0]) == level12(paths[0]))
            if not prev_same:
                rule.setdefault(i, "R2" if is_branching(paths[0]) else "R3")
        i += 1
    if n and 0 not in rule:
        rule[0] = "S0"
    return sorted(rule.items())


def blocks_from_openers(ops: list[tuple[int, str]], n: int) -> list[tuple[int, int, int, str]]:
    """[(m, s_start, s_end, rule)]"""
    out = []
    for m, (start, r) in enumerate(ops):
        end = ops[m + 1][0] - 1 if m + 1 < len(ops) else n - 1
        out.append((m, start, end, r))
    return out


# ----------------------------------------------------------------------------
# Nodes and names
# ----------------------------------------------------------------------------

def node_name(abbr: str, block: int, ordinal: int | None, count: int) -> tuple[str, str]:
    """(display, plain): Pl₀(3) / Pl_0(3); Pl₀¹(4) / Pl_0^1(4); Rs₁ / Rs_1."""
    disp = abbr + str(block).translate(SUB)
    plain = f"{abbr}_{block}"
    if ordinal is not None:
        disp += str(ordinal).translate(SUP)
        plain += f"^{ordinal}"
    if count > 1:
        disp += f"({count})"
        plain += f"({count})"
    return disp, plain


def derive(labels: list[list[str]], trace_id: str, label_source: str, texts: list[str] | None = None) -> dict:
    """The pipeline's blocks record (Section 3 item 6) plus a per-sentence name list.  With
    `texts`, rule R4 applies (the labels are used as given: enforce them first with
    apply_r4_labels when they come from the judge)."""
    for i, paths in enumerate(labels):
        if not 1 <= len(paths) <= 2:
            raise ValueError(f"sentence {i}: {len(paths)} paths; expected one or two")
        for p in paths:
            if level1(p) not in L1_ABBR:
                raise ValueError(f"sentence {i}: unknown Level 1 in {p!r}")
    n = len(labels)
    ops = openers(labels, texts)
    blocks = blocks_from_openers(ops, n)
    nodes: list[dict] = []
    sentence_names: list[str] = [""] * n
    block_records = []
    for m, start, end, r in blocks:
        # nodes of this block
        raw: list[tuple[str, int, int, list[str]]] = []  # (abbr, s_start, s_end, paths)
        i = start
        while i <= end:
            paths = labels[i]
            if len(paths) == 2:
                raw.append((abbreviation(paths), i, i, paths))
                i += 1
                continue
            l1 = level1(paths[0])
            j = i
            while j + 1 <= end and len(labels[j + 1]) == 1 and level1(labels[j + 1][0]) == l1:
                j += 1
            raw.append((L1_ABBR[l1], i, j, paths))
            i = j + 1
        per_abbr: dict[str, int] = {}
        for abbr, *_ in raw:
            per_abbr[abbr] = per_abbr.get(abbr, 0) + 1
        seen: dict[str, int] = {}
        for abbr, s_start, s_end, paths in raw:
            seen[abbr] = seen.get(abbr, 0) + 1
            ordinal = seen[abbr] if per_abbr[abbr] > 1 else None
            disp, plain = node_name(abbr, m, ordinal, s_end - s_start + 1)
            l1 = level1(paths[0]) if len(paths) == 1 else " + ".join(level1(p) for p in paths)
            nodes.append({"name": disp, "name_plain": plain, "L1": l1, "s_start": s_start,
                          "s_end": s_end, "n": s_end - s_start + 1, "block": m})
            for s in range(s_start, s_end + 1):
                sentence_names[s] = disp
        block_records.append({"m": m, "s_start": start, "s_end": end, "opener_rule": r,
                              "opener_label": " || ".join(labels[start]), "tokens": None})
    return {"trace_id": trace_id, "label_source": label_source, "nodes": nodes,
            "blocks": block_records, "sentence_names": sentence_names, "r4": texts is not None}


# ----------------------------------------------------------------------------
# The reviewed listing and the sentence file
# ----------------------------------------------------------------------------

ROW = re.compile(r"^\| s(\d+)\(new\)-s(\d+)\(old(?:, part (\d))?\) \| (.*?) \| (.*) \|\s*$")
# The node name closes the Node column; a fragment after it (listing v4, E s19: a stray
# "|\| Reasoning > comparison > prompt vs original text" left from the pre-R4 row) is tolerated
# and recorded under "defects" so that the document can be corrected.
NAME = re.compile(r" \((\[?[A-Z][a-z](?:\+[A-Z][a-z])?\]?[\u2080-\u2089]+[\u00b9\u00b2\u00b3\u2070-\u2079]*(?:\(\d+\))?)\)(?=$| \|)")
SEP = re.compile(r" \\?\|\\?\| ")
BLOCK = re.compile(r"^\| ([CE])-B(\d+) \| \[s(\d+), s(\d+)\] \| (\d+) \| (\d+) \| (R[1234]): (.*) \|\s*$")


def normalize_listing_name(name: str) -> str:
    """The listing writes the count also when it is 1 (Rs₁(1)); the scheme omits it."""
    return name[:-3] if name.endswith("(1)") else name


def parse_listing(path: Path | str = LISTING) -> dict[str, dict]:
    """{trace_id: {labels, names (as written), texts, old_s, blocks [(m, s_start, s_end, rule, label)]}}"""
    out = {"c004": {"labels": [], "names": [], "texts": [], "old_s": [], "blocks": [], "defects": []},
           "e036": {"labels": [], "names": [], "texts": [], "old_s": [], "blocks": [], "defects": []}}
    trace = None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("## C-trace"):
                trace = "c004"
            elif line.startswith("## E-trace"):
                trace = "e036"
            elif line.startswith("## "):
                trace = None
            if not trace:
                continue
            b = BLOCK.match(line)
            if b:
                out[trace]["blocks"].append((int(b.group(2)), int(b.group(3)), int(b.group(4)),
                                             b.group(7), b.group(8).replace("\\|\\|", "||")))
                continue
            m = ROW.match(line)
            if not m:
                continue
            s = int(m.group(1))
            if s != len(out[trace]["labels"]):
                raise ValueError(f"{trace}: row s{s} out of order")
            node_col = m.group(4)
            nm = NAME.search(node_col)
            if not nm:
                raise ValueError(f"{trace} s{s}: no node name in {node_col!r}")
            paths = [p.strip() for p in SEP.split(node_col[:nm.start()])]
            trailing = node_col[nm.end():]
            if trailing.strip():
                out[trace]["defects"].append({"s": s, "fragment_after_node_name": trailing.strip()})
            out[trace]["labels"].append(paths)
            out[trace]["names"].append(nm.group(1))
            out[trace]["texts"].append(m.group(5).replace("\\|", "|"))
            out[trace]["old_s"].append(int(m.group(2)))
    return out


def load_sentence_texts(path: Path | str = SENTENCES_SOURCE) -> dict[str, list[str]]:
    """{trace_id: [text, ...]} from a sentences_<collection>.jsonl file, in sentence order."""
    out: dict[str, list[str]] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                out.setdefault(r["trace_id"], []).append(r["text"])
    return out


def gate(trace_id: str, labels: list[list[str]], expected: dict, texts: list[str] | None = None,
         label_source: str = "reviewed_v4") -> dict:
    """Compare derive(labels[, texts]) with the listing's blocks and names.  Returns the numbers
    and every difference; 'pass' is True only with zero differences."""
    rec = derive(labels, trace_id, label_source, texts)
    exp_blocks = [(m, a, b) for m, a, b, _, _ in expected["blocks"]]
    got_blocks = [(bl["m"], bl["s_start"], bl["s_end"]) for bl in rec["blocks"]]
    block_diffs = []
    for k in range(max(len(exp_blocks), len(got_blocks))):
        e = exp_blocks[k] if k < len(exp_blocks) else None
        g = got_blocks[k] if k < len(got_blocks) else None
        if e != g:
            block_diffs.append({"m": k, "expected": e, "derived": g})
    rule_diffs = []
    for (m, a, b, r, lab), bl in zip(expected["blocks"], rec["blocks"]):
        if r != bl["opener_rule"] or lab != bl["opener_label"]:
            rule_diffs.append({"m": m, "expected": f"{r}: {lab}", "derived": f"{bl['opener_rule']}: {bl['opener_label']}"})
    exp_names = [normalize_listing_name(x) for x in expected["names"]]
    name_diffs = [{"s": s, "expected": e, "derived": g}
                  for s, (e, g) in enumerate(zip(exp_names, rec["sentence_names"])) if e != g]
    n_nodes_expected = len(dict.fromkeys(expected["names"]))
    result = {
        "trace_id": trace_id, "r4": texts is not None,
        "blocks_expected": len(exp_blocks), "blocks_derived": len(got_blocks),
        "nodes_expected": n_nodes_expected, "nodes_derived": len(rec["nodes"]),
        "sentences": len(labels),
        "names_normalized": sum(1 for x in expected["names"] if x.endswith("(1)")),
        "r4_openers": [bl["s_start"] for bl in rec["blocks"] if bl["opener_rule"] == "R4"],
        "block_diffs": block_diffs, "rule_diffs": rule_diffs, "name_diffs": name_diffs,
    }
    result["pass"] = (not block_diffs and not rule_diffs and not name_diffs
                      and len(exp_blocks) == len(got_blocks) and n_nodes_expected == len(rec["nodes"]))
    return result
