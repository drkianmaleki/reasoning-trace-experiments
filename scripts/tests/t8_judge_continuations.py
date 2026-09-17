#!/usr/bin/env python3
"""t8_judge_continuations -- test of pipeline step (8/9) (pipeline v2, Section 9 item 10): s3 in
dry run on the three smoke continuations of t7, then one real 3-request batch on them (cents);
the report lists each continuation's first new node and block sequence.

  python scripts/tests/t8_judge_continuations.py [--smoke runs/tests/t7_resample_<stamp>/smoke] [--poll-seconds 30]
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import s1_judge as S  # noqa: E402
import s3_judge_continuations as S3  # noqa: E402

REPO = S.REPO


def latest_smoke() -> Path | None:
    cands = sorted(p for p in (REPO / "runs" / "tests").glob("t7_resample_*/smoke") if (p / "continuations.jsonl").exists())
    return cands[-1] if cands else None


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", help="the t7 smoke folder (default: the latest)")
    ap.add_argument("--poll-seconds", type=int, default=30)
    args = ap.parse_args(argv)
    smoke = Path(args.smoke) if args.smoke else latest_smoke()
    stamp = datetime.now()
    folder = REPO / "runs" / "tests" / f"t8_judge_continuations_{stamp:%Y-%m-%d_%H%M}"
    folder.mkdir(parents=True, exist_ok=True)
    lines, verdicts, details = [], [], []

    def check(ok, name, numbers):
        verdicts.append(ok)
        lines.append(f"- {'PASS' if ok else 'FAIL'} — {name} — {numbers}")
        print(lines[-1])

    cost = 0.0
    if smoke is None:
        check(False, "check 1, smoke folder", "no t7 smoke folder with continuations.jsonl found")
    else:
        d = S3.run(smoke, folder / "dry", dry_run=True, log=lambda s: None)
        proj = d["projection"]
        cc = d["collections"].get("continuations_c004", {})
        ok = set(d["collections"]) == {"continuations_c004"} and cc.get("documents") == 3 and (folder / "dry" / "continuations_c004" / "requests").exists()
        check(ok, "check 1, s3 dry run on the smoke folder: documents built, cost projected",
              f"collections {list(d['collections'])}; documents {cc.get('documents')}, sentences {cc.get('sentences')}, "
              f"prefix sentences shown {cc.get('prefix_sentences')}; projected cost ${proj['total_cost_est_usd']:.3f} at batch prices "
              f"(rates {proj['rates']['thinking_per_sentence']:.0f} thinking + {proj['rates']['label_per_sentence']:.0f} label tokens per sentence, {proj['rates']['text_per_sentence']} text tokens per sentence)")
        try:
            s = S3.run(smoke, folder / "judge", no_noise=True, poll_seconds=args.poll_seconds, log=print)
        except Exception as e:
            check(False, "check 2, the real batch", f"error: {str(e)[:300]}")
            s = None
        if s is not None:
            cost = s["cost_usd"]
            c = s["collections"]["continuations_c004"]
            ok = s.get("stopped") is None and c.get("valid") == 3
            check(ok, "check 2, one real batch of three continuation requests: submitted, polled, parsed",
                  f"valid {c.get('valid')} of 3, failed {c.get('failed')}, retry {c.get('retry_parsed')}; cost ${cost:.4f}; stopped {s.get('stopped')}")
            blocks_path = folder / "judge" / "continuations_c004" / "blocks_continuations_c004_judge.jsonl"
            blocks = [json.loads(l) for l in blocks_path.read_text(encoding="utf-8").splitlines()] if blocks_path.exists() else []
            rows = ["## The three continuations (cut(C-B00), prefix s0-s7 labeled)", "", "| continuation | continuation sentences | first new node | L1 | opens block (rule) | first sentence is Wait | block sequence from the cut |", "|---|---|---|---|---|---|---|"]
            for b in blocks:
                fn = b["first_new_node"]
                rows.append(f"| {b['trace_id']} | {b['n_cont']} | {fn['name']} | {fn['L1']} | {fn['opens_block']} ({fn['opener_rule']}) | {b['first_sentence_r4']} | {S.block_sequence_text(b).replace('|', '\\|')[:600]} |")
            details.append("\n".join(rows))
            pn = folder / "judge" / f"pnext_{smoke.name}.csv"
            check(len(blocks) == 3 and pn.exists(), "check 3, derivation with R1-R4: first new node and block sequence per continuation, pnext written",
                  "; ".join(f"{b['trace_id']}: {b['first_new_node']['name']} ({b['first_new_node']['L1']}, opens {b['first_new_node']['opens_block']}), {len(b['cont_blocks'])} blocks from the cut" for b in blocks)
                  + f"; pnext file {pn.name if pn.exists() else 'MISSING'}")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "scripts/tests"], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    out = proc.stdout + (("\n" + proc.stderr) if proc.stderr.strip() else "")
    (folder / "pytest_output.txt").write_text(out, encoding="utf-8")
    check(proc.returncode == 0, "check 4, pytest on scripts/tests", f"exit code {proc.returncode}; last line: {out.strip().splitlines()[-1] if out.strip() else '(none)'}")
    gate = all(verdicts)
    report = [f"# TEST_REPORT — t8_judge_continuations — {stamp:%Y-%m-%d %H:%M}", "",
              f"Test of pipeline step (8/9) (`scripts/s3_judge_continuations.py` over `scripts/s1_judge.py` batch mode), per pipeline v2 Section 9 item 10. Git commit `{S.git_head()}`. "
              f"Smoke folder `{smoke.relative_to(REPO).as_posix() if smoke else 'none'}`; judge Sonnet 5 × prompt v3 × thinking low, batch prices. API cost ${cost:.4f}.", "",
              f"## Result: {'PASS' if gate else 'FAIL'} ({sum(verdicts)}/{len(verdicts)} checks passed)", "", "## Checks", "", *lines, "", *details, "",
              "## pytest output", "", "```", out.rstrip(), "```"]
    (folder / "TEST_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"\nReport: {folder / 'TEST_REPORT.md'}\nGate: {'PASS' if gate else 'FAIL'}\nAPI cost: ${cost:.4f}")
    return 0 if gate else 1


if __name__ == "__main__":
    sys.exit(main())
