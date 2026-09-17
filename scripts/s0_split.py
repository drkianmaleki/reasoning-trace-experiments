#!/usr/bin/env python3
"""s0_split.py -- pipeline step (2/9): the sentence splitter.

Specification: docs/shared/2026-09-16_pipeline_v1.md (Sections 2, 3 item 3, 4 step 2/9)
and docs/shared/2026-09-16_labeling_scheme_v4.md, Section 0c (the splitting rule).

Rules implemented (labeling scheme v4, Section 0c)
--------------------------------------------------
Base rule (the reconstructed base rule of Section 0c; it equals the archived run's splitter,
archive/decided-mid-thought/scripts/resample_cuts.py split_sentences, except at a newline
preceded by a space, see clarification 6): a sentence ends after `.` `?` `!` `:` when the next
character is whitespace or the end of the text, and at a line break.

Rule (a): a comma that closes a segment containing a relation symbol (`=`, `<`, `>`, and the
Unicode symbols U+2264 U+2265 U+2260; not the arrows `->`, `=>`, `>=`, `<=`) acts as a period.
Segments are delimited by `, ; : ( )` and the sentence start. Commas inside parentheses do not
split.

Rule (b): an opening parenthesis that follows a segment containing a relation symbol starts a
new sentence if the parenthesis opens a capitalized clause ("(Wait, ...", "(Identity)"); a
lowercase clause ("(where $B$ is bat ...") stays attached.

Rule (b') (Kian, 2026-09-16): an opening parenthesis whose content is a single capital letter
immediately followed by `)` -- the pattern `\\([A-Z]\\)`, an option label such as (C) or (E) --
never starts a new sentence, whatever precedes it.  Reason: an option label is an operand, not
a clause.  "So (E) > (C)." and "Strict correctness = (E)." stay one sentence each.  Being an
operand, the label is also not a segment delimiter: in "The answer = (C), so we stop." the
segment "= (C)" keeps its relation symbol and the comma splits under rule (a).  Everything
else about rule (b) is unchanged.

Tag exclusion (Kian, 2026-09-16): a `<` or `>` that belongs to a tag matching
`</?[A-Za-z][A-Za-z0-9_-]*>` (for example `</think>`, `<think>`, `<br>`) is not a relation
symbol.  The tags are detected first (TAG_RE over the whole text), their bracket positions are
marked, and is_relation_symbol returns False there.  A bare `<` or `>` between operands
("x<y", "Bat > Ball") is still a relation symbol.

Offsets
-------
`split_offsets(text)` returns contiguous, non-overlapping [start, end) spans that partition the
whole text.  Every boundary sits immediately after the last non-whitespace character of the
sentence it closes (after the terminator, after the rule-(a) comma, after the last content
character before a line break or before a rule-(b) `(`), so the whitespace between two
sentences belongs to the beginning of the following sentence.  The first span starts at 0 and
the last span ends at len(text); trailing whitespace of the text therefore belongs to the last
sentence.  A boundary is never placed where the text before or after it is whitespace only,
so no span is empty and no span is whitespace only (unless the whole text is).

Clarifications beyond the quoted rule (reported in the t2 gate report)
----------------------------------------------------------------------
1. Rule (a) "acts as a period": the comma splits only when, like a period, it is followed by
   whitespace or the end of the text (so `1,000` is never split).
2. Segment state and parenthesis depth are tracked within a sentence and reset at every
   sentence start (an unbalanced `(` cannot suppress rule (a) beyond the sentence it is in).
3. "Capitalized clause": the character immediately after `(` is an uppercase letter
   (str.isupper()).
4. Rule (b) is applied only at parenthesis depth 0, like rule (a).
5. The display form strips spaces and tabs from both ends and, in addition, the trailing
   whitespace of the text from the last sentence (the only span that can end in whitespace).
6. "At a line break": a newline is a boundary when it directly follows a non-whitespace
   character (a carriage return in between is ignored, so CR+LF is one line break), or when it
   belongs to a blank line (a paragraph break always separates).  A single newline preceded by
   a space or tab is not a boundary (the terminator rule may still fire on the character before
   that space).  Forced by the confirmed listing: E-trace s157 `However, ... "the bat costs
   *more* than the ball." ⏎   Mathematically, we have two conditions:` is one sentence there
   (raw text `ball." \n   Mathematically`), and five more E-trace sentences are merged the same
   way.  NOTE: the archived script splits on every newline (its EXPECT table records 253 base
   sentences for e036, the listing 247); the six merges form the listing's old s150 (archived
   s150 + s151), s193, s200, s212, s227 and s240, so the two numberings agree up to archived
   s150 and every archived E cut (cut-60 to cut-65) is unaffected.  The C-trace has no
   space-before-newline site (366 in both).  The blank-line and CR sub-rules are clarification 7.
7. Blank line and CR+LF (2026-09-16, after the first gate; a review finding, not a listing
   sentence).  Clarification 6 as first implemented ("a newline is a boundary only when the
   character before it is not whitespace") also suppressed the boundary at a paragraph break
   whose previous line ends with a space, merging two paragraphs into one sentence.  The rule
   now is: a newline that belongs to a blank line (the whitespace run around it holds another
   newline) is always a boundary, and a carriage return directly before a newline is ignored,
   so CR+LF counts as one line break (sentence_text also shows CR+LF as one ⏎).  Forced by
   archived continuation rs0823_cut000_000 at raw offset 8006, `**"The bat costs $1.00 more
   than the ball."** \n\nWithout that specific numerical difference, ...`, which had become
   one sentence.  Effect: none on the source traces or sweep44; nine boundaries added in
   archived500 (nine continuations, all of the form `." \n\n`), no boundary removed.  The
   listing gate is unchanged (375 / 254, zero mismatches); check 4b passes with or without it
   (no such site in the source traces), and only the unit tests
   test_blank_line_after_a_trailing_space_is_a_boundary and test_crlf_line_endings depend on it.

Standard library only.  No network.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SWEEP_FILE = REPO / "archive" / "decided-mid-thought" / "runs" / "sweep_items_batball_2026-08-19_1623.jsonl"
ARCHIVED_FILE = REPO / "archive" / "decided-mid-thought" / "runs" / "resample_cuts_2026-08-25_1503.jsonl"
SOURCE_CONDITION = "eval0_multi0"
SOURCE_SAMPLES = {2: "c004", 40: "e036"}  # sample field -> trace_id
COLLECTIONS = ("source", "sweep44", "archived500")

NEWLINE_MARK = "⏎"  # the listing's line-break mark
TERMINATORS = ".?!:"
RELATION_UNICODE = "≤≥≠"  # the single-symbol forms of <=, >=, !=
RELATION_ASCII = "=<>"
ARROWS = ("->", "=>", ">=", "<=")
SEGMENT_DELIMITERS = ",;:()"
TAG_RE = re.compile(r"</?[A-Za-z][A-Za-z0-9_-]*>")  # tag exclusion (Kian, 2026-09-16)


# ----------------------------------------------------------------------------
# Character-level helpers
# ----------------------------------------------------------------------------

def tag_bracket_positions(text: str) -> frozenset[int]:
    """Positions of the `<` and `>` of every tag matching TAG_RE (`</think>`, `<think>`,
    `<br>`); at these positions is_relation_symbol is False (Kian, 2026-09-16)."""
    pos = set()
    for m in TAG_RE.finditer(text):
        pos.add(m.start())
        pos.add(m.end() - 1)
    return frozenset(pos)


def is_relation_symbol(text: str, i: int, tag_positions: frozenset[int] | None = None) -> bool:
    """True when text[i] is a relation symbol under rule (a): one of = < > (unless the
    character is part of one of the four arrow tokens -> => >= <=, or is the bracket of a tag
    matching TAG_RE) or one of the Unicode symbols U+2264 U+2265 U+2260.  `tag_positions` is
    the result of tag_bracket_positions(text); it is computed here when not supplied."""
    c = text[i]
    if c in RELATION_UNICODE:
        return True
    if c not in RELATION_ASCII:
        return False
    if tag_positions is None:
        tag_positions = tag_bracket_positions(text)
    if i in tag_positions:
        return False
    prev = text[i - 1] if i > 0 else ""
    nxt = text[i + 1] if i + 1 < len(text) else ""
    for arrow in ARROWS:
        if c == arrow[0] and nxt == arrow[1]:
            return False
        if c == arrow[1] and prev == arrow[0]:
            return False
    return True


def _content_end_before(text: str, i: int) -> int:
    """Index just after the last non-whitespace character strictly before position i."""
    j = i
    while j > 0 and text[j - 1].isspace():
        j -= 1
    return j


def _followed_by_space_or_end(text: str, i: int) -> bool:
    return i + 1 >= len(text) or text[i + 1].isspace()


# ----------------------------------------------------------------------------
# Boundary computation
# ----------------------------------------------------------------------------

def _line_break_is_boundary(text: str, i: int) -> bool:
    """Clarification 6: the newline at text[i] ends a sentence when it directly follows a
    non-whitespace character (a carriage return before it is ignored, so CR+LF counts as one
    line break), or when it belongs to a blank line (the whitespace run around it holds another
    newline), so a paragraph break always separates.  A single newline preceded by a space or
    tab is not a boundary (E-trace `ball." \\n   Mathematically, ...`)."""
    j = i - 1
    if j >= 0 and text[j] == "\r":
        j -= 1
    if j < 0:
        return False
    if not text[j].isspace():
        return True
    k = i - 1
    while k >= 0 and text[k].isspace():
        if text[k] == "\n":
            return True
        k -= 1
    k = i + 1
    while k < len(text) and text[k].isspace():
        if text[k] == "\n":
            return True
        k += 1
    return False


def _base_boundaries(text: str) -> set[int]:
    """Positions p where a sentence ends under the base rule (the next sentence starts at p)."""
    bounds: set[int] = set()
    for i, c in enumerate(text):
        if c in TERMINATORS and _followed_by_space_or_end(text, i):
            bounds.add(i + 1)
        elif c == "\n" and _line_break_is_boundary(text, i):
            bounds.add(_content_end_before(text, i))
    return bounds


def _is_option_label(text: str, i: int) -> bool:
    """True when text[i:i + 3] matches `\\([A-Z]\\)`, an option label such as (C) or (E)
    (rule (b'), Kian, 2026-09-16: an option label is an operand, not a clause)."""
    return (text[i] == "(" and i + 2 < len(text)
            and "A" <= text[i + 1] <= "Z" and text[i + 2] == ")")


def _equation_boundaries(text: str, base: set[int]) -> set[int]:
    """Additional positions from rules (a), (b) and (b'), computed in one left-to-right scan.
    Segment state (relation symbol seen, parenthesis depth) resets at every sentence start."""
    extra: set[int] = set()
    seg_has_relation = False
    depth = 0
    n = len(text)
    tags = tag_bracket_positions(text)
    i = 0
    while i < n:
        if i in base or i in extra:
            seg_has_relation = False
            depth = 0
        c = text[i]
        if c == "(" and _is_option_label(text, i):
            # rule (b'): an option label `(A)`..`(Z)` is an operand: it never starts a new
            # sentence, is not a segment delimiter and does not change the depth; the segment
            # it sits in keeps its relation symbol ("= (C), so" still splits under rule (a)).
            i += 3
            continue
        if c == "(":
            if depth == 0 and seg_has_relation and i + 1 < n and text[i + 1].isupper():
                extra.add(_content_end_before(text, i))  # rule (b): boundary before the `(`
            depth += 1
            seg_has_relation = False
        elif c == ")":
            depth = max(0, depth - 1)
            seg_has_relation = False
        elif c == ",":
            if depth == 0 and seg_has_relation and _followed_by_space_or_end(text, i):
                extra.add(i + 1)  # rule (a): the comma acts as a period
            seg_has_relation = False
        elif c in SEGMENT_DELIMITERS:  # ; :
            seg_has_relation = False
        elif is_relation_symbol(text, i, tags):
            seg_has_relation = True
        i += 1
    return extra


def _spans_from_boundaries(text: str, bounds: set[int]) -> list[tuple[int, int]]:
    n = len(text)
    if n == 0:
        return []
    keep = sorted(p for p in bounds if 0 < p < n and text[:p].strip() and text[p:].strip())
    starts = [0] + keep
    ends = keep + [n]
    return list(zip(starts, ends))


def base_offsets(text: str) -> list[tuple[int, int]]:
    """Spans of the base rule alone (Section 0c without rules (a) and (b); the archived splitter
    except for clarification 6), as a partition of the text."""
    return _spans_from_boundaries(text, _base_boundaries(text))


def split_offsets(text: str) -> list[tuple[int, int]]:
    """Spans of the equation-rule splitter (base rule plus rules (a) and (b)).
    Every base-rule boundary is kept by construction."""
    base = _base_boundaries(text)
    extra = _equation_boundaries(text, base)
    return _spans_from_boundaries(text, base | extra)


def sentence_text(text: str, start: int, end: int) -> str:
    """The listing's display form of a span: spaces and tabs stripped from both ends (and the
    trailing whitespace of the text, which only the last span can carry), newlines as U+23CE."""
    s = text[start:end].lstrip(" \t").rstrip()
    return s.replace("\r\n", "\n").replace("\n", NEWLINE_MARK)


def old_index_and_part(text: str) -> list[tuple[int, int]]:
    """For every equation-rule span: (old_s, part) -- the index of the base-rule span that
    contains it and its 1-based ordinal inside that base span."""
    base = base_offsets(text)
    spans = split_offsets(text)
    out: list[tuple[int, int]] = []
    b = 0
    part = 0
    for start, end in spans:
        while b < len(base) and base[b][1] <= start:
            b += 1
            part = 0
        if b >= len(base) or not (base[b][0] <= start and end <= base[b][1]):
            raise ValueError(f"span [{start}, {end}) is not inside one base-rule span")
        part += 1
        out.append((b, part))
    return out


THINK_END_TAG = "</think>"
CONTINUATION_COLLECTIONS = ("archived500",)  # and every future resampling run
CONTINUATION_RULE = ("continuation: the text before the first </think> tag is split; the reply after the tag is "
                     "neither split nor labeled; a continuation without the tag (the cap was hit) is split whole; "
                     "think_end = character index of the tag in the raw text, or null (Kian, 2026-09-17)")


def split_records(trace_id: str, text: str, with_old: bool = False, continuation: bool = False) -> list[dict]:
    """One record per sentence in the schema of pipeline v1, Section 3 item 3.  With
    continuation=True (archived500 and every future resampling run) only the text before the
    first </think> tag is split and every record carries think_end (the tag's character index in
    the raw text, or None when there is no tag and the whole text is split)."""
    think_end = None
    if continuation:
        i = text.find(THINK_END_TAG)
        if i >= 0:
            think_end = i
            text = text[:i]
    spans = split_offsets(text)
    old = old_index_and_part(text) if with_old else None
    records = []
    for s, (start, end) in enumerate(spans):
        rec = {"trace_id": trace_id, "s": s}
        if with_old:
            rec["old_s"], rec["part"] = old[s]
        rec["char_start"] = start
        rec["char_end"] = end
        rec["text"] = sentence_text(text, start, end)
        if continuation:
            rec["think_end"] = think_end
        records.append(rec)
    return records


# ----------------------------------------------------------------------------
# Loaders (read only)
# ----------------------------------------------------------------------------

def _read_jsonl(path: Path):
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


def load_sweep_condition(path: Path = SWEEP_FILE) -> list[dict]:
    """All records of the source condition, in file order (the sweep44 collection)."""
    return [r for r in _read_jsonl(path) if r.get("condition") == SOURCE_CONDITION]


def load_source_traces(path: Path = SWEEP_FILE) -> dict[str, str]:
    """{'c004': text, 'e036': text}, looked up by the `sample` field."""
    out = {}
    for r in load_sweep_condition(path):
        if r.get("sample") in SOURCE_SAMPLES:
            out[SOURCE_SAMPLES[r["sample"]]] = r["trace"]
    missing = set(SOURCE_SAMPLES.values()) - set(out)
    if missing:
        raise RuntimeError(f"source traces not found: {sorted(missing)}")
    return out


def load_collection(name: str) -> list[tuple[str, str]]:
    """[(trace_id, text), ...] for a collection."""
    if name == "source":
        return list(load_source_traces().items())
    if name == "sweep44":
        recs = load_sweep_condition()
        cond = SOURCE_CONDITION.replace("_", "")
        return [(f"s0819_{cond}_{k:03d}", r["trace"]) for k, r in enumerate(recs, start=1)]
    if name == "archived500":
        return [(r["id"], r["cont_text"]) for r in _read_jsonl(ARCHIVED_FILE)]
    raise ValueError(f"unknown collection {name!r}")


def input_files(name: str) -> list[Path]:
    return [ARCHIVED_FILE] if name == "archived500" else [SWEEP_FILE]


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:  # git missing or not a repository
        return None


def git_dirty() -> bool | None:
    """True when the working tree has modified or untracked files (the recorded HEAD then does
    not contain the exact code that ran; config.json also records the script's sha256)."""
    try:
        out = subprocess.run(["git", "status", "--porcelain"], cwd=REPO, capture_output=True,
                             text=True, check=True).stdout
        return bool(out.strip())
    except Exception:
        return None


def _rel(path: Path) -> str:
    path = path.resolve()
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return str(path)


def run_collection(name: str, out_dir: Path) -> dict:
    """Split a collection, write sentences_<name>.jsonl, config.json and _log.txt into out_dir.
    Returns the config entry of this collection."""
    out_dir.mkdir(parents=True, exist_ok=True)
    traces = load_collection(name)
    continuation = name in CONTINUATION_COLLECTIONS
    out_path = out_dir / f"sentences_{name}.jsonl"
    n_records = 0
    counts = []
    log_lines = []
    with_tag = without_tag = 0
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        for trace_id, text in traces:
            recs = split_records(trace_id, text, with_old=(name == "source"), continuation=continuation)
            for rec in recs:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n_records += len(recs)
            counts.append(len(recs))
            if continuation:
                tagged = THINK_END_TAG in text
                with_tag += tagged
                without_tag += not tagged
                log_lines.append(f"{trace_id}\t{len(text)}\t{len(recs)}\tthink_end={text.find(THINK_END_TAG) if tagged else 'null'}")
            else:
                log_lines.append(f"{trace_id}\t{len(text)}\t{len(recs)}")
    entry = {
        "collection": name,
        "output": _rel(out_path),
        "inputs": [{"path": _rel(p), "sha256": sha256_of_file(p)} for p in input_files(name)],
        "traces": len(traces),
        "records": n_records,
        "continuation_rule": CONTINUATION_RULE if continuation else None,
        "continuations_with_think_tag": with_tag if continuation else None,
        "continuations_without_think_tag": without_tag if continuation else None,
        "sentences_per_trace": {
            "min": min(counts) if counts else None,
            "median": statistics.median(counts) if counts else None,
            "max": max(counts) if counts else None,
        },
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    config_path = out_dir / "config.json"
    config = {}
    if config_path.exists():
        with open(config_path, encoding="utf-8") as fh:
            config = json.load(fh)
    config["script"] = _rel(Path(__file__))
    config["script_sha256"] = sha256_of_file(Path(__file__).resolve())
    config["git_commit"] = git_head()
    config["git_dirty"] = git_dirty()
    config["python"] = sys.version.split()[0]
    config.setdefault("collections", {})[name] = entry
    with open(config_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(config, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    with open(out_dir / "_log.txt", "a", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# s0_split collection={name} {entry['timestamp']} traces={len(traces)} records={n_records}\n")
        fh.write("# trace_id\tcharacters\tsentences\n")
        for line in log_lines:
            fh.write(line + "\n")
    return entry


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Pipeline step (2/9): split traces into sentences.")
    ap.add_argument("--collection", required=True, choices=COLLECTIONS)
    ap.add_argument("--out", required=True, help="output folder (created if missing)")
    args = ap.parse_args(argv)
    out_dir = Path(args.out)
    print(f"s0_split: collection={args.collection} out={out_dir} git={git_head()} "
          f"inputs={[_rel(p) for p in input_files(args.collection)]}")
    entry = run_collection(args.collection, out_dir)
    print(json.dumps(entry, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
