#!/usr/bin/env python3
"""judge_codec.py -- the judge's reply format (pipeline v1, steps 3c/9 and 3c''/9).

A reply is plain text, one line per run of consecutive sentences with the same label:
    <first>-<last> <code>        a run of two or more sentences
    <first> <code>               a single sentence
    <index> <codeA>+<codeB>      a combined sentence (two labels, its own line)
Runs are in increasing order and cover 0 .. n-1 exactly once.  Codes are those of
prompts/labels_v1.json (the inventory written by s1a_make_prompt.py).

parse_reply(text, n_sentences, inventory) -> [[path, ...], ...]   one list of one or two full
paths ("Level 1 > Level 2 [> Level 3]") per sentence, or ReplyError(kind, line_no, line, detail)
with kind in {unparsable, unknown_code, gap, overlap, out_of_range, too_many_codes, descending}.
Blank lines and surrounding whitespace are tolerated; a ``` fence is stripped and reported in the
warnings of parse_reply_with_warnings.  Nothing else is forgiven.

encode(labels_per_sentence, inventory) -> str   the canonical run-length form (the inverse).

Standard library only.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_LABELS = REPO / "prompts" / "labels_v1.json"
KINDS = ("unparsable", "unknown_code", "gap", "overlap", "out_of_range", "too_many_codes", "descending")
LINE_RE = re.compile(r"^(\d+)(?:-(\d+))?\s+(\S+)$")


class ReplyError(ValueError):
    def __init__(self, kind: str, line_no: int, line: str, detail: str):
        if kind not in KINDS:
            raise ValueError(f"unknown error kind {kind!r}")
        self.kind, self.line_no, self.line, self.detail = kind, line_no, line, detail
        super().__init__(f"{kind} at line {line_no} ({line!r}): {detail}")


class Inventory:
    """code <-> path ('Level 1 > Level 2 [> Level 3]')."""

    def __init__(self, code_to_path: dict[str, str], version: str | None = None):
        self.code_to_path = dict(code_to_path)
        self.path_to_code = {p: c for c, p in self.code_to_path.items()}
        if len(self.path_to_code) != len(self.code_to_path):
            raise ValueError("inventory paths are not unique")
        self.version = version

    @classmethod
    def load(cls, path: Path | str = DEFAULT_LABELS) -> "Inventory":
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return cls({e["code"]: " > ".join(e["path"]) for e in data["paths"]}, data.get("version"))

    def __contains__(self, code: str) -> bool:
        return code in self.code_to_path

    def __len__(self) -> int:
        return len(self.code_to_path)


_default: Inventory | None = None


def _coerce(inventory) -> Inventory:
    global _default
    if isinstance(inventory, Inventory):
        return inventory
    if isinstance(inventory, dict):
        return Inventory(inventory)
    if inventory is None:
        if _default is None:
            _default = Inventory.load()
        return _default
    raise TypeError("inventory must be an Inventory, a dict code->path, or None")


def _strip_fence(lines: list[str], warnings: list[str]) -> list[str]:
    # drop leading/trailing blank lines, then a ``` line at each end
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if lines and lines[0].strip().startswith("```"):
        warnings.append(f"opening code fence stripped: {lines[0].strip()!r}")
        lines.pop(0)
        if lines and lines[-1].strip() == "```":
            warnings.append("closing code fence stripped")
            lines.pop()
        else:
            warnings.append("opening fence without a closing fence")
    return lines


def parse_reply_with_warnings(text: str, n_sentences: int, inventory=None) -> tuple[list[list[str]], list[str]]:
    inv = _coerce(inventory)
    warnings: list[str] = []
    raw_lines = text.splitlines()
    lines = _strip_fence(list(raw_lines), warnings)
    labels: list[list[str]] = []
    expected_next = 0
    prev_first = -1
    last_line_no = 0
    for line_no, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line:
            continue  # blank lines are tolerated
        last_line_no = line_no
        m = LINE_RE.match(line)
        if not m:
            raise ReplyError("unparsable", line_no, line, "expected '<first>-<last> <code>' or '<index> <code>'")
        first = int(m.group(1))
        last = int(m.group(2)) if m.group(2) is not None else first
        codes = m.group(3).split("+")
        if len(codes) > 2:
            raise ReplyError("too_many_codes", line_no, line, f"{len(codes)} codes; at most two")
        for c in codes:
            if c not in inv:
                raise ReplyError("unknown_code", line_no, line, f"code {c!r} is not in the inventory")
        if len(codes) == 2:
            if last != first:
                raise ReplyError("unparsable", line_no, line, "a combined sentence needs a single index, not a run")
            if codes[0] == codes[1]:
                raise ReplyError("unparsable", line_no, line, "the two codes of a combined sentence are identical")
        if last < first:
            raise ReplyError("descending", line_no, line, f"run ends at {last} before it starts at {first}")
        if last >= n_sentences:
            raise ReplyError("out_of_range", line_no, line, f"index {last} beyond the last sentence {n_sentences - 1}")
        if first != expected_next:
            if first > expected_next:
                raise ReplyError("gap", line_no, line, f"sentences {expected_next}..{first - 1} are not covered")
            if first < prev_first:
                raise ReplyError("descending", line_no, line, f"run starts at {first}, before the previous run's start {prev_first}")
            raise ReplyError("overlap", line_no, line, f"sentences {first}..{min(last, expected_next - 1)} are covered twice")
        paths = [inv.code_to_path[c] for c in codes]
        for _ in range(first, last + 1):
            labels.append(list(paths))
        expected_next = last + 1
        prev_first = first
    if expected_next < n_sentences:
        raise ReplyError("gap", last_line_no, lines[last_line_no - 1].strip() if last_line_no else "",
                         f"sentences {expected_next}..{n_sentences - 1} are not covered")
    return labels, warnings


def parse_reply(text: str, n_sentences: int, inventory=None) -> list[list[str]]:
    labels, _ = parse_reply_with_warnings(text, n_sentences, inventory)
    return labels


def encode(labels_per_sentence: list[list[str]], inventory=None) -> str:
    """The canonical run-length form of a labeling: runs of a single label merged, every
    combined sentence on its own line."""
    inv = _coerce(inventory)
    out: list[str] = []
    run_code: str | None = None
    run_first = 0
    run_last = -1

    def flush():
        if run_code is not None:
            out.append(f"{run_first}-{run_last} {run_code}" if run_last > run_first else f"{run_first} {run_code}")

    for i, paths in enumerate(labels_per_sentence):
        if not 1 <= len(paths) <= 2:
            raise ValueError(f"sentence {i}: {len(paths)} labels; expected one or two")
        try:
            codes = [inv.path_to_code[p] for p in paths]
        except KeyError as e:
            raise ValueError(f"sentence {i}: path not in the inventory: {e.args[0]!r}") from None
        if len(codes) == 2:
            flush()
            run_code = None
            out.append(f"{i} {codes[0]}+{codes[1]}")
            continue
        if run_code == codes[0] and run_last == i - 1:
            run_last = i
        else:
            flush()
            run_code, run_first, run_last = codes[0], i, i
    flush()
    return "\n".join(out)
