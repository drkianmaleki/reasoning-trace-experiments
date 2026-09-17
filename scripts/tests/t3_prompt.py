#!/usr/bin/env python3
"""t3_prompt -- gate test of pipeline step (3/9), the judge prompt and codes (pipeline v1,
Section 9 item 5).  Offline.

Writes runs/tests/t3_prompt_<YYYY-MM-DD>_<HHMM>/TEST_REPORT.md plus artifacts: a copy of the
prompt and of labels_v1.json, hits.txt, pytest_output.txt, config.json.

Checks:
  1. no-quote gate (decision 6): every sentence of c004 and e036 with four or more words is
     searched in the prompt (whitespace-normalized, case-sensitive); sentences that are verbatim
     parts of the item prompt are exempt and listed; PASS only with zero non-exempt hits
  2. every inventory path has exactly one code, every code decodes to its path, codes unique
  3. the prompt contains the eight Level 1 names, the six option codes, the output-format
     section and the three worked examples, and each example's expected output parses
  4. pytest on scripts/tests exits 0
  5. prompt size: characters, characters/4, under 15,000 estimated tokens
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import judge_codec as J  # noqa: E402
import s1a_make_prompt as P  # noqa: E402

REPO = P.REPO
SENTENCES = REPO / "runs" / "tests" / "t2_split_2026-09-16_2224" / "sentences_source.jsonl"
TOKEN_LIMIT = 15000
MIN_WORDS = 4


def normalize(s: str) -> str:
    return " ".join(s.replace(P.NEWLINE_MARK, " ").split())


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import argparse
    ap = argparse.ArgumentParser(description="t3: gate test of the judge prompt and codes")
    ap.add_argument("--prompt-version", default="v1", choices=P.VERSIONS)
    args = ap.parse_args(argv)
    version = args.prompt_version
    prompt_file, labels_file, _ = P.prompt_paths(version)
    examples = P.examples_for(version)
    stamp = datetime.now()
    tag = "" if version == "v1" else f"{version}_"
    folder = REPO / "runs" / "tests" / f"t3_prompt_{tag}{stamp:%Y-%m-%d_%H%M}"
    folder.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    details: list[str] = []
    verdicts: list[bool] = []

    def check(ok: bool, name: str, numbers: str):
        verdicts.append(ok)
        lines.append(f"- {'PASS' if ok else 'FAIL'} — {name} — {numbers}")
        print(lines[-1])

    prompt = prompt_file.read_text(encoding="utf-8")
    labels_data = json.loads(labels_file.read_text(encoding="utf-8"))
    shutil.copy(prompt_file, folder / prompt_file.name)
    shutil.copy(labels_file, folder / labels_file.name)
    inv = J.Inventory.load(labels_file)
    scheme_file, summary_file = P.scheme_files(version)
    scheme_text = scheme_file.read_text(encoding="utf-8")
    summary_text = summary_file.read_text(encoding="utf-8")

    # ---- check 1: no-quote gate ----------------------------------------------------------
    norm_prompt = normalize(prompt)
    norm_item = normalize(P.item_prompt(summary_text))
    hits, exempt = [], []
    n_checked = 0
    per_trace = {}
    with open(SENTENCES, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            s = normalize(r["text"])
            if len(s.split()) < MIN_WORDS:
                continue
            n_checked += 1
            per_trace[r["trace_id"]] = per_trace.get(r["trace_id"], 0) + 1
            if s in norm_prompt:
                (exempt if s in norm_item else hits).append(f"{r['trace_id']} s{r['s']}: {s}")
    (folder / "hits.txt").write_text(
        "# non-exempt hits\n" + "\n".join(hits) + ("\n" if hits else "") +
        "# exempt (verbatim parts of the item prompt)\n" + "\n".join(exempt) + ("\n" if exempt else ""),
        encoding="utf-8")
    check(not hits, "check 1, no-quote gate (decision 6)",
          f"{n_checked} sentences with {MIN_WORDS}+ words searched ({', '.join(f'{t}: {n}' for t, n in sorted(per_trace.items()))}); "
          f"non-exempt hits {len(hits)}; exempt (verbatim parts of the item prompt) {len(exempt)}; listed in hits.txt")
    details.append("### Check 1: hits and exemptions\n\n```\n" + "\n".join(["non-exempt hits:"] + (hits or ["(none)"]) +
                   ["", "exempt (verbatim parts of the item prompt):"] + (exempt or ["(none)"])) + "\n```")

    # ---- check 2: inventory ----------------------------------------------------------------
    inventory = P.build_inventory(scheme_text)
    paths = [" > ".join(e["path"]) for e in inventory]
    codes = [e["code"] for e in inventory]
    json_codes = [e["code"] for e in labels_data["paths"]]
    json_paths = [" > ".join(e["path"]) for e in labels_data["paths"]]
    ok = (len(set(codes)) == len(codes) == len(set(paths)) == len(paths) == len(inv)
          and json_codes == codes and json_paths == paths
          and all(inv.code_to_path[c] == p and inv.path_to_code[p] == c for c, p in zip(codes, paths))
          and all(len(e["path"]) >= 2 for e in inventory)
          and labels_data.get("version") == version)
    by_len = {2: sum(1 for e in inventory if len(e["path"]) == 2), 3: sum(1 for e in inventory if len(e["path"]) == 3)}
    check(ok, "check 2, inventory and codes",
          f"{len(paths)} paths ({by_len[2]} at Level 2, {by_len[3]} at Level 3), {len(set(codes))} unique codes, "
          f"each code decodes to its path and back; {labels_file.name} matches the parse of {scheme_file.name}")

    # ---- check 3: prompt contents --------------------------------------------------------
    missing_l1 = [n for n in P.L1_NAMES if n not in prompt]
    missing_opt = [c for c in (f"Re.oe.{x}" for x in "ABCDEF") if c not in prompt]
    has_output_section = P.SECTION_TITLES[5] in prompt
    has_examples_section = P.SECTION_TITLES[6] in prompt
    ex_results = []
    for k, ex in enumerate(examples, start=1):
        present = P.example_input(ex) in prompt and ex["expected"] in prompt and ex["title"] in prompt
        try:
            labels = J.parse_reply(ex["expected"], len(ex["sentences"]), inv)
            parses = len(labels) == len(ex["sentences"])
        except J.ReplyError as e:
            parses = False
            labels = None
        ex_results.append((k, present, parses, len(ex["sentences"])))
    ok = (not missing_l1 and not missing_opt and has_output_section and has_examples_section
          and all(pr and pa for _, pr, pa, _ in ex_results) and len(ex_results) == 3)
    check(ok, "check 3, prompt contents",
          f"Level 1 names missing {missing_l1 or 'none'}; option codes missing {missing_opt or 'none'}; "
          f"output-format section {'present' if has_output_section else 'MISSING'}; worked examples "
          + "; ".join(f"{k}: {'present' if pr else 'MISSING'}, expected output {'parses' if pa else 'DOES NOT PARSE'} ({n} sentences)" for k, pr, pa, n in ex_results))

    # ---- check 4: pytest -----------------------------------------------------------------
    cmd = [sys.executable, "-m", "pytest", "-q", "scripts/tests"]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    pytest_out = proc.stdout + (("\n" + proc.stderr) if proc.stderr.strip() else "")
    (folder / "pytest_output.txt").write_text(pytest_out, encoding="utf-8")
    check(proc.returncode == 0, "check 4, pytest on scripts/tests",
          f"exit code {proc.returncode}; last line: {pytest_out.strip().splitlines()[-1] if pytest_out.strip() else '(no output)'}")

    # ---- check 5: size -------------------------------------------------------------------
    chars = len(prompt)
    est = round(chars / 4)
    check(est < TOKEN_LIMIT, "check 5, prompt size", f"{chars} characters, about {est} tokens (characters/4); "
          f"{'under' if est < TOKEN_LIMIT else 'NOT under'} {TOKEN_LIMIT} estimated tokens")

    # ---- config and report ----------------------------------------------------------------
    config = {
        "git_commit": P.git_head(),
        "prompt_version": version,
        "scheme": scheme_file.name, "scheme_sha256": P.sha256_of_file(scheme_file),
        "summary": summary_file.name, "summary_sha256": P.sha256_of_file(summary_file),
        "prompt": prompt_file.name, "prompt_sha256": P.sha256_of_file(prompt_file),
        "labels": labels_file.name, "labels_sha256": P.sha256_of_file(labels_file),
        "sentences": SENTENCES.relative_to(REPO).as_posix(), "sentences_sha256": P.sha256_of_file(SENTENCES),
        "script": Path(__file__).resolve().relative_to(REPO).as_posix(),
        "python": sys.version.split()[0],
        "timestamp": stamp.isoformat(timespec="seconds"),
    }
    (folder / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    gate = all(verdicts)
    report = [
        f"# TEST_REPORT — t3_prompt — {stamp:%Y-%m-%d %H:%M}",
        "",
        f"Gate test of pipeline step (3/9), the judge prompt and the label codes (`scripts/s1a_make_prompt.py`, `scripts/judge_codec.py`), per pipeline v1 Section 9 item 5. Prompt version {version} (`{prompt_file.name}`, `{labels_file.name}`). "
        f"Git commit at run time: `{config['git_commit']}`. Scheme `{scheme_file.name}` sha256 `{config['scheme_sha256']}`; prompt sha256 `{config['prompt_sha256']}`. Python {config['python']}. Offline; API cost $0.",
        "",
        f"## Result: {'PASS' if gate else 'FAIL'} ({sum(verdicts)}/{len(verdicts)} checks passed)",
        "",
        "## Checks",
        "",
        *lines,
        "",
        "## Files produced",
        "",
        f"- `{folder.relative_to(REPO).as_posix()}/TEST_REPORT.md` (this file)",
        f"- `{prompt_file.name}`, `{labels_file.name}` — copies of the generated prompt and inventory",
        f"- `hits.txt` — {len(hits)} non-exempt hits, {len(exempt)} exemptions",
        "- `pytest_output.txt`, `config.json`",
        "",
        "## pytest output",
        "",
        "```",
        pytest_out.rstrip(),
        "```",
        "",
        *details,
    ]
    (folder / "TEST_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"\nReport: {folder / 'TEST_REPORT.md'}\nGate: {'PASS' if gate else 'FAIL'}")
    return 0 if gate else 1


if __name__ == "__main__":
    sys.exit(main())
