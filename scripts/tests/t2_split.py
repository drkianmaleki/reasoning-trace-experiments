#!/usr/bin/env python3
"""t2_split -- gate test of pipeline step (2/9), the splitter (pipeline v1, Section 9 item 4).

Writes runs/tests/t2_split_<YYYY-MM-DD>_<HHMM>/TEST_REPORT.md plus artifacts:
  sentences_source.jsonl (with old_s and part), config.json, _log.txt, mismatches.txt,
  sentences_archived5_sample.jsonl, sentences_archived5_sample.md, pytest_output.txt.

Checks (each PASS or FAIL with the numbers behind it):
  1. counts: c004 375, e036 254 (equation rule); 366 and 247 (base rule)
  2. boundary-by-boundary match with the confirmed listing (exact / prefix / mismatch)
  3. old_s and part match the listing's Item column for all 629 rows
  4. every base-rule boundary is also an equation-rule boundary
  5. partition properties and text == sentence_text(...) for every record of sentences_source.jsonl
  6. the splitter on the first five archived continuations (sentence lists for Kian to eyeball)
  plus: pytest on scripts/tests/test_s0_split.py (output copied into the report)
Offline; API cost $0.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import s0_split as S  # noqa: E402

LISTING = S.REPO / "docs" / "shared" / "2026-09-16_source_traces_labeled_v3.md"  # v2 moved to archive/ on 2026-09-16
UNIT_TESTS = S.REPO / "scripts" / "tests" / "test_s0_split.py"
EXPECTED = {"c004": (375, 366), "e036": (254, 247)}  # (equation rule, base rule)
TRUNCATED_LENGTHS = (149, 150)  # the listing truncates the text column at 150 characters
ROW = re.compile(r"^\| s(\d+)\(new\)-s(\d+)\(old(?:, part (\d))?\) \| (.*?) \| (.*) \|\s*$")


def parse_listing(path: Path = LISTING) -> dict[str, list[dict]]:
    """Every table row of the listing -> {trace: [{s, old_s, part, text}, ...]} in file order.
    The text column's `\\|` escape is undone; nothing else is unescaped."""
    rows: dict[str, list[dict]] = {"c004": [], "e036": []}
    trace = None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("## C-trace"):
                trace = "c004"
            elif line.startswith("## E-trace"):
                trace = "e036"
            elif line.startswith("## "):
                trace = None  # any other top section (e.g. the changelog) holds no rows
            m = ROW.match(line)
            if m and trace:
                rows[trace].append({
                    "s": int(m.group(1)),
                    "old_s": int(m.group(2)),
                    "part": int(m.group(3) or 1),
                    "text": m.group(5).replace("\\|", "|"),
                })
    return rows


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    stamp = datetime.now()
    folder = S.REPO / "runs" / "tests" / f"t2_split_{stamp:%Y-%m-%d_%H%M}"
    folder.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []      # report lines (one per check)
    details: list[str] = []    # supporting detail blocks
    verdicts: list[bool] = []

    def check(ok: bool, name: str, numbers: str):
        verdicts.append(ok)
        lines.append(f"- {'PASS' if ok else 'FAIL'} — {name} — {numbers}")
        print(lines[-1])

    traces = S.load_source_traces()
    listing = parse_listing()

    # ---- check 1: counts --------------------------------------------------------------
    eq = {tid: S.split_offsets(t) for tid, t in traces.items()}
    base = {tid: S.base_offsets(t) for tid, t in traces.items()}
    nums = []
    ok = True
    for tid, (n_eq, n_base) in EXPECTED.items():
        nums.append(f"{tid}: equation rule {len(eq[tid])} (expected {n_eq}), base rule {len(base[tid])} (expected {n_base})")
        ok &= len(eq[tid]) == n_eq and len(base[tid]) == n_base
    check(ok, "check 1, sentence counts", "; ".join(nums))

    # ---- check 2: boundary-by-boundary match with the listing ------------------------
    mismatch_lines: list[str] = []
    nums = []
    ok = True
    for tid, text in traces.items():
        rows = listing[tid]
        exact = prefix = mism = 0
        n = max(len(rows), len(eq[tid]))
        for k in range(n):
            mine = S.sentence_text(text, *eq[tid][k]) if k < len(eq[tid]) else None
            row = rows[k] if k < len(rows) else None
            if row is not None and row["s"] != k:
                mism += 1
                mismatch_lines.append(f"{tid} s{k}: listing row index {row['s']} out of order")
                continue
            ltext = row["text"] if row is not None else None
            if mine is not None and ltext is not None and mine == ltext:
                exact += 1
            elif (mine is not None and ltext is not None and len(ltext) in TRUNCATED_LENGTHS
                  and mine.startswith(ltext)):
                prefix += 1
            else:
                mism += 1
                mismatch_lines.append(f"{tid} s{k}:\n  listing: {ltext!r}\n  mine:    {mine!r}")
        ok &= mism == 0 and len(rows) == len(eq[tid])
        nums.append(f"{tid}: {len(rows)} listing rows, {len(eq[tid])} sentences; exact {exact}, prefix {prefix}, mismatches {mism}")
    (folder / "mismatches.txt").write_text("\n".join(mismatch_lines) + ("\n" if mismatch_lines else ""), encoding="utf-8")
    check(ok, "check 2, boundary-by-boundary match with the listing", "; ".join(nums) + f"; mismatches listed in mismatches.txt ({len(mismatch_lines)} entries)")
    if mismatch_lines:
        details.append("### Mismatches (check 2)\n\n```\n" + "\n".join(mismatch_lines) + "\n```")

    # ---- check 3: old_s and part ------------------------------------------------------
    nums = []
    ok = True
    total_rows = 0
    bad: list[str] = []
    for tid, text in traces.items():
        mine = S.old_index_and_part(text)
        rows = listing[tid]
        total_rows += len(rows)
        n_ok = 0
        for k, row in enumerate(rows):
            if k < len(mine) and mine[k] == (row["old_s"], row["part"]):
                n_ok += 1
            else:
                bad.append(f"{tid} s{k}: listing old_s/part {(row['old_s'], row['part'])}, mine {mine[k] if k < len(mine) else None}")
        ok &= n_ok == len(rows) == len(mine)
        n_parts = sum(1 for p in mine if p[1] > 1)
        nums.append(f"{tid}: {n_ok}/{len(rows)} rows agree, {n_parts} equation-rule parts (part > 1)")
    check(ok, "check 3, old_s and part against the listing's Item column", f"{total_rows} rows; " + "; ".join(nums))
    if bad:
        details.append("### old_s/part disagreements (check 3)\n\n```\n" + "\n".join(bad) + "\n```")

    # ---- check 4: base boundaries kept ------------------------------------------------
    nums = []
    ok = True
    for tid in traces:
        base_ends = {b for _, b in base[tid]}
        eq_ends = {b for _, b in eq[tid]}
        lost = sorted(base_ends - eq_ends)
        ok &= not lost
        nums.append(f"{tid}: {len(base_ends)} base boundaries, {len(base_ends & eq_ends)} kept, {len(lost)} lost, {len(eq_ends - base_ends)} added by the equation rule")
    check(ok, "check 4, every base-rule boundary is an equation-rule boundary", "; ".join(nums))

    # ---- check 4b: the archived splitter as an independent oracle for the base rule ---------
    # split_sentences of archive/decided-mid-thought/scripts/resample_cuts.py, verbatim, and the
    # archived way of locating each sentence in the raw text (find from the previous end).
    def archived_split_sentences(text):
        sents = []
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            parts = re.split(r"(?<=[.!?:])\s+", line)
            sents.extend(p for p in parts if p.strip())
        return sents

    nums = []
    ok = True
    oracle_detail: list[str] = []
    for tid, text in traces.items():
        sents = archived_split_sentences(text)
        pos, arch_ends = 0, []
        for s_ in sents:
            i = text.find(s_, pos)
            if i < 0:
                oracle_detail.append(f"{tid}: archived sentence not found in raw text: {s_[:60]!r}")
                ok = False
                break
            pos = i + len(s_)
            arch_ends.append(pos)
        arch_set = set(arch_ends[:-1])           # inner boundaries of the archived numbering
        mine_set = {b for _, b in base[tid][:-1]}
        added = sorted(mine_set - arch_set)      # boundaries the base rule has but the archive lacks
        merged = sorted(arch_set - mine_set)     # archived boundaries the base rule drops
        # every dropped boundary must be a single newline preceded by a space or tab
        # (clarification 6); anything else is a FAIL
        bad = [p for p in merged
               if not (text[p] in " \t" and text[p:].lstrip(" \t").startswith("\n")
                       and not text[p:].lstrip(" \t")[1:].lstrip(" \t").startswith("\n"))]
        old_of = {}
        for k, (a, b) in enumerate(base[tid]):
            for p in merged:
                if a < p < b:
                    old_of[p] = k
        ok &= not added and not bad
        nums.append(f"{tid}: archived splitter {len(sents)} sentences, base rule {len(base[tid])}; "
                    f"boundaries added {len(added)}, dropped {len(merged)}"
                    + (f" (all single newlines preceded by a space; they form old {', '.join('s' + str(old_of[p]) for p in merged)})" if merged and not bad else "")
                    + (f"; {len(bad)} dropped boundary NOT of that form" if bad else ""))
        for p in merged:
            oracle_detail.append(f"{tid} raw offset {p} (old s{old_of.get(p)}): {text[max(0, p - 50):p]!r} || {text[p:p + 30]!r}")
    check(ok, "check 4b, base rule against the archived splitter (independent oracle)", "; ".join(nums))
    if oracle_detail:
        details.append("### Base-rule boundaries dropped relative to the archived splitter (check 4b)\n\n```\n" + "\n".join(oracle_detail) + "\n```")

    # ---- check 5: sentences_source.jsonl, partition properties, text field -----------
    entry = S.run_collection("source", folder)
    recs = [json.loads(l) for l in open(folder / "sentences_source.jsonl", encoding="utf-8") if l.strip()]
    problems: list[str] = []
    by_trace: dict[str, list[dict]] = {}
    for r in recs:
        by_trace.setdefault(r["trace_id"], []).append(r)
    for tid, text in traces.items():
        rs = by_trace.get(tid, [])
        if not rs:
            problems.append(f"{tid}: no records")
            continue
        if [r["s"] for r in rs] != list(range(len(rs))):
            problems.append(f"{tid}: s not 0..N-1 in order")
        if rs[0]["char_start"] != 0:
            problems.append(f"{tid}: first span starts at {rs[0]['char_start']}")
        if rs[-1]["char_end"] != len(text):
            problems.append(f"{tid}: last span ends at {rs[-1]['char_end']} != {len(text)}")
        for a, b in zip(rs, rs[1:]):
            if a["char_end"] != b["char_start"]:
                problems.append(f"{tid}: gap/overlap between s{a['s']} and s{b['s']}")
        for r in rs:
            if not (r["char_start"] < r["char_end"]):
                problems.append(f"{tid} s{r['s']}: empty span")
            if r["text"] != S.sentence_text(text, r["char_start"], r["char_end"]):
                problems.append(f"{tid} s{r['s']}: text != sentence_text(...)")
            if "old_s" not in r or "part" not in r:
                problems.append(f"{tid} s{r['s']}: old_s/part missing")
    ok = not problems and len(recs) == sum(n for n, _ in EXPECTED.values())
    check(ok, "check 5, sentences_source.jsonl partition properties and text field",
          f"{len(recs)} records ({', '.join(f'{t}: {len(by_trace.get(t, []))}' for t in traces)}); "
          f"first start 0, last end = len(text), contiguous, no empty span, text == sentence_text: "
          f"{'all hold' if not problems else str(len(problems)) + ' problems'}")
    if problems:
        details.append("### Problems (check 5)\n\n```\n" + "\n".join(problems[:200]) + "\n```")

    # ---- check 6: five archived continuations -----------------------------------------
    archived = []
    with open(S.ARCHIVED_FILE, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                archived.append(json.loads(line))
            if len(archived) == 5:
                break
    counts = []
    with open(folder / "sentences_archived5_sample.jsonl", "w", encoding="utf-8", newline="\n") as fj, \
         open(folder / "sentences_archived5_sample.md", "w", encoding="utf-8", newline="\n") as fm:
        fm.write("# Splitter output on the first five archived continuations (resample_cuts_2026-08-25_1503.jsonl)\n\n")
        fm.write("One line per sentence: `trace_id s: text` (display form; ⏎ marks a line break). "
                 "Continuation rule (Kian, 2026-09-17): only the text before the first </think> tag is split; think_end is the tag's character index.\n")
        for r in archived:
            recs5 = S.split_records(r["id"], r["cont_text"], continuation=True)
            think_end = recs5[0]["think_end"] if recs5 else r["cont_text"].find(S.THINK_END_TAG)
            counts.append((r["id"], len(r["cont_text"]), len(recs5), think_end))
            fm.write(f"\n## {r['id']} ({len(r['cont_text'])} characters, think_end {think_end}, {len(recs5)} sentences)\n\n")
            for rec in recs5:
                fj.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fm.write(f"{rec['trace_id']} {rec['s']}: {rec['text']}\n")
    ok = len(counts) == 5 and all(n > 0 for _, _, n, _ in counts) and all(
        (te is None) or all(json.loads(l)["char_end"] <= te for l in open(folder / "sentences_archived5_sample.jsonl", encoding="utf-8") if json.loads(l)["trace_id"] == i)
        for i, _, _, te in counts)
    check(ok, "check 6, splitter on the first five archived continuations (text before </think> only)",
          "; ".join(f"{i}: {c} chars, think_end {te}, {n} sentences" for i, c, n, te in counts) + " (files sentences_archived5_sample.jsonl and .md)")

    # ---- pytest ------------------------------------------------------------------------
    cmd = [sys.executable, "-m", "pytest", "-q", str(UNIT_TESTS.relative_to(S.REPO).as_posix())]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    proc = subprocess.run(cmd, cwd=S.REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    pytest_out = proc.stdout + (("\n" + proc.stderr) if proc.stderr.strip() else "")
    (folder / "pytest_output.txt").write_text(pytest_out, encoding="utf-8")
    check(proc.returncode == 0, "pytest, scripts/tests/test_s0_split.py",
          f"exit code {proc.returncode}; last line: {pytest_out.strip().splitlines()[-1] if pytest_out.strip() else '(no output)'}")

    # ---- report -------------------------------------------------------------------------
    gate = all(verdicts)
    inputs = [f"`{e['path']}` sha256 `{e['sha256']}`" for e in entry["inputs"]]
    report = [
        f"# TEST_REPORT — t2_split — {stamp:%Y-%m-%d %H:%M}",
        "",
        f"Gate test of pipeline step (2/9), the splitter (`scripts/s0_split.py`), per pipeline v1 Section 9 item 4. "
        f"Git commit at run time: `{S.git_head()}` (working tree dirty: {S.git_dirty()}; the script under test is "
        f"identified by its sha256 `{S.sha256_of_file(S.REPO / 'scripts' / 's0_split.py')}` in config.json). "
        f"Python {sys.version.split()[0]}. Offline; API cost $0.",
        "",
        f"Inputs: {'; '.join(inputs)}; listing `{LISTING.relative_to(S.REPO).as_posix()}`.",
        "",
        f"## Result: {'PASS' if gate else 'FAIL'} ({sum(verdicts)}/{len(verdicts)} checks passed)",
        "",
        "## Checks",
        "",
        *lines,
        "",
        "## Clarifications applied beyond the quoted rule (labeling scheme v4, Section 0c)",
        "",
        "See the module docstring of `scripts/s0_split.py`, items 1–6. In short: (1) a rule-(a) comma, like a period, "
        "must be followed by whitespace or the end of the text; (2) segment state and parenthesis depth reset at every "
        "sentence start; (3) a capitalized clause = the character right after `(` is an uppercase letter; (4) rule (b) "
        "only at parenthesis depth 0; (5) the display form drops the text's trailing whitespace from the last sentence; "
        "(6) a line break is a boundary when the newline directly follows a non-whitespace character or belongs to a "
        "blank line; a single newline preceded by a space is not — forced by E s157 (`ball.\" ⏎   Mathematically, ...`), "
        "where the confirmed listing keeps one sentence; the archived script's splitter (split on every newline) gives "
        "253 base sentences for e036, the listing 247 (six merges forming old s150, s193, s200, s212, s227, s240; the "
        "numberings agree up to archived s150, so the archived E cuts 60–65 are unaffected; see check 4b).",
        "",
        "## Files produced",
        "",
        f"- `{folder.relative_to(S.REPO).as_posix()}/TEST_REPORT.md` (this file)",
        f"- `sentences_source.jsonl` — {len(recs)} records with old_s and part; `config.json`, `_log.txt` (written by s0_split.run_collection)",
        f"- `mismatches.txt` — {len(mismatch_lines)} entries",
        f"- `sentences_archived5_sample.jsonl`, `sentences_archived5_sample.md` — {sum(n for _, _, n, _ in counts)} sentences of five archived continuations (text before </think> only)",
        "- `pytest_output.txt`",
        "",
        "## pytest output",
        "",
        "```",
        pytest_out.rstrip(),
        "```",
    ]
    if details:
        report += ["", *details]
    (folder / "TEST_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"\nReport: {folder / 'TEST_REPORT.md'}\nGate: {'PASS' if gate else 'FAIL'}")
    return 0 if gate else 1


if __name__ == "__main__":
    sys.exit(main())
