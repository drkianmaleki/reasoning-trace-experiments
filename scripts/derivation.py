#!/usr/bin/env python3
"""derivation.py -- from sentence labels to nodes and blocks (pipeline v1, step 4d/9; labeling
scheme v5, Sections 0a, 6a, 6b).  Offline, standard library only.

Input: one trace's labels, one entry per sentence, each entry a list of one or two paths
"Level 1 > Level 2 [> Level 3]".  A sentence with two paths is a combined sentence.

Openers (block starts), exactly as specified for the pipeline:
- sentence 0 always opens (rule "S0" is recorded when no other rule applies to it);
- R1: the first sentence of every maximal run of consecutive single-path Planning sentences
  that contains at least one path other than "Planning > local plan" (a run of local plans
  opens nothing; a combined sentence is never part of such a run);
- a combined sentence opens if one of its paths is a Planning path other than local plan (R1),
  an "Assumption > branching" path (R2) or a "Conclusion > final answer" path (R3);
- R2/R3: a single-path sentence whose path starts with "Assumption > branching" or
  "Conclusion > final answer" opens unless the previous sentence is a single-path sentence
  with the same Level 1 and Level 2.
Blocks run from an opener to the sentence before the next opener; the last block to the end.
Nodes inside a block: maximal runs of consecutive non-combined sentences with the same Level 1;
every combined sentence is a node of its own; a block boundary ends a node.
Names: abbreviation (Pl Re Rf Kn Rs As Ex Co; "[Re+As]" for a combined node, in path order),
subscript block number, superscript ordinal among nodes with the same abbreviation in the
block only when there is more than one, and the sentence count in parentheses only when it is
greater than one: Pl₀(3), Rs₁, Re₃(7), Pl₀¹(4), [Re+As]₂.  Plain form: Pl_0(3), Pl_0^1(4).

parse_listing() reads the reviewed listing (docs/shared/2026-09-16_source_traces_labeled_v3.md):
labels, expected node names, sentence texts and the block headers.  NOTE: the listing writes
the sentence count also when it is 1 ("Rs₁(1)"); the gate strips that "(1)" before comparing.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LISTING = REPO / "docs" / "shared" / "2026-09-16_source_traces_labeled_v3.md"

L1_ABBR = {"Planning": "Pl", "Reasoning": "Re", "Reflection": "Rf", "Knowledge": "Kn",
           "Restatement": "Rs", "Assumption": "As", "Example": "Ex", "Conclusion": "Co"}
LOCAL_PLAN = "Planning > local plan"
BRANCHING = "Assumption > branching"
FINAL = "Conclusion > final answer"
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


# ----------------------------------------------------------------------------
# Openers and blocks
# ----------------------------------------------------------------------------

def openers(labels: list[list[str]]) -> list[tuple[int, str]]:
    """[(sentence index, rule)] in increasing order; sentence 0 is always included."""
    n = len(labels)
    rule: dict[int, str] = {}

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


def derive(labels: list[list[str]], trace_id: str, label_source: str) -> dict:
    """The pipeline's blocks record (Section 3 item 6) plus a per-sentence name list."""
    for i, paths in enumerate(labels):
        if not 1 <= len(paths) <= 2:
            raise ValueError(f"sentence {i}: {len(paths)} paths; expected one or two")
        for p in paths:
            if level1(p) not in L1_ABBR:
                raise ValueError(f"sentence {i}: unknown Level 1 in {p!r}")
    n = len(labels)
    ops = openers(labels)
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
            "blocks": block_records, "sentence_names": sentence_names}


# ----------------------------------------------------------------------------
# The reviewed listing
# ----------------------------------------------------------------------------

ROW = re.compile(r"^\| s(\d+)\(new\)-s(\d+)\(old(?:, part (\d))?\) \| (.*?) \| (.*) \|\s*$")
NAME = re.compile(r" \((\[?[A-Z][a-z](?:\+[A-Z][a-z])?\]?[\u2080-\u2089]+[\u00b9\u00b2\u00b3\u2070-\u2079]*(?:\(\d+\))?)\)$")
SEP = re.compile(r" \\?\|\\?\| ")
BLOCK = re.compile(r"^\| ([CE])-B(\d+) \| \[s(\d+), s(\d+)\] \| (\d+) \| (\d+) \| (R[123]): (.*) \|\s*$")


def normalize_listing_name(name: str) -> str:
    """The listing writes the count also when it is 1 (Rs₁(1)); the scheme omits it."""
    return name[:-3] if name.endswith("(1)") else name


def parse_listing(path: Path | str = LISTING) -> dict[str, dict]:
    """{trace_id: {labels, names (as written), texts, blocks [(m, s_start, s_end, rule, label)]}}"""
    out = {"c004": {"labels": [], "names": [], "texts": [], "blocks": []},
           "e036": {"labels": [], "names": [], "texts": [], "blocks": []}}
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
            out[trace]["labels"].append(paths)
            out[trace]["names"].append(nm.group(1))
            out[trace]["texts"].append(m.group(5).replace("\\|", "|"))
    return out


def gate(trace_id: str, labels: list[list[str]], expected: dict) -> dict:
    """Compare derive(labels) with the listing's blocks and names.  Returns the numbers and
    every difference; 'pass' is True only with zero differences."""
    rec = derive(labels, trace_id, "reviewed_v3")
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
        "trace_id": trace_id,
        "blocks_expected": len(exp_blocks), "blocks_derived": len(got_blocks),
        "nodes_expected": n_nodes_expected, "nodes_derived": len(rec["nodes"]),
        "sentences": len(labels),
        "names_normalized": sum(1 for x in expected["names"] if x.endswith("(1)")),
        "block_diffs": block_diffs, "rule_diffs": rule_diffs, "name_diffs": name_diffs,
    }
    result["pass"] = (not block_diffs and not rule_diffs and not name_diffs
                      and len(exp_blocks) == len(got_blocks) and n_nodes_expected == len(rec["nodes"]))
    return result
