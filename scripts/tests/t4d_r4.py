#!/usr/bin/env python3
"""t4d_r4 -- gate of rule R4 in the derivation (pipeline v2, step 4d/9; decision 20; labeling
scheme v6, Section 6b).  Offline, no API call.

  python scripts/tests/t4d_r4.py [--run runs/experiments/judge_source_sonnet_v2_thinklow_r1_2026-09-17_1017]

Writes runs/tests/t4d_r4_<date>_<hhmm>/TEST_REPORT.md plus structural_before_r4.csv,
structural_after_r4.csv, r4_enforcement.json, pytest_output.txt, config.json.

Checks:
  1. the derivation with the sentence texts reproduces listing v4 on the reviewed labels: 47 blocks
     and 193 nodes for c004, 38 and 147 for e036, with the listing's block intervals, opener rules
     and labels and the node name of every sentence (zero differences); the R4 openers are the ten
     sentences of the scheme
  2. regression: the derivation without texts reproduces the archived listing v3 (46/193, 37/146)
  3. R4 label enforcement applied to the reviewed labels changes nothing
  4. structural metrics of the chosen judge run before R4 (labels as the judge gave them, listing
     v3, no texts) and after R4 (judge labels R4-enforced, listing v4, texts on both sides): block
     F1 and next-node agreement per trace and pooled; the R4 openers agree in every case
  5. pytest on scripts/tests
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import derivation as D  # noqa: E402
import structural_agreement as SA  # noqa: E402

REPO = D.REPO
DEFAULT_RUN = REPO / "runs" / "experiments" / "judge_source_sonnet_v2_thinklow_r1_2026-09-17_1017"
EXPECTED_R4 = {"c004": (375, 47, 193), "e036": (254, 38, 147)}
EXPECTED_V3 = {"c004": (375, 46, 193), "e036": (254, 37, 146)}
R4_SENTENCES = {"c004": [42, 137, 254, 288, 340, 352], "e036": [19, 71, 100, 179]}
ORDER = ["c004", "e036"]


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import argparse
    ap = argparse.ArgumentParser(description="t4d_r4: rule R4 in the derivation")
    ap.add_argument("--run", default=str(DEFAULT_RUN), help="judge run folder with labels_source_judge.jsonl")
    args = ap.parse_args(argv)
    run_dir = Path(args.run)
    stamp = datetime.now()
    folder = REPO / "runs" / "tests" / f"t4d_r4_{stamp:%Y-%m-%d_%H%M}"
    folder.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    details: list[str] = []
    verdicts: list[bool] = []

    def check(ok: bool, name: str, numbers: str):
        verdicts.append(ok)
        lines.append(f"- {'PASS' if ok else 'FAIL'} — {name} — {numbers}")
        print(lines[-1])

    listing = D.parse_listing()
    listing_v3 = D.parse_listing(D.LISTING_V3)
    texts = D.load_sentence_texts()

    # ---- 1. the gate under R4 ------------------------------------------------------------------
    ok = True
    nums = []
    for tid in ORDER:
        n, blocks, nodes = EXPECTED_R4[tid]
        g = D.gate(tid, listing[tid]["labels"], listing[tid], texts[tid])
        this = (g["pass"] and g["sentences"] == n and g["blocks_derived"] == g["blocks_expected"] == blocks
                and g["nodes_derived"] == g["nodes_expected"] == nodes and g["r4_openers"] == R4_SENTENCES[tid])
        ok &= this
        nums.append(f"{tid}: {g['sentences']} sentences; blocks {g['blocks_derived']} derived vs {g['blocks_expected']} listed (expected {blocks}); "
                    f"nodes {g['nodes_derived']} vs {g['nodes_expected']} (expected {nodes}); interval differences {len(g['block_diffs'])}, "
                    f"opener rule/label differences {len(g['rule_diffs'])}, name differences {len(g['name_diffs'])}; "
                    f"R4 openers at s{', s'.join(map(str, g['r4_openers']))}; listing rows with a fragment after the node name: "
                    + (", ".join(f"s{d['s']} ({d['fragment_after_node_name']!r})" for d in listing[tid]["defects"]) or "none"))
        if not g["pass"]:
            details.append(f"### Derivation differences under R4, {tid}\n\n```\n" + json.dumps({k: g[k] for k in ('block_diffs', 'rule_diffs', 'name_diffs')}, ensure_ascii=False, indent=1)[:6000] + "\n```")
    check(ok, "check 1, derivation gate under R4 on the reviewed labels of listing v4 (texts from sentences_source.jsonl)", "; ".join(nums))

    # ---- 2. regression without texts on listing v3 ---------------------------------------------
    ok = True
    nums = []
    for tid in ORDER:
        n, blocks, nodes = EXPECTED_V3[tid]
        g = D.gate(tid, listing_v3[tid]["labels"], listing_v3[tid], None, "reviewed_v3")
        ok &= g["pass"] and g["blocks_derived"] == blocks and g["nodes_derived"] == nodes
        nums.append(f"{tid}: blocks {g['blocks_derived']} (expected {blocks}), nodes {g['nodes_derived']} (expected {nodes}), differences {len(g['block_diffs']) + len(g['rule_diffs']) + len(g['name_diffs'])}")
    check(ok, "check 2, regression: the derivation without texts reproduces the archived listing v3", "; ".join(nums))

    # ---- 3. enforcement on the reviewed labels --------------------------------------------------
    ok = True
    nums = []
    for tid in ORDER:
        new, notes = D.apply_r4_labels(listing[tid]["labels"], texts[tid])
        changed = [s for s, x in enumerate(notes) if x and x["changed"]]
        r4 = [s for s, x in enumerate(notes) if x]
        ok &= new == listing[tid]["labels"] and not changed and r4 == R4_SENTENCES[tid]
        nums.append(f"{tid}: R4 sentences {len(r4)}, labels changed {len(changed)}")
    check(ok, "check 3, R4 label enforcement on the reviewed labels changes nothing", "; ".join(nums))

    # ---- 4. the chosen run before and after R4 --------------------------------------------------
    labels_path = run_dir / "labels_source_judge.jsonl"
    if not labels_path.exists():
        check(False, "check 4, structural metrics of the chosen run", f"{labels_path} not found")
    else:
        judge_raw = SA.judge_labels_from_file(labels_path, raw=True)
        before = SA.compute(judge_raw, {t: listing_v3[t]["labels"] for t in ORDER})
        judge_r4 = {}
        enforcement = {}
        for t in ORDER:
            judge_r4[t], notes = D.apply_r4_labels(judge_raw[t], texts[t])
            enforcement[t] = [{"s": s, "text": texts[t][s][:80], **x, "after": judge_r4[t][s]} for s, x in enumerate(notes) if x]
        after = SA.compute(judge_r4, {t: listing[t]["labels"] for t in ORDER}, texts)
        SA.write_csv(folder / "structural_before_r4.csv", before)
        SA.write_csv(folder / "structural_after_r4.csv", after)
        (folder / "r4_enforcement.json").write_text(json.dumps(enforcement, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        rows = ["| scope | block F1 before → after | block hits / misses / extras before → after | next node after cut before → after | R4 openers reviewed / judge / agree (after) | node F1 before → after |",
                "|---|---|---|---|---|---|"]
        ok = True
        nums = []
        for scope in ORDER + ["pooled"]:
            b0, b1 = before[scope]["blocks"], after[scope]["blocks"]
            n0, n1 = before[scope]["next_node"], after[scope]["next_node"]
            ok &= b1["r4_reviewed"] == b1["r4_judge"] == b1["r4_agree"] == (len(R4_SENTENCES[scope]) if scope != "pooled" else 10)
            rows.append(f"| {scope} | {b0['f1']:.3f} → {b1['f1']:.3f} | {b0['hits']} / {b0['misses']} / {b0['extras']} → {b1['hits']} / {b1['misses']} / {b1['extras']} | "
                        f"{n0['agree']} / {n0['n_cuts']} ({n0['rate']:.3f}) → {n1['agree']} / {n1['n_cuts']} ({n1['rate']:.3f}) | "
                        f"{b1['r4_reviewed']} / {b1['r4_judge']} / {b1['r4_agree']} | {before[scope]['nodes']['f1']:.3f} → {after[scope]['nodes']['f1']:.3f} |")
            nums.append(f"{scope}: block F1 {b0['f1']:.3f} → {b1['f1']:.3f}, next node {n0['rate']:.3f} → {n1['rate']:.3f}, R4 openers agree {b1['r4_agree']} of {b1['r4_reviewed']}")
        n_changed = sum(1 for t in ORDER for x in enforcement[t] if x["changed"])
        check(ok, f"check 4, structural metrics of `{run_dir.relative_to(REPO).as_posix()}` before R4 (judge labels as given vs listing v3) and after R4 (enforced vs listing v4, texts on both sides)",
              "; ".join(nums) + f"; judge labels changed by enforcement: {n_changed} of 10 R4 sentences")
        details.append("## Check 4: before and after R4\n\n" + "\n".join(rows))
        details.append(SA.markdown(before, "Before R4 (judge labels as given; reviewed = listing v3; no texts)"))
        details.append(SA.markdown(after, "After R4 (judge labels R4-enforced; reviewed = listing v4; texts on both sides)"))
        enf_rows = ["## R4 enforcement on the judge labels of the chosen run", "", "| trace | s | action | changed | judge label before | after | text |", "|---|---|---|---|---|---|---|"]
        for t in ORDER:
            for x in enforcement[t]:
                enf_rows.append(f"| {t} | {x['s']} | {x['action']} | {x['changed']} | {' \\|\\| '.join(x['before'])} | {' \\|\\| '.join(x['after'])} | {x['text'].replace('|', '\\|')} |")
        details.append("\n".join(enf_rows))

    # ---- 5. pytest -----------------------------------------------------------------------------
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "scripts/tests"], cwd=REPO, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", env=env)
    out = proc.stdout + (("\n" + proc.stderr) if proc.stderr.strip() else "")
    (folder / "pytest_output.txt").write_text(out, encoding="utf-8")
    check(proc.returncode == 0, "check 5, pytest on scripts/tests", f"exit code {proc.returncode}; last line: {out.strip().splitlines()[-1] if out.strip() else '(none)'}")
    details.append("## pytest output\n\n```\n" + out.rstrip() + "\n```")

    config = {"git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip() or None,
              "listing": D.LISTING.relative_to(REPO).as_posix(), "listing_v3": D.LISTING_V3.relative_to(REPO).as_posix(),
              "sentences": D.SENTENCES_SOURCE.relative_to(REPO).as_posix(), "run": str(run_dir), "r4_regex": D.R4_RE.pattern,
              "python": sys.version.split()[0], "timestamp": stamp.isoformat(timespec="seconds")}
    (folder / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    gate = all(verdicts)
    report = [f"# TEST_REPORT — t4d_r4 — {stamp:%Y-%m-%d %H:%M}", "",
              f"Gate of rule R4 in the derivation (`scripts/derivation.py`, `scripts/structural_agreement.py`), pipeline v2 step (4d/9) and decision 20; labeling scheme v6 Section 6b. "
              f"Git commit `{config['git_commit']}`. Listing `{config['listing']}`; pre-R4 listing `{config['listing_v3']}` (archive, read only); texts `{config['sentences']}`. "
              f"R4 regex `{D.R4_RE.pattern}` (case-insensitive). Offline; API cost $0.", "",
              f"## Result: {'PASS' if gate else 'FAIL'} ({sum(verdicts)}/{len(verdicts)} checks passed)", "", "## Checks", "", *lines, "", *details]
    (folder / "TEST_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"\nReport: {folder / 'TEST_REPORT.md'}\nGate: {'PASS' if gate else 'FAIL'}")
    return 0 if gate else 1


if __name__ == "__main__":
    sys.exit(main())
