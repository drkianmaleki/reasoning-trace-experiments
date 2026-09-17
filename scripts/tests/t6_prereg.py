#!/usr/bin/env python3
"""t6_prereg -- test of pipeline step (6/9), the pre-registration (pipeline v2, Section 9 item 8).
Offline.  Writes runs/tests/t6_prereg_<date>_<hhmm>/TEST_REPORT.md.

Checks: the registration file is in docs/shared and committed (git log shows it, the earliest
commit being the registration timestamp); the block-end cut list computed from listing v4 under
R4 equals Section 3 items 3 and 4 of the text and the lists pinned in scripts/s2_resample.py;
n = 25, n_0 = 100, the two ceilings and the stopping rule are present in the text; pytest.
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
import derivation as D  # noqa: E402
import s2_resample as R  # noqa: E402

REPO = R.REPO
PREREG = REPO / "docs" / "shared" / "2026-09-17_preregistration_stage1_v1.md"
PHRASES = {"n = 25": "n = 25 continuations per cut", "n_0 = 100": "n_0 = 100", "DeepInfra ceiling $45": "DeepInfra $45",
           "Claude ceiling $80": "Claude $80", "stopping rule": "if P̂_m = 1, M := m", "denominator": '"?" in the denominator'}


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    stamp = datetime.now()
    folder = REPO / "runs" / "tests" / f"t6_prereg_{stamp:%Y-%m-%d_%H%M}"
    folder.mkdir(parents=True, exist_ok=True)
    lines, verdicts = [], []

    def check(ok, name, numbers):
        verdicts.append(ok)
        lines.append(f"- {'PASS' if ok else 'FAIL'} — {name} — {numbers}")
        print(lines[-1])

    exists = PREREG.exists()
    log = subprocess.run(["git", "log", "--format=%H %ad %s", "--date=iso", "--follow", "--", str(PREREG.relative_to(REPO))],
                         cwd=REPO, capture_output=True, text=True).stdout.strip().splitlines() if exists else []
    earliest = log[-1] if log else None
    check(exists and bool(log), "check 1, the registration file is in docs/shared and committed",
          f"exists {exists}; commits {len(log)}; registration timestamp (earliest commit): {earliest}")
    text = PREREG.read_text(encoding="utf-8") if exists else ""
    m3 = re.search(r"The 46 block-end sentence indices, in order: (.*?) \(cut\(B_46\)", text, re.S)
    m4 = re.search(r"the 37 block-end indices (.*?)\.\n", text, re.S)
    c_text = [int(x) for x in re.findall(r"s(\d+)", m3.group(1))] if m3 else []
    e_text = [int(x) for x in re.findall(r"s(\d+)", m4.group(1))] if m4 else []
    design = R.load_design()
    c_der, e_der = design["traces"]["c004"]["block_ends"], design["traces"]["e036"]["block_ends"]
    ok = c_text == c_der == R.REGISTERED_ENDS["c004"] and e_text == e_der == R.REGISTERED_ENDS["e036"] and len(c_text) == 46 and len(e_text) == 37
    check(ok, "check 2, the cut list of Section 3 items 3-4 equals the block ends derived from listing v4 under R4 and the pinned lists",
          f"text C {len(c_text)} / E {len(e_text)} indices; derived C {len(c_der)} / E {len(e_der)}; equal {ok}; C first/last s{c_text[:1]}…s{c_text[-1:]}, E s{e_text[:1]}…s{e_text[-1:]}")
    found = {k: (p in text) for k, p in PHRASES.items()}
    check(all(found.values()), "check 3, n, n_0, the ceilings and the stopping rule are stated", "; ".join(f"{k}: {'present' if v else 'MISSING'}" for k, v in found.items()))
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "scripts/tests"], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    out = proc.stdout + (("\n" + proc.stderr) if proc.stderr.strip() else "")
    (folder / "pytest_output.txt").write_text(out, encoding="utf-8")
    check(proc.returncode == 0, "check 4, pytest on scripts/tests", f"exit code {proc.returncode}; last line: {out.strip().splitlines()[-1] if out.strip() else '(none)'}")
    gate = all(verdicts)
    (folder / "config.json").write_text(json.dumps({"prereg": PREREG.relative_to(REPO).as_posix(), "prereg_sha256": R.sha256_text(text), "git_log": log,
                                                    "git_commit": R.git_head(), "timestamp": stamp.isoformat(timespec="seconds")}, indent=2) + "\n", encoding="utf-8")
    report = [f"# TEST_REPORT — t6_prereg — {stamp:%Y-%m-%d %H:%M}", "",
              f"Test of pipeline step (6/9), the pre-registration `{PREREG.relative_to(REPO).as_posix()}` (sha256 `{R.sha256_text(text)}`), per pipeline v2 Section 9 item 8. Git commit `{R.git_head()}`. Offline; API cost $0.", "",
              f"## Result: {'PASS' if gate else 'FAIL'} ({sum(verdicts)}/{len(verdicts)} checks passed)", "", "## Checks", "", *lines, "",
              "## git log of the registration file", "", "```", *log, "```", "", "## pytest output", "", "```", out.rstrip(), "```"]
    (folder / "TEST_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"\nReport: {folder / 'TEST_REPORT.md'}\nGate: {'PASS' if gate else 'FAIL'}")
    return 0 if gate else 1


if __name__ == "__main__":
    sys.exit(main())
