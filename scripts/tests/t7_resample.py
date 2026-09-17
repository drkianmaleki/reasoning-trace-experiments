#!/usr/bin/env python3
"""t7_resample -- test of pipeline step (7/9), the sampling script (pipeline v2, Section 9 item 9).

  python scripts/tests/t7_resample.py [--skip-api]

Part (i), offline replay: the scorer reproduces the archived per-prefix table
(runs/resample_cuts_2026-08-25_1503_summary.csv) from the archived continuations; the stopping
rule of registration 3.6 replayed on that table (P_hat of a_T with "?" in the denominator) stops
both arms at old cut-62; the Tk-by-prompt_tokens rule on the archived prefixes gives positive
differences whose sum equals prompt_tokens(last cut) - prompt_tokens(cut-0).
Part (ii), API smoke into runs/tests/t7_resample_<stamp>/smoke/: the no-think prefill with 10
samples (none reopens <think>; every reply resolves to a letter or "?"), then 3 continuations
from cut(C-B00) in the record format (prompt, usage, letters, chosen) with _log.txt.  About $0.15.
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import s2_resample as R  # noqa: E402
import scorer as SC  # noqa: E402

REPO = R.REPO
ARCHIVED = REPO / "archive" / "decided-mid-thought" / "runs" / "resample_cuts_2026-08-25_1503.jsonl"
SUMMARY = REPO / "archive" / "decided-mid-thought" / "runs" / "resample_cuts_2026-08-25_1503_summary.csv"
PREFIXES = REPO / "archive" / "decided-mid-thought" / "runs" / "resample_cuts_2026-08-25_1503_prefixes.json"
ARCHIVED_ORDER = {"c004": [15, 29, 44, 58, 59, 60, 61, 62, 63, 64, 67, 68, 69], "e036": [60, 61, 62, 63, 64, 65]}


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-api", action="store_true")
    args = ap.parse_args(argv)
    stamp = datetime.now()
    folder = REPO / "runs" / "tests" / f"t7_resample_{stamp:%Y-%m-%d_%H%M}"
    folder.mkdir(parents=True, exist_ok=True)
    lines, verdicts, details = [], [], []

    def check(ok, name, numbers):
        verdicts.append(ok)
        lines.append(f"- {'PASS' if ok else 'FAIL'} — {name} — {numbers}")
        print(lines[-1])

    # ---- (i) offline replay ---------------------------------------------------------------------
    records = [json.loads(l) for l in open(ARCHIVED, encoding="utf-8") if l.strip()]
    with open(SUMMARY, encoding="utf-8") as fh:
        expected = list(csv.DictReader(fh))
    rows = SC.archived_table(records, order=[r["prefix_id"] for r in expected])
    mism = [(g["prefix_id"], g["p_C"], e["p_C"], g["p_E"], e["p_E"]) for g, e in zip(rows, expected)
            if f"{g['p_C']}" != e["p_C"] or f"{g['p_E']}" != e["p_E"] or g["distribution"] != e["distribution"]]
    check(not mism and len(rows) == 20, "check 1, the scorer reproduces the archived per-prefix table", f"20 prefixes recomputed from cont_text; mismatches {len(mism)} {mism[:3]}")
    # stopping rule under registration 3.7 (single letter a_T over n)
    by_pid = {}
    for r in records:
        if r["seq"] < 900:
            by_pid.setdefault(r["prefix_id"], []).append(SC.score(r["cont_text"])["answer"])
    stops = {}
    phats = {}
    for arm, cuts in ARCHIVED_ORDER.items():
        a_t = R.A_T[arm]
        for k in cuts:
            ans = by_pid[f"rs0823_{arm}_cut{k:03d}"]
            phats[(arm, k)] = sum(1 for a in ans if a == a_t) / len(ans)
            if phats[(arm, k)] == 1.0 and arm not in stops:
                stops[arm] = k
    check(stops == {"c004": 62, "e036": 62}, "check 2, the stopping rule replayed on the archived table stops both arms at old cut-62",
          "; ".join(f"{arm}: " + ", ".join(f"cut{k} {phats[(arm, k)]:.2f}" for k in cuts) + f" -> stop at cut {stops.get(arm)}" for arm, cuts in ARCHIVED_ORDER.items()))
    # Tk by prompt_tokens
    pt = {}
    for r in records:
        pt.setdefault(r["prefix_id"], set()).add(r["usage"]["prompt_tokens"])
    constant = all(len(v) == 1 for v in pt.values())
    prefixes = json.load(open(PREFIXES, encoding="utf-8"))["prefixes"]
    tk_ok = constant
    tk_text = []
    for arm, cuts in ARCHIVED_ORDER.items():
        prev = next(iter(pt["rs0823_cut000"]))
        diffs = []
        for k in cuts:
            cur = next(iter(pt[f"rs0823_{arm}_cut{k:03d}"]))
            diffs.append(cur - prev)
            prev = cur
        total = prev - next(iter(pt["rs0823_cut000"]))
        chars = len(prefixes[f"rs0823_{arm}_cut{cuts[-1]:03d}"]["prefill"])
        tk_ok &= all(d > 0 for d in diffs) and sum(diffs) == total
        tk_text.append(f"{arm}: differences {diffs} (all positive {all(d > 0 for d in diffs)}), sum {sum(diffs)} = prompt_tokens(cut {cuts[-1]}) - prompt_tokens(cut-0) = {total}; "
                       f"last prefix {chars} characters ({chars / total:.2f} characters per token)")
    check(tk_ok, "check 3, Tk by prompt_tokens on the archived prefixes: positive differences summing to the recorded prefix length in tokens",
          f"prompt_tokens constant within every prefix: {constant}; " + "; ".join(tk_text))

    # ---- (ii) API smoke -------------------------------------------------------------------------
    cost = 0.0
    if args.skip_api:
        check(True, "check 4, API smoke", "skipped (--skip-api)")
    else:
        design = R.load_design()
        base = R.conditions(design, ["c004"], n=3, n0=10, max_cuts=1)
        conds = [c for c in base if c["condition"] in ("nothink", "cut")]
        smoke = folder / "smoke"
        try:
            s = R.run(smoke, design, conds, workers=4, log=print, label="t7 smoke")
        except Exception as e:
            check(False, "check 4, API smoke", f"error: {str(e)[:300]}")
            s = None
        if s is not None:
            cost = s["cost_usd"]
            recs = [json.loads(l) for l in (smoke / "continuations.jsonl").read_text(encoding="utf-8").splitlines()] if (smoke / "continuations.jsonl").exists() else []
            nothink = [r for r in recs if r["condition"] == "nothink"]
            cut = [r for r in recs if r["condition"] == "cut"]
            config = json.loads((smoke / "config.json").read_text(encoding="utf-8"))
            ok_nt = len(nothink) == 10 and not any(r["think_reopened"] for r in nothink) and all(r["answer"] in set("ABCDEF?") for r in nothink)
            check(config["slug_check"]["ok"], "check 4, slug check", f"status {config['slug_check']['status']}, model echoed {config['slug_check']['model_echoed']!r}")
            check(ok_nt, "check 5, no-think baseline, 10 samples: none reopens <think>, every reply resolves to a letter or ?",
                  f"{len(nothink)} records; reopened {sum(r['think_reopened'] for r in nothink)}; answers " + json.dumps({a: sum(1 for r in nothink if r["answer"] == a) for a in "ABCDEF?"})
                  + f"; mean completion tokens {sum(r['usage'].get('completion_tokens', 0) for r in nothink) / max(len(nothink), 1):.0f}; finish {sorted({r['finish'] for r in nothink})}")
            fields = {"prompt", "usage", "letters", "chosen", "answer", "cont_text", "think_closed", "finish", "seq", "block", "prefix_char_end", "condition"}
            ok_cut = len(cut) == 3 and all(fields <= set(r) for r in cut) and all(r["block"] == 0 and r["prefix_char_end"] == 450 for r in cut) \
                and all(r["prompt"].endswith(design["traces"]["c004"]["prefixes"][0]["text"]) for r in cut)
            check(ok_cut, "check 6, three continuations from cut(C-B00) in the record format",
                  f"{len(cut)} records; " + "; ".join(f"{r['id']}: letters {r['letters']}, answer {r['answer']}, closed {r['think_closed']}, finish {r['finish']}, "
                                                    f"tokens {r['usage'].get('prompt_tokens')}+{r['usage'].get('completion_tokens')}, ${r['cost_usd']:.4f}" for r in cut))
            log = (smoke / "_log.txt").read_text(encoding="utf-8") if (smoke / "_log.txt").exists() else ""
            dep = (smoke / "DEPARTURES.md").read_text(encoding="utf-8") if (smoke / "DEPARTURES.md").exists() else None
            check("rb_nothink" in log and "rb_c004_B00" in log and (smoke / "pcut.csv").exists(), "check 7, _log.txt and pcut.csv written",
                  f"log lines {len(log.splitlines())}; pcut rows {len(R.read_pcut(smoke / 'pcut.csv'))}; DEPARTURES.md lines {len(dep.splitlines()) if dep is not None else 'absent'}; cost ${cost:.4f}")
            details.append("## Smoke: no-think replies (first 120 characters)\n\n" + "\n".join(f"- {r['id']}: {r['answer']} — {r['cont_text'][:120]!r}" for r in nothink))
            details.append("## Smoke: cut(C-B00) continuations (first 200 characters)\n\n" + "\n".join(f"- {r['id']}: {r['answer']} — {r['cont_text'][:200]!r}" for r in cut))
            if dep:
                details.append("## DEPARTURES.md of the smoke\n\n```\n" + dep.rstrip() + "\n```")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "scripts/tests"], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    out = proc.stdout + (("\n" + proc.stderr) if proc.stderr.strip() else "")
    (folder / "pytest_output.txt").write_text(out, encoding="utf-8")
    check(proc.returncode == 0, "check 8, pytest on scripts/tests", f"exit code {proc.returncode}; last line: {out.strip().splitlines()[-1] if out.strip() else '(none)'}")
    gate = all(verdicts)
    report = [f"# TEST_REPORT — t7_resample — {stamp:%Y-%m-%d %H:%M}", "",
              f"Test of pipeline step (7/9), the sampling script (`scripts/s2_resample.py`, `scripts/scorer.py`), per pipeline v2 Section 9 item 9. Git commit `{R.git_head()}`. "
              f"Part (i) offline on the archived run; part (ii) API smoke in `{(folder / 'smoke').relative_to(REPO).as_posix()}` (model {R.MODEL}, stop {R.STOP}). API cost ${cost:.4f}.", "",
              f"## Result: {'PASS' if gate else 'FAIL'} ({sum(verdicts)}/{len(verdicts)} checks passed)", "", "## Checks", "", *lines, "", *details, "",
              "## pytest output", "", "```", out.rstrip(), "```"]
    (folder / "TEST_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"\nReport: {folder / 'TEST_REPORT.md'}\nGate: {'PASS' if gate else 'FAIL'}\nAPI cost: ${cost:.4f}")
    return 0 if gate else 1


if __name__ == "__main__":
    sys.exit(main())
