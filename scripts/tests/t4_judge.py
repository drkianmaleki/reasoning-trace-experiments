#!/usr/bin/env python3
"""t4_judge -- test of pipeline step (4/9), the judge on the two source traces (pipeline v1,
Section 9 item 6).  Two ordinary calls to Claude Haiku 4.5 (cents).

Writes runs/tests/t4_judge_<YYYY-MM-DD>_<HHMM>/TEST_REPORT.md and runs the judge into
runs/experiments/judge_source_<YYYY-MM-DD>_<HHMM>/.  Order:
  1. derivation gate on the reviewed labels (offline; FAIL stops everything before any call)
  2. dry run: both requests built, token estimates, every index once in the user message
  3. e036: the call, attempts, validity, tokens, cost, node/block counts vs 146/37, agreement
  4. c004: the same (193/46)
  5. agreement table and residue copied into the test folder; confusion pairs; total cost
  6. pytest on scripts/tests
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
import derivation as D  # noqa: E402
import s1_judge as S  # noqa: E402

REPO = S.REPO
SENTENCES = REPO / "runs" / "tests" / "t2_split_2026-09-16_2224" / "sentences_source.jsonl"
EXPECTED = {"e036": {"nodes": 146, "blocks": 37}, "c004": {"nodes": 193, "blocks": 46}}
ORDER = ["e036", "c004"]


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import argparse
    ap = argparse.ArgumentParser(description="t4: the judge on the two source traces")
    ap.add_argument("--model", choices=tuple(S.MODELS), default="haiku")
    ap.add_argument("--prompt-version", choices=S.PROMPT_VERSIONS, default="v1")
    args = ap.parse_args(argv)
    model_key, version = args.model, args.prompt_version
    stamp = datetime.now()
    folder = REPO / "runs" / "tests" / f"t4_judge_{model_key}_{version}_{stamp:%Y-%m-%d_%H%M}"
    folder.mkdir(parents=True, exist_ok=True)
    run_dir = REPO / "runs" / "experiments" / S.make_run_id(model_key, version, stamp)
    prompt_file, labels_file = S.prompt_files(version)
    lines: list[str] = []
    details: list[str] = []
    verdicts: list[bool] = []

    def check(ok: bool, name: str, numbers: str):
        verdicts.append(ok)
        lines.append(f"- {'PASS' if ok else 'FAIL'} — {name} — {numbers}")
        print(lines[-1])

    def write_report(final: bool):
        gate = all(verdicts)
        text = [
            f"# TEST_REPORT — t4_judge — {stamp:%Y-%m-%d %H:%M}",
            "",
            f"Test of pipeline step (4/9), the judge on the two source traces (`scripts/s1_judge.py`, `scripts/derivation.py`), per pipeline v1 Section 9 item 6. "
            f"Git commit `{S.git_head()}`; model `{S.MODELS[model_key]['id']}` ({model_key}), max_tokens {S.MAX_TOKENS}, temperature {S.MODELS[model_key]['temperature']} "
            f"({'via extra_body' if S.MODELS[model_key]['temperature'] is not None else 'not sent: the model rejects sampling parameters'}), thinking {S.MODELS[model_key]['thinking'] or 'omitted'}; "
            f"prompt {version} sha256 `{S.sha256_of_file(prompt_file)}`; inventory sha256 `{S.sha256_of_file(labels_file)}`; sentences `{SENTENCES.relative_to(REPO).as_posix()}`. "
            f"Run folder `{run_dir.relative_to(REPO).as_posix()}`.",
            "",
            f"## Result: {'PASS' if gate else 'FAIL'} ({sum(verdicts)}/{len(verdicts)} checks passed){'' if final else ' — STOPPED EARLY'}",
            "",
            "## Checks",
            "",
            *lines,
            "",
            *details,
        ]
        (folder / "TEST_REPORT.md").write_text("\n".join(text) + "\n", encoding="utf-8")

    # ---- 1. derivation gate on the reviewed labels ----------------------------------------------
    listing = D.parse_listing()
    gate_ok = True
    nums = []
    for tid in ORDER:
        g = D.gate(tid, listing[tid]["labels"], listing[tid])
        gate_ok &= g["pass"]
        nums.append(f"{tid}: {g['sentences']} sentences; blocks {g['blocks_derived']} derived vs {g['blocks_expected']} listed; "
                    f"nodes {g['nodes_derived']} vs {g['nodes_expected']}; interval differences {len(g['block_diffs'])}, "
                    f"opener rule/label differences {len(g['rule_diffs'])}, name differences {len(g['name_diffs'])} "
                    f"(listing names with a '(1)' count stripped: {g['names_normalized']})")
        if not g["pass"]:
            details.append(f"### Derivation differences, {tid}\n\n```\n" + json.dumps({k: g[k] for k in ('block_diffs', 'rule_diffs', 'name_diffs')}, ensure_ascii=False, indent=1)[:6000] + "\n```")
    check(gate_ok, "check 1, derivation gate on the reviewed labels (offline)", "; ".join(nums))
    if not gate_ok:
        write_report(final=False)
        print("Derivation gate FAILED: no API call made.")
        return 1

    # ---- 2. dry run -----------------------------------------------------------------------------
    dry = S.run_judge(SENTENCES, folder / "dry_run", ORDER, dry_run=True, log=lambda s: None,
                      model_key=model_key, prompt_version=version)
    nums = []
    ok = True
    for tid in ORDER:
        req = json.loads((folder / "dry_run" / "requests" / f"{tid}.json").read_text(encoding="utf-8"))
        content = req["messages"][0]["content"]
        idx = [int(m.group(1)) for l in content.split("\n") for m in [re.match(r"^s(\d+): ", l)] if m]
        n = dry["traces"][tid]["n"]
        once = idx == list(range(n))
        m = S.MODELS[model_key]
        ok &= once and req["system"][0]["cache_control"] == {"type": "ephemeral"} and req["model"] == m["id"]
        ok &= (req.get("extra_body") == {"temperature": m["temperature"]}) if m["temperature"] is not None else ("extra_body" not in req)
        ok &= (req.get("thinking") == m["thinking"]) if m["thinking"] is not None else ("thinking" not in req)
        nums.append(f"{tid}: {n} sentences, about {dry['traces'][tid]['estimated_input_tokens']} input tokens (characters/4); "
                    f"every index exactly once in the user message: {once}")
    check(ok, "check 2, dry run (requests built, nothing called)", "; ".join(nums) + "; requests written to dry_run/requests/")

    # ---- 3 and 4. the calls, e036 first --------------------------------------------------------------
    try:
        client = S.make_client()
    except Exception as e:
        check(False, "check 3, Claude client", f"cannot create the client: {e}")
        write_report(final=False)
        return 1
    summary = S.run_judge(SENTENCES, run_dir, ORDER, dry_run=False, client=client, reviewed_path=D.LISTING,
                          model_key=model_key, prompt_version=version)
    for k, tid in enumerate(ORDER, start=3):
        t = summary["traces"].get(tid, {})
        if "valid" not in t:
            check(False, f"check {k}, {tid}", "not run (the run stopped earlier)")
            continue
        u = t.get("usage", {})
        exp = EXPECTED[tid]
        counts_ok = t.get("valid") and t.get("nodes") is not None
        agr = summary.get("agreement")
        agr_txt = ""
        if agr and t.get("valid"):
            # per-trace agreement summary
            sub = per_trace_levels(summary, tid, listing)
            agr_txt = "; agreement (this trace): " + ", ".join(
                f"{LEVEL_SHORT[lv['level']]} exact {lv['exact_match']:.3f} kappa {lv['kappa']:.3f}" for lv in sub["levels"]) + f"; residue rows {len(sub['residue'])}"
        check(bool(counts_ok), f"check {k}, {tid} judged",
              f"attempts {t.get('attempts')}, valid {t.get('valid')}, model echoed {t.get('model')!r}, stop reasons {t.get('stop_reasons')}; "
              f"tokens input {u.get('input_tokens')}, cache read {u.get('cache_read_input_tokens')}, cache write {u.get('cache_creation_input_tokens')}, "
              f"output {u.get('output_tokens')}; cost ${t.get('cost_usd', 0):.6f}; judge nodes {t.get('nodes')} / blocks {t.get('blocks')} "
              f"vs reviewed {exp['nodes']} / {exp['blocks']}" + (f"; retry message: {t.get('retry_message')}" if t.get('retry_message') else "")
              + (f"; error: {t.get('error')}" if t.get('error') else "") + agr_txt)
    if summary["stopped"]:
        check(False, "run", f"stopped: {summary['stopped']}")

    # ---- 5. agreement artifacts -------------------------------------------------------------------
    agr = summary.get("agreement")
    if agr:
        for p in summary["agreement_paths"]:
            shutil.copy(p, folder / Path(p).name)
        for name in ("labels_source_judge.jsonl", "blocks_source_judge.jsonl", "config.json", "_log.txt"):
            if (run_dir / name).exists():
                shutil.copy(run_dir / name, folder / name)
        lv = {x["level"]: x for x in agr["levels"]}
        check(True, "check 5, agreement over both traces",
              f"{agr['n']} sentences; " + "; ".join(f"{LEVEL_SHORT[l]}: exact {lv[l]['exact_match']:.3f}, Jaccard {lv[l]['mean_jaccard']:.3f}, kappa {lv[l]['kappa']:.3f}" for l in (1, 2, 3))
              + f"; residue rows {len(agr['residue'])}; total cost ${summary['total_cost_usd']:.6f}; agreement_source.csv, residue_source.csv, confusions_source.csv copied here")
        details.append(agreement_markdown(agr))
    else:
        check(False, "check 5, agreement", "no agreement computed (the run stopped)")

    # ---- 6. pytest ----------------------------------------------------------------------------------
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "scripts/tests"], cwd=REPO, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", env=env)
    out = proc.stdout + (("\n" + proc.stderr) if proc.stderr.strip() else "")
    (folder / "pytest_output.txt").write_text(out, encoding="utf-8")
    check(proc.returncode == 0, "check 6, pytest on scripts/tests", f"exit code {proc.returncode}; last line: {out.strip().splitlines()[-1] if out.strip() else '(none)'}")
    details.append("## pytest output\n\n```\n" + out.rstrip() + "\n```")
    (folder / "summary.json").write_text(json.dumps({k: v for k, v in summary.items() if k != "agreement"}, indent=2, default=str) + "\n", encoding="utf-8")
    write_report(final=True)
    print(f"\nReport: {folder / 'TEST_REPORT.md'}\nGate: {'PASS' if all(verdicts) else 'FAIL'}\nTotal API cost: ${summary['total_cost_usd']:.6f}")
    return 0 if all(verdicts) else 1


LEVEL_SHORT = {1: "Level 1", 2: "Level 2", 3: "Level 3"}


def per_trace_levels(summary: dict, tid: str, listing: dict) -> dict:
    """Agreement restricted to one trace, recomputed from the run's label file."""
    judge = {}
    with open(summary["labels_path"], encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r["trace_id"] == tid:
                judge.setdefault(tid, []).append([S.path_of(l) for l in r["labels"]])
    return S.agreement(judge, {tid: listing[tid]["labels"]}, {tid: listing[tid]["texts"]})


def agreement_markdown(agr: dict) -> str:
    out = ["## Agreement (judge vs reviewed, both traces)", "", "| level | n | exact-match rate | mean Jaccard | kappa (primary label) | primary agreement |", "|---|---|---|---|---|---|"]
    for lv in agr["levels"]:
        out.append(f"| {lv['name']} | {lv['n']} | {lv['exact_match']:.4f} | {lv['mean_jaccard']:.4f} | {lv['kappa']:.4f} | {lv['primary_agreement']:.4f} |")
    out += ["", "| level | label | n_reviewed | n_judge | tp | precision | recall | F1 |", "|---|---|---|---|---|---|---|---|"]
    for r in agr["per_label"]:
        out.append(f"| {r['level']} | {r['label']} | {r['n_reviewed']} | {r['n_judge']} | {r['tp']} | {r['precision']:.3f} | {r['recall']:.3f} | {r['f1']:.3f} |")
    for level in (1, 2):
        out += ["", f"### Twenty most frequent confusion pairs at Level {level} (reviewed → judge, primary label)", "", "| reviewed | judge | count |", "|---|---|---|"]
        for (a, b), c in agr["confusions"][level]:
            out.append(f"| {a} | {b} | {c} |")
    out += ["", f"### Residue: {len(agr['residue'])} sentences whose full-path set differs (first thirty)", "", "| trace | s | reviewed | judge | text |", "|---|---|---|---|---|"]
    for r in agr["residue"][:30]:
        out.append(f"| {r['trace_id']} | {r['s']} | {r['reviewed']} | {r['judge']} | {r['text'].replace('|', '\\|')} |")
    return "\n".join(out)


if __name__ == "__main__":
    sys.exit(main())
