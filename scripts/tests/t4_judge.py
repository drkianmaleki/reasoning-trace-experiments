#!/usr/bin/env python3
"""t4_judge -- test of pipeline step (4/9), the judge on the two source traces (pipeline v2,
Section 9 item 6).  Ordinary calls to the chosen judge model (cents to a few dollars).

  python scripts/tests/t4_judge.py [--model haiku|sonnet] [--prompt-version v1|v2|v3]
                                   [--thinking off|none|low|medium] [--repeat K]

Writes runs/tests/t4_judge_<model>_<version>[_think<mode>][_x<K>]_<stamp>/TEST_REPORT.md and runs
the judge into K run folders runs/experiments/judge_source_<model>_<version>[_think<mode>][_r<k>]_<stamp>/.
Order:
  1. derivation gate on the reviewed labels of listing v4 under rule R4 (offline; 47/193 and
     38/147; FAIL stops everything before any call)
  2. dry run: both requests built, token estimates, every index once in the user message
  3.. per run k and trace (e036 then c004): the call, attempts, validity, stop reason, tokens,
     thinking tokens, <think> leaks, cost, node/block counts vs 147/38 and 193/47 (judge labels
     R4-enforced), agreement (enforced and as given)
  then: agreement artifacts per run copied here; structural metrics after R4 (enforced judge
  labels vs listing v4, texts on both sides: the R4 openers must agree in every case) and before
  R4 (labels as given vs the archived listing v3, no texts; comparable with the v2 runs); with
  K >= 2 the test-retest agreement between run 1 (reference) and run 2; pytest.
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
import structural_agreement as SA  # noqa: E402

REPO = S.REPO
SENTENCES = REPO / "runs" / "tests" / "t2_split_2026-09-16_2224" / "sentences_source.jsonl"
EXPECTED = {"e036": {"nodes": 147, "blocks": 38}, "c004": {"nodes": 193, "blocks": 47}}  # listing v4 under R4
EXPECTED_V3 = {"e036": {"nodes": 146, "blocks": 37}, "c004": {"nodes": 193, "blocks": 46}}  # archived listing v3, no R4
ORDER = ["e036", "c004"]
LEVEL_SHORT = {1: "Level 1", 2: "Level 2", 3: "Level 3"}


def load_judge_labels(labels_path: Path, raw: bool = False) -> dict[str, list[list[str]]]:
    return SA.judge_labels_from_file(labels_path, raw=raw)


def agreement_markdown(agr: dict, title: str, residue_rows: int = 30) -> str:
    out = [f"## {title}", "", "| level | n | exact-match rate | mean Jaccard | kappa (primary label) | primary agreement |", "|---|---|---|---|---|---|"]
    for lv in agr["levels"]:
        out.append(f"| {lv['name']} | {lv['n']} | {lv['exact_match']:.4f} | {lv['mean_jaccard']:.4f} | {lv['kappa']:.4f} | {lv['primary_agreement']:.4f} |")
    out += ["", "| level | label | n_reviewed | n_judge | tp | precision | recall | F1 |", "|---|---|---|---|---|---|---|---|"]
    for r in agr["per_label"]:
        out.append(f"| {r['level']} | {r['label']} | {r['n_reviewed']} | {r['n_judge']} | {r['tp']} | {r['precision']:.3f} | {r['recall']:.3f} | {r['f1']:.3f} |")
    for level in (1, 2):
        out += ["", f"### Twenty most frequent confusion pairs at Level {level} (reference → other, primary label)", "", "| reference | other | count |", "|---|---|---|"]
        for (a, b), c in agr["confusions"][level]:
            out.append(f"| {a} | {b} | {c} |")
    out += ["", f"### Residue: {len(agr['residue'])} sentences whose full-path set differs (first {residue_rows})", "",
            "| trace | s | reference | other | text |", "|---|---|---|---|---|"]
    for r in agr["residue"][:residue_rows]:
        out.append(f"| {r['trace_id']} | {r['s']} | {r['reviewed']} | {r['judge']} | {r['text'].replace('|', '\\|')} |")
    return "\n".join(out)


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import argparse
    ap = argparse.ArgumentParser(description="t4: the judge on the two source traces")
    ap.add_argument("--model", choices=tuple(S.MODELS), default="haiku")
    ap.add_argument("--prompt-version", choices=S.PROMPT_VERSIONS, default="v1")
    ap.add_argument("--thinking", choices=S.THINKING_MODES, default="off")
    ap.add_argument("--repeat", type=int, default=1, help="run the judge K times per trace (test-retest between runs 1 and 2)")
    args = ap.parse_args(argv)
    model_key, version, thinking, K = args.model, args.prompt_version, args.thinking, args.repeat
    if K < 1:
        raise SystemExit("--repeat must be at least 1")
    stamp = datetime.now()
    tag = (f"_think{thinking}" if thinking != "off" else "") + (f"_x{K}" if K > 1 else "")
    folder = REPO / "runs" / "tests" / f"t4_judge_{model_key}_{version}{tag}_{stamp:%Y-%m-%d_%H%M}"
    folder.mkdir(parents=True, exist_ok=True)
    run_dirs = [REPO / "runs" / "experiments" / S.make_run_id(model_key, version, stamp, thinking, k if K > 1 else None)
                for k in range(1, K + 1)]
    prompt_file, labels_file = S.prompt_files(version)
    m = S.MODELS[model_key]
    tparams = S.thinking_params(model_key, thinking)
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
            f"Test of pipeline step (4/9), the judge on the two source traces (`scripts/s1_judge.py`, `scripts/derivation.py`), per pipeline v2 Section 9 item 6, with rule R4 in the derivation (decision 20). "
            f"Git commit `{S.git_head()}`; model `{m['id']}` ({model_key}); thinking mode {thinking}"
            + (f" (request parameters {json.dumps(tparams)}, max_tokens {S.MAX_TOKENS_THINKING})" if tparams else f" (thinking {m['thinking'] or 'omitted'}, max_tokens {S.MAX_TOKENS})")
            + f"; temperature {m['temperature']} ({'via extra_body' if m['temperature'] is not None else 'not sent: the model rejects sampling parameters'}); "
            f"prompt {version} sha256 `{S.sha256_of_file(prompt_file)}`; inventory sha256 `{S.sha256_of_file(labels_file)}`; sentences `{SENTENCES.relative_to(REPO).as_posix()}`; "
            f"reviewed listing `{D.LISTING.relative_to(REPO).as_posix()}` (pre-R4 comparison: `{D.LISTING_V3.relative_to(REPO).as_posix()}`). "
            f"Repeats: {K}. Run folders: " + ", ".join(f"`{d.relative_to(REPO).as_posix()}`" for d in run_dirs) + ".",
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

    # ---- 1. derivation gate on the reviewed labels (R4) --------------------------------------------
    listing = D.parse_listing()
    listing_v3 = D.parse_listing(D.LISTING_V3)
    texts = D.load_sentence_texts(SENTENCES)
    gate_ok = True
    nums = []
    for tid in ORDER:
        g = D.gate(tid, listing[tid]["labels"], listing[tid], texts[tid])
        gate_ok &= g["pass"] and g["blocks_derived"] == EXPECTED[tid]["blocks"] and g["nodes_derived"] == EXPECTED[tid]["nodes"]
        nums.append(f"{tid}: {g['sentences']} sentences; blocks {g['blocks_derived']} derived vs {g['blocks_expected']} listed; "
                    f"nodes {g['nodes_derived']} vs {g['nodes_expected']}; interval differences {len(g['block_diffs'])}, "
                    f"opener rule/label differences {len(g['rule_diffs'])}, name differences {len(g['name_diffs'])}; R4 openers at s{', s'.join(map(str, g['r4_openers']))} "
                    f"(listing names with a '(1)' count stripped: {g['names_normalized']})")
        if not g["pass"]:
            details.append(f"### Derivation differences, {tid}\n\n```\n" + json.dumps({k: g[k] for k in ('block_diffs', 'rule_diffs', 'name_diffs')}, ensure_ascii=False, indent=1)[:6000] + "\n```")
    check(gate_ok, "check 1, derivation gate under R4 on the reviewed labels of listing v4 (offline)", "; ".join(nums))
    if not gate_ok:
        write_report(final=False)
        print("Derivation gate FAILED: no API call made.")
        return 1

    # ---- 2. dry run -----------------------------------------------------------------------------
    dry = S.run_judge(SENTENCES, folder / "dry_run", ORDER, dry_run=True, log=lambda s: None,
                      model_key=model_key, prompt_version=version, thinking_mode=thinking)
    nums = []
    ok = True
    for tid in ORDER:
        req = json.loads((folder / "dry_run" / "requests" / f"{tid}.json").read_text(encoding="utf-8"))
        content = req["messages"][0]["content"]
        idx = [int(mm.group(1)) for l in content.split("\n") for mm in [re.match(r"^s(\d+): ", l)] if mm]
        n = dry["traces"][tid]["n"]
        once = idx == list(range(n))
        ok &= once and req["system"][0]["cache_control"] == {"type": "ephemeral"} and req["model"] == m["id"]
        ok &= (req.get("extra_body") == {"temperature": m["temperature"]}) if m["temperature"] is not None else ("extra_body" not in req)
        if tparams:
            ok &= req.get("thinking") == tparams["thinking"] and req.get("output_config") == tparams["output_config"] and req["max_tokens"] == S.MAX_TOKENS_THINKING
        else:
            ok &= (req.get("thinking") == m["thinking"]) if m["thinking"] is not None else ("thinking" not in req)
        nums.append(f"{tid}: {n} sentences, about {dry['traces'][tid]['estimated_input_tokens']} input tokens (characters/4); "
                    f"every index exactly once in the user message: {once}")
    check(ok, "check 2, dry run (requests built, nothing called)", "; ".join(nums) + f"; thinking parameters in the request: {json.dumps(tparams) if tparams else 'none'}; requests written to dry_run/requests/")

    # ---- 3.. the calls, K runs, e036 first --------------------------------------------------------------
    try:
        client = S.make_client()
    except Exception as e:
        check(False, "check 3, Claude client", f"cannot create the client: {e}")
        write_report(final=False)
        return 1
    summaries = []
    total_cost = 0.0
    k_check = 3
    for k, run_dir in enumerate(run_dirs, start=1):
        summary = S.run_judge(SENTENCES, run_dir, ORDER, dry_run=False, client=client, reviewed_path=D.LISTING,
                              model_key=model_key, prompt_version=version, thinking_mode=thinking)
        summaries.append(summary)
        total_cost += summary["total_cost_usd"]
        for tid in ORDER:
            t = summary["traces"].get(tid, {})
            if "valid" not in t:
                check(False, f"check {k_check}, run {k}, {tid}", "not run (the run stopped earlier)")
                k_check += 1
                continue
            u = t.get("usage", {})
            exp = EXPECTED[tid]
            agr_txt = ""
            if summary.get("agreement") and t.get("valid"):
                jl = load_judge_labels(Path(summary["labels_path"]))
                jl_raw = load_judge_labels(Path(summary["labels_path"]), raw=True)
                sub = S.agreement({tid: jl[tid]}, {tid: listing[tid]["labels"]}, {tid: listing[tid]["texts"]})
                sub_raw = S.agreement({tid: jl_raw[tid]}, {tid: listing[tid]["labels"]}, {tid: listing[tid]["texts"]})
                agr_txt = "; agreement vs reviewed v4 (this trace; judge labels R4-enforced): " + ", ".join(
                    f"{LEVEL_SHORT[lv['level']]} exact {lv['exact_match']:.3f} kappa {lv['kappa']:.3f}" for lv in sub["levels"]) + \
                    f"; residue rows {len(sub['residue'])}; as given (before enforcement): Level 1 kappa {sub_raw['levels'][0]['kappa']:.3f}, full-path exact {sub_raw['levels'][2]['exact_match']:.3f}"
            check(bool(t.get("valid")), f"check {k_check}, run {k}, {tid} judged",
                  f"attempts {t.get('attempts')}, valid {t.get('valid')}, model echoed {t.get('model')!r}, stop reasons {t.get('stop_reasons')}, final {t.get('final_stop_reason')}; "
                  f"tokens input {u.get('input_tokens')}, cache read {u.get('cache_read_input_tokens')}, cache write {u.get('cache_creation_input_tokens')}, "
                  f"thinking {u.get('thinking_tokens')}, output {u.get('output_tokens')} (thinking included); <think> tag in text blocks per attempt {t.get('leaks')}; "
                  f"thinking text chars per attempt {t.get('thinking_chars')}; cost ${t.get('cost_usd', 0):.6f}; judge nodes {t.get('nodes')} / blocks {t.get('blocks')} "
                  f"vs reviewed {exp['nodes']} / {exp['blocks']} (R4 on both sides); judge labels changed by R4 enforcement {t.get('r4_changed')}"
                  + (f"; retry message: {t.get('retry_message')}" if t.get('retry_message') else "")
                  + (f"; error: {t.get('error')}" if t.get('error') else "") + agr_txt)
            k_check += 1
        if summary["stopped"]:
            check(False, f"run {k}", f"stopped: {summary['stopped']}")
        # artifacts of this run
        sub = folder / f"run{k}"
        sub.mkdir(exist_ok=True)
        for name in ("labels_source_judge.jsonl", "blocks_source_judge.jsonl", "traces_source_judge.jsonl", "config.json", "_log.txt",
                     "agreement_source.csv", "residue_source.csv", "confusions_source.csv", "summary.md"):
            if (run_dir / name).exists():
                shutil.copy(run_dir / name, sub / name)
        agr = summary.get("agreement")
        if agr:
            lv = {x["level"]: x for x in agr["levels"]}
            jl_raw = load_judge_labels(Path(summary["labels_path"]), raw=True)
            agr_raw = S.agreement(jl_raw, {t: listing[t]["labels"] for t in jl_raw}, {t: listing[t]["texts"] for t in jl_raw})
            lvr = {x["level"]: x for x in agr_raw["levels"]}
            check(True, f"check {k_check}, run {k}, agreement vs reviewed v4 over both traces (judge labels R4-enforced)",
                  f"{agr['n']} sentences; " + "; ".join(f"{LEVEL_SHORT[l]}: exact {lv[l]['exact_match']:.3f}, Jaccard {lv[l]['mean_jaccard']:.3f}, kappa {lv[l]['kappa']:.3f}" for l in (1, 2, 3))
                  + f"; residue rows {len(agr['residue'])}; as given (before enforcement): " + "; ".join(f"{LEVEL_SHORT[l]} kappa {lvr[l]['kappa']:.3f}" for l in (1, 2, 3))
                  + f"; cost of this run ${summary['total_cost_usd']:.6f}")
            k_check += 1
            details.append(agreement_markdown(agr, f"Run {k}: agreement judge (R4-enforced) vs reviewed v4 (both traces)"))
            # structural metrics (Kian, 2026-09-17): after R4 (texts on both sides) and before R4 (comparable with the v2 runs)
            judge = load_judge_labels(Path(summary["labels_path"]))
            after = SA.compute(judge, {t: listing[t]["labels"] for t in judge}, texts)
            before = SA.compute(jl_raw, {t: listing_v3[t]["labels"] for t in jl_raw})
            SA.write_csv(run_dir / "structural_source.csv", after)
            SA.write_csv(run_dir / "structural_source_before_r4.csv", before)
            shutil.copy(run_dir / "structural_source.csv", sub / "structural_source.csv")
            shutil.copy(run_dir / "structural_source_before_r4.csv", sub / "structural_source_before_r4.csv")
            ps, pb = after["pooled"], before["pooled"]
            r4_ok = all(after[t]["blocks"]["r4_reviewed"] == after[t]["blocks"]["r4_judge"] == after[t]["blocks"]["r4_agree"] for t in ORDER)
            check(r4_ok, f"check {k_check}, run {k}, structural metrics vs reviewed (pooled), after R4 → before R4 in brackets",
                  f"block openers hits {ps['blocks']['hits']} [{pb['blocks']['hits']}] / misses {ps['blocks']['misses']} [{pb['blocks']['misses']}] (near {ps['blocks']['near_misses']}) / extras {ps['blocks']['extras']} [{pb['blocks']['extras']}], "
                  f"F1 {ps['blocks']['f1']:.3f} [{pb['blocks']['f1']:.3f}], rule agrees on {ps['blocks']['rule_agree']} of {ps['blocks']['hits']} hits; "
                  f"R4 openers reviewed / judge / agree {ps['blocks']['r4_reviewed']} / {ps['blocks']['r4_judge']} / {ps['blocks']['r4_agree']} (must coincide); "
                  f"next node after the reviewed cuts {ps['next_node']['agree']} / {ps['next_node']['n_cuts']} ({ps['next_node']['rate']:.3f}) [{pb['next_node']['agree']} / {pb['next_node']['n_cuts']} ({pb['next_node']['rate']:.3f})]; "
                  f"node ends F1 {ps['nodes']['f1']:.3f} [{pb['nodes']['f1']:.3f}], matched nodes Level 1 agree {ps['nodes']['matched_l1_rate']:.3f}, reviewed nodes split {ps['nodes']['split']} / merged {ps['nodes']['merged']}; "
                  f"sentences L1 wrong {ps['sentences']['l1_wrong']} / L2 wrong {ps['sentences']['l2_wrong']} / L3 wrong {ps['sentences']['l3_wrong']} / all right {ps['sentences']['all_right']} "
                  f"(L1 share of disagreements {ps['sentences']['l1_share_of_disagreements']:.3f}); structural_source.csv and structural_source_before_r4.csv written")
            k_check += 1
            details.append(SA.markdown(after, f"Run {k}: structural metrics judge vs reviewed, after R4 (enforced judge labels vs listing v4, texts on both sides)"))
            details.append(SA.markdown(before, f"Run {k}: structural metrics judge vs reviewed, before R4 (labels as given vs listing v3, no texts; comparable with the v2 runs)"))
        else:
            check(False, f"check {k_check}, run {k}, agreement", "no agreement computed (the run stopped)")
            k_check += 1

    # ---- test-retest between run 1 (reference) and run 2 -------------------------------------------
    if K >= 2 and all(s.get("labels_path") and not s["stopped"] for s in summaries[:2]):
        j1 = load_judge_labels(Path(summaries[0]["labels_path"]))
        j2 = load_judge_labels(Path(summaries[1]["labels_path"]))
        ltexts = {t: listing[t]["texts"] for t in ORDER}
        rows = ["## Test-retest: run 2 against run 1 (run 1 as reference; same functions as reviewed-vs-judge)", "",
                "| scope | L1 exact | L1 kappa | L2 exact | L2 kappa | full exact | full kappa | run 1 blocks / nodes | run 2 blocks / nodes | reviewed |", "|---|---|---|---|---|---|---|---|---|---|"]
        tr_nums = []
        for scope in ORDER + ["pooled"]:
            traces = ORDER if scope == "pooled" else [scope]
            agr = S.agreement({t: j2[t] for t in traces}, {t: j1[t] for t in traces}, {t: ltexts[t] for t in traces})
            lv = {x["level"]: x for x in agr["levels"]}
            b1 = sum(summaries[0]["traces"][t]["blocks"] for t in traces)
            n1 = sum(summaries[0]["traces"][t]["nodes"] for t in traces)
            b2 = sum(summaries[1]["traces"][t]["blocks"] for t in traces)
            n2 = sum(summaries[1]["traces"][t]["nodes"] for t in traces)
            rb = sum(EXPECTED[t]["blocks"] for t in traces)
            rn = sum(EXPECTED[t]["nodes"] for t in traces)
            rows.append(f"| {scope} | {lv[1]['exact_match']:.3f} | {lv[1]['kappa']:.3f} | {lv[2]['exact_match']:.3f} | {lv[2]['kappa']:.3f} | {lv[3]['exact_match']:.3f} | {lv[3]['kappa']:.3f} | {b1} / {n1} | {b2} / {n2} | {rb} / {rn} |")
            tr_nums.append(f"{scope}: L1 exact {lv[1]['exact_match']:.3f} kappa {lv[1]['kappa']:.3f}, L2 exact {lv[2]['exact_match']:.3f} kappa {lv[2]['kappa']:.3f}, full exact {lv[3]['exact_match']:.3f} kappa {lv[3]['kappa']:.3f}; differing sentences {len(agr['residue'])}")
            if scope == "pooled":
                rows += ["", "### Ten most frequent Level 2 disagreements between the runs (run 1 → run 2)", "", "| run 1 | run 2 | count |", "|---|---|---|"]
                for (a, b), c in agr["confusions"][2][:10]:
                    rows.append(f"| {a} | {b} | {c} |")
        check(True, f"check {k_check}, test-retest run 2 vs run 1", "; ".join(tr_nums))
        k_check += 1
        details.append("\n".join(rows))

    # ---- pytest ----------------------------------------------------------------------------------
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "scripts/tests"], cwd=REPO, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", env=env)
    out = proc.stdout + (("\n" + proc.stderr) if proc.stderr.strip() else "")
    (folder / "pytest_output.txt").write_text(out, encoding="utf-8")
    check(proc.returncode == 0, f"check {k_check}, pytest on scripts/tests", f"exit code {proc.returncode}; last line: {out.strip().splitlines()[-1] if out.strip() else '(none)'}")
    details.append("## pytest output\n\n```\n" + out.rstrip() + "\n```")
    (folder / "summary.json").write_text(json.dumps([{k: v for k, v in s.items() if k not in ("agreement", "pcorpus")} for s in summaries], indent=2, default=str) + "\n", encoding="utf-8")
    write_report(final=True)
    print(f"\nReport: {folder / 'TEST_REPORT.md'}\nGate: {'PASS' if all(verdicts) else 'FAIL'}\nTotal API cost: ${total_cost:.6f}")
    return 0 if all(verdicts) else 1


if __name__ == "__main__":
    sys.exit(main())
