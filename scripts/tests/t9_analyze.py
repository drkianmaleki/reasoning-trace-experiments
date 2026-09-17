#!/usr/bin/env python3
"""t9_analyze -- test of pipeline step (9/9) (pipeline v2, Section 9 item 11): s4 on the archived
replay (the 500 archived continuations with the pilot's judge labels, the archived cuts treated
as cuts) and on the hand-made toys; every table and figure produced and opened.  Offline.

  python scripts/tests/t9_analyze.py [--judge runs/experiments/judge_archived500_2026-09-17_1334] [--draws 10000] [--perms 10000]
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
import derivation as D  # noqa: E402
import s2_resample as R  # noqa: E402
import s4_analyze as A  # noqa: E402
import scorer as SC  # noqa: E402

REPO = R.REPO
ARCHIVED = REPO / "archive" / "decided-mid-thought" / "runs" / "resample_cuts_2026-08-25_1503.jsonl"
JUDGE_DEFAULT = REPO / "runs" / "experiments" / "judge_archived500_2026-09-17_1334"
ARCHIVED_ORDER = {"c004": [15, 29, 44, 58, 59, 60, 61, 62, 63, 64, 67, 68, 69], "e036": [60, 61, 62, 63, 64, 65]}


def build_replay(folder: Path) -> dict:
    """pcut.csv and continuations.jsonl of the archived run in the new record format; the
    archived cut k (old numbering) becomes block_end_s = the last listing sentence with old_s = k;
    m = the cut's rank within its arm; no no-think row (never sampled in the archived run)."""
    folder.mkdir(parents=True, exist_ok=True)
    sents = {}
    with open(D.SENTENCES_SOURCE, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            sents.setdefault(r["trace_id"], []).append(r)
    end_of = {tid: {r["old_s"]: r["s"] for r in rs} for tid, rs in sents.items()}  # the last part of an old sentence wins
    records = [json.loads(l) for l in open(ARCHIVED, encoding="utf-8") if l.strip()]
    by_pid = {}
    for r in records:
        if r["seq"] < 900:
            by_pid.setdefault(r["prefix_id"], []).append(r)
    conds = [{"condition": "cut0", "trace_id": "shared", "m": None, "prefix_id": "rs0823_cut000", "block_end_s": None, "prefix_char_end": 0}]
    for arm, cuts in ARCHIVED_ORDER.items():
        for m, k in enumerate(cuts):
            conds.append({"condition": "cut", "trace_id": arm, "m": m, "prefix_id": f"rs0823_{arm}_cut{k:03d}", "block_end_s": end_of[arm][k],
                          "prefix_char_end": sents[arm][end_of[arm][k]]["char_end"], "old_cut": k})
    pcut_path, cont_path = folder / "pcut.csv", folder / "continuations.jsonl"
    if pcut_path.exists():
        pcut_path.unlink()
    prev_pt = {"c004": None, "e036": None}
    n_rows = 0
    with open(cont_path, "w", encoding="utf-8", newline="\n") as fh:
        for c in conds:
            recs = []
            for r in by_pid[c["prefix_id"]]:
                sc = SC.score(r["cont_text"])
                rec = {"id": r["id"], "prefix_id": c["prefix_id"], "trace_arm": c["trace_id"], "cut": c["block_end_s"], "block": c["m"], "condition": c["condition"],
                       "prefix_char_end": c["prefix_char_end"], "seq": r["seq"], "letters": sc["letters"], "answer": sc["answer"], "think_closed": sc["think_closed"],
                       "finish": r["finish"], "cont_len": r["cont_len"], "usage": r["usage"], "cost_usd": r["usage"].get("estimated_cost", 0.0), "old_cut": c.get("old_cut")}
                fh.write(json.dumps(rec) + "\n")
                recs.append(rec)
            prev = None
            if c["condition"] == "cut":
                prev = prev_pt[c["trace_id"]] if c["m"] > 0 else next(iter({x["usage"]["prompt_tokens"] for x in by_pid["rs0823_cut000"]}))
            row = R.summarize(recs, c, R.A_T.get(c["trace_id"]), prev)
            R.write_pcut_row(pcut_path, row)
            if c["condition"] == "cut":
                prev_pt[c["trace_id"]] = row["prompt_tokens"]
            n_rows += 1
    return {"conditions": n_rows, "continuations": sum(len(v) for v in by_pid.values()), "block_ends": {arm: [end_of[arm][k] for k in cuts] for arm, cuts in ARCHIVED_ORDER.items()}}


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", default=str(JUDGE_DEFAULT))
    ap.add_argument("--draws", type=int, default=10000)
    ap.add_argument("--perms", type=int, default=10000)
    args = ap.parse_args(argv)
    stamp = datetime.now()
    folder = REPO / "runs" / "tests" / f"t9_analyze_{stamp:%Y-%m-%d_%H%M}"
    folder.mkdir(parents=True, exist_ok=True)
    lines, verdicts, details = [], [], []

    def check(ok, name, numbers):
        verdicts.append(ok)
        lines.append(f"- {'PASS' if ok else 'FAIL'} — {name} — {numbers}")
        print(lines[-1])

    # ---- the archived replay ---------------------------------------------------------------------
    replay = folder / "archived_replay"
    info = build_replay(replay)
    judge = Path(args.judge)
    blocks_file = judge / "blocks_archived500_judge.jsonl"
    check(info["conditions"] == 20 and info["continuations"] == 500 and blocks_file.exists(), "check 1, the archived replay built (pcut.csv, continuations.jsonl) and the pilot's judge labels present",
          f"{info['conditions']} conditions, {info['continuations']} continuations; block-end indices (listing numbering) {json.dumps(info['block_ends'])}; judge blocks file {'present' if blocks_file.exists() else 'ABSENT (git-ignored; held locally by Kian)'}")
    res = A.analyze(replay, judge if blocks_file.exists() else None, folder / "analysis_archived", draws=args.draws, perms=args.perms, seed=0, log=print)
    tables = [folder / "analysis_archived" / t for t in res["tables"]]
    opened = {}
    for t in tables:
        if t.suffix == ".csv":
            with open(t, encoding="utf-8") as fh:
                opened[t.name] = len(list(csv.DictReader(fh)))
        else:
            opened[t.name] = len(t.read_text(encoding="utf-8").splitlines())
    figs = [Path(p) for p in res["figures"]]
    figs_ok = len(figs) == 4 and all(p.exists() and p.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n" and p.stat().st_size > 5000 for p in figs)
    may_be_empty = {"transition_noise.csv", "transition_history.csv", "transition_order.csv"}  # no second labeling in the archived replay; pairs need three cuts a side
    core_ok = all(v > 0 for k, v in opened.items() if k not in may_be_empty)
    check(core_ok and figs_ok and len(opened) == 11, "check 2, every table and figure of the archived replay produced and opened (the noise table is empty by construction here)",
          "; ".join(f"{k}: {v} rows" for k, v in opened.items()) + "; figures " + ", ".join(p.name for p in figs))
    med = {s["trace_id"]: s for s in res["mediation"]}
    perm = {r["scope"]: r for r in res["permutation"]}
    m_ok = med["c004"]["M"] == 12 and med["e036"]["M"] == 5 and abs(med["c004"]["p_cut0"] - 0.12) < 1e-9 and abs(med["e036"]["p_cut0"] - 0.80) < 1e-9
    check(m_ok, "check 3, archived replay numbers (registration 3.7 scoring)",
          "; ".join(f"{t}: cuts {s['cuts_sampled']}, P(cut-0) {s['p_cut0']:.2f} -> P_M {s['p_M']:.2f}, B_top m={s['B_top']} (old cut {ARCHIVED_ORDER[t][s['B_top']]}) Δ {s['delta_top']:+.2f}, Tk(B_top) {s['tk_B_top']}, "
                    f"gap {s['gap']:.2f} [{s['gap_low']:.2f}, {s['gap_high']:.2f}], shares {s['share_top1']:.2f}/{s['share_top2']:.2f}/{s['share_top3']:.2f}, blocks to half {s['blocks_to_half']}" for t, s in med.items())
          + "; permutation: " + "; ".join(f"{k}: S {v['S_obs']:.3f}, p {v['p']:.4f}, cuts {v['cuts_included']}, groups {v['groups']}, singletons {v['singleton_X_excluded'] or '-'}" for k, v in perm.items()))
    details.append("## Archived replay: stage1_summary.md (head)\n\n" + "\n".join((folder / "analysis_archived" / "stage1_summary.md").read_text(encoding="utf-8").splitlines()[:60]))

    # ---- the toys ---------------------------------------------------------------------------------
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import test_s4_analyze as T4
    toy, toy_judge = T4.write_toy_run(folder / "toy", T4.ANSWERS, T4.META, {"rb_c004_B00": T4.labels_from({"Planning": 24, "Reasoning": 1}, 1),
                                                                            "rb_c004_B01": T4.labels_from({"Reasoning": 24, "Planning": 1}, 2),
                                                                            "rb_c004_B02": T4.labels_from({"Planning": 15, "Reasoning": 7, "Restatement": 3}, 3)})
    tres = A.analyze(toy, toy_judge, folder / "analysis_toy", draws=args.draws, perms=args.perms, seed=1, log=lambda s: None)
    s = tres["mediation"][0]
    hand = {"p_cut0": 0.12, "p_M": 1.0, "total_movement": 0.88, "B_top": 2, "delta_top": 0.36, "gap": 0.08, "share_top1": 0.36 / 0.88, "share_top2": 0.64 / 0.88, "share_top3": 1.0, "blocks_to_half": 2}
    ok = all(abs(s[k] - v) < 1e-9 for k, v in hand.items()) and tres["permutation"][0]["p"] < 0.02
    check(ok, "check 4, the 4-row toy against the hand calculation (P_hat, Δ, B_top, gap, shares, blocks to half; Newcombe in the unit test) and the null-false permutation toy",
          "; ".join(f"{k} {s[k]:.4f} (hand {v:.4f})" for k, v in hand.items()) + f"; gap interval [{s['gap_low']:.3f}, {s['gap_high']:.3f}]; permutation c004 p {tres['permutation'][0]['p']:.4f}, S {tres['permutation'][0]['S_obs']:.3f}")
    for p in tres["figures"]:
        Path(p).unlink()  # toy figures do not stay in figures/
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "scripts/tests"], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    out = proc.stdout + (("\n" + proc.stderr) if proc.stderr.strip() else "")
    (folder / "pytest_output.txt").write_text(out, encoding="utf-8")
    check(proc.returncode == 0, "check 5, pytest on scripts/tests", f"exit code {proc.returncode}; last line: {out.strip().splitlines()[-1] if out.strip() else '(none)'}")
    gate = all(verdicts)
    report = [f"# TEST_REPORT — t9_analyze — {stamp:%Y-%m-%d %H:%M}", "",
              f"Test of pipeline step (9/9) (`scripts/s4_analyze.py`, `scripts/stats_utils.py`), per pipeline v2 Section 9 item 11. Git commit `{R.git_head()}`. "
              f"Archived replay: the 500 archived continuations scored by the registered rule, the pilot's judge labels `{judge.relative_to(REPO).as_posix()}`, the archived cuts treated as cuts (m = rank within the arm); "
              f"bootstrap draws {args.draws}, permutations {args.perms}. Figures of the replay in figures/ (prefix archived_replay_). Offline; API cost $0.", "",
              f"## Result: {'PASS' if gate else 'FAIL'} ({sum(verdicts)}/{len(verdicts)} checks passed)", "", "## Checks", "", *lines, "", *details, "",
              "## pytest output", "", "```", out.rstrip(), "```"]
    (folder / "TEST_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"\nReport: {folder / 'TEST_REPORT.md'}\nGate: {'PASS' if gate else 'FAIL'}")
    return 0 if gate else 1


if __name__ == "__main__":
    sys.exit(main())
