#!/usr/bin/env python3
"""t5_batch -- test of pipeline step (5/9), batch mode of the judge (pipeline v2, Section 9
item 7).  A batch of three archived continuations from three different cuts -- one shared cut-0,
one c004, one e036 (the shortest of each group) -- through the full path: submit, poll, download,
parse, derive with R4, first new node and block sequence.  Cents.

  python scripts/tests/t5_batch.py [--sentences runs/experiments/s0_split_2026-09-17_1046/sentences_archived500.jsonl]
                                   [--model sonnet] [--prompt-version v3] [--thinking low] [--poll-seconds 30]

Writes runs/tests/t5_batch_<date>_<hhmm>/TEST_REPORT.md with the batch id, timing, request_counts,
cost and the three block sequences; the run itself goes into runs/tests/t5_batch_<stamp>/run/
(sentences_archived3.jsonl, labels_, blocks_, traces_archived3_judge.jsonl, replies/, requests/,
custom_ids.json, batch_state.json, config.json, _log.txt, summary.md, pnext_archived3.csv,
psource_c004.csv, psource_e036.csv, labels_source_reviewed_v4.jsonl).
Checks:
  1. the three continuations chosen (one per arm, three different cuts) and written out
  2. dry run: the continuation requests (prefix part with tab codes for c004/e036, none for cut-0;
     prefix length = source sentences with old_s <= cut; c-indices 0..N-1 once)
  3. the batch: submitted (id), ended, request_counts, results downloaded and parsed (three valid,
     follow-up batch if needed), thinking blocks stored, custom_ids.json and batch_state.json
  4. records: labels per sentence with batch_id, custom_id, attempt, stop_reason, thinking_tokens,
     cost; usage on the first record; cost equals the usage at batch prices
  5. derivation with R4: three blocks records, first new node and block sequence per continuation;
     pnext_archived3.csv and the two psource files
  6. pytest on scripts/tests
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import derivation as D  # noqa: E402
import s1_judge as S  # noqa: E402

REPO = S.REPO
DEFAULT_SENTENCES = REPO / "runs" / "experiments" / "s0_split_2026-09-17_1046" / "sentences_archived500.jsonl"
REGENERATE = "python scripts/s0_split.py --collection archived500 --out runs/experiments/s0_split_2026-09-17_1046/"


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import argparse
    ap = argparse.ArgumentParser(description="t5: batch mode on three archived continuations")
    ap.add_argument("--sentences", default=str(DEFAULT_SENTENCES))
    ap.add_argument("--model", choices=tuple(S.MODELS), default="sonnet")
    ap.add_argument("--prompt-version", choices=S.PROMPT_VERSIONS, default="v3")
    ap.add_argument("--thinking", choices=S.THINKING_MODES, default="low")
    ap.add_argument("--poll-seconds", type=int, default=30)
    args = ap.parse_args(argv)
    stamp = datetime.now()
    folder = REPO / "runs" / "tests" / f"t5_batch_{stamp:%Y-%m-%d_%H%M}"
    folder.mkdir(parents=True, exist_ok=True)
    run_dir = folder / "run"
    lines: list[str] = []
    details: list[str] = []
    verdicts: list[bool] = []

    def check(ok: bool, name: str, numbers: str):
        verdicts.append(ok)
        lines.append(f"- {'PASS' if ok else 'FAIL'} — {name} — {numbers}")
        print(lines[-1])

    def write_report(final: bool, extra_head: str = ""):
        gate = all(verdicts)
        text = [f"# TEST_REPORT — t5_batch — {stamp:%Y-%m-%d %H:%M}", "",
                f"Test of pipeline step (5/9), batch mode of the judge (`scripts/s1_judge.py --mode batch`, Message Batches API), per pipeline v2 Section 9 item 7. "
                f"Git commit `{S.git_head()}`; model `{S.MODELS[args.model]['id']}` ({args.model}); prompt {args.prompt_version}; thinking {args.thinking}; "
                f"batch prices (Sonnet 5: $1 / $5 per million input / output, cache read $0.10, cache write $1.25); polling every {args.poll_seconds} s (the pilot polls every {S.BATCH_POLL_SECONDS} s). "
                f"Sentences `{Path(args.sentences).as_posix()}`. Run folder `{run_dir.relative_to(REPO).as_posix()}`." + extra_head, "",
                f"## Result: {'PASS' if gate else 'FAIL'} ({sum(verdicts)}/{len(verdicts)} checks passed){'' if final else ' — STOPPED EARLY'}", "",
                "## Checks", "", *lines, "", *details]
        (folder / "TEST_REPORT.md").write_text("\n".join(text) + "\n", encoding="utf-8")

    # ---- 1. choose three continuations ----------------------------------------------------------
    sentences_path = Path(args.sentences)
    if not sentences_path.exists():
        check(False, "check 1, sentences file", f"{sentences_path} is absent (git-ignored); regenerate with `{REGENERATE}`")
        write_report(final=False)
        return 1
    meta = S.load_archived_meta()
    counts = Counter()
    with open(sentences_path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                counts[json.loads(line)["trace_id"]] += 1
    chosen = {}
    for arm in ("shared", "c004", "e036"):
        cands = [t for t in counts if t in meta and meta[t]["trace_arm"] == arm]
        chosen[arm] = min(cands, key=lambda t: (counts[t], t))
    ids = [chosen[a] for a in ("shared", "c004", "e036")]
    cuts = [(meta[t]["trace_arm"], meta[t]["cut"]) for t in ids]
    sub_path = folder / "sentences_archived3.jsonl"
    with open(sentences_path, encoding="utf-8") as fh, open(sub_path, "w", encoding="utf-8", newline="\n") as out:
        for line in fh:
            if line.strip() and json.loads(line)["trace_id"] in ids:
                out.write(line if line.endswith("\n") else line + "\n")
    ok = len(set(cuts)) == 3 and {a for a, _ in cuts} == {"shared", "c004", "e036"}
    check(ok, "check 1, three archived continuations from three different cuts (the shortest of each arm)",
          "; ".join(f"{t}: arm {meta[t]['trace_arm']}, cut {meta[t]['cut']}, {counts[t]} sentences" for t in ids) + f"; written to {sub_path.name}")

    # ---- 2. dry run -----------------------------------------------------------------------------
    dry = S.run_judge(sub_path, folder / "dry_run", dry_run=True, log=lambda s: None, model_key=args.model, prompt_version=args.prompt_version,
                      thinking_mode=args.thinking, mode="batch", collection="archived3")
    src = S.load_sentences(S.SENTENCES_SOURCE)
    ok = True
    nums = []
    for t in ids:
        req = json.loads((folder / "dry_run" / "requests" / f"{dry['traces'][t]['custom_id']}.json").read_text(encoding="utf-8"))
        msg = req["messages"][0]["content"]
        mlines = msg.split("\n")
        arm, cut = meta[t]["trace_arm"], meta[t]["cut"]
        expected_prefix = 0 if arm == "shared" else sum(1 for r in src[arm] if r["old_s"] <= cut)
        has_prefix = "Prefix, already labeled (do not relabel):" in mlines
        p_lines = [l for l in mlines if re.match(r"^s\d+: .*\t\S+$", l)]
        c_idx = [int(mm.group(1)) for l in mlines for mm in [re.match(r"^c(\d+): ", l)] if mm]
        this = (has_prefix == (arm != "shared") and len(p_lines) == expected_prefix and c_idx == list(range(counts[t]))
                and "Continuation to label:" in mlines and req["max_tokens"] == S.max_tokens_for(counts[t], args.model, args.thinking))
        ok &= this
        nums.append(f"{t}: prefix part {'present' if has_prefix else 'absent'} with {len(p_lines)} labeled sentences (expected {expected_prefix}: old_s <= {cut} of {arm}); "
                    f"c-indices 0..{counts[t] - 1} once: {c_idx == list(range(counts[t]))}; max_tokens {req['max_tokens']}; about {dry['traces'][t]['estimated_input_tokens']} input tokens")
    check(ok, "check 2, dry run: continuation requests", "; ".join(nums))

    # ---- 3. the batch ---------------------------------------------------------------------------
    try:
        client = S.make_client()
    except Exception as e:
        check(False, "check 3, Claude client", f"cannot create the client: {e}")
        write_report(final=False)
        return 1
    t0 = datetime.now()
    summary = S.run_judge(sub_path, run_dir, client=client, model_key=args.model, prompt_version=args.prompt_version, thinking_mode=args.thinking,
                          mode="batch", collection="archived3", poll_seconds=args.poll_seconds, log=print)
    t1 = datetime.now()
    batches = summary.get("batches", [])
    state = json.loads((run_dir / "batch_state.json").read_text(encoding="utf-8")) if (run_dir / "batch_state.json").exists() else {}
    cid_map = json.loads((run_dir / "custom_ids.json").read_text(encoding="utf-8")) if (run_dir / "custom_ids.json").exists() else {}
    ok = (summary["stopped"] is None and summary["n_valid"] == 3 and bool(batches) and state.get("status") == "ended"
          and set(cid_map.values()) == set(ids) and all(b["request_counts"] and b["request_counts"]["processing"] == 0 for b in batches))
    thinking_files = sorted(p.name for p in (run_dir / "replies").glob("*_thinking.txt")) if (run_dir / "replies").exists() else []
    check(ok, "check 3, batch submitted, polled, downloaded and parsed",
          "; ".join(f"batch {b['batch_id']} (attempt {b['attempt']}, {b['n_entries']} entries): submitted {b['submitted']}, ended {b['ended']}, request_counts {json.dumps(b['request_counts'])}" for b in batches)
          + f"; wall time {(t1 - t0).total_seconds():.0f} s; valid {summary['n_valid']} of 3; failures {json.dumps(summary.get('failures'))}; "
          f"thinking files {len(thinking_files)}; custom_ids.json {sorted(cid_map.values()) == sorted(ids)}; batch_state.json status {state.get('status')}"
          + (f"; stopped: {summary['stopped']}" if summary["stopped"] else ""))
    if summary["stopped"] or summary["n_valid"] == 0:
        write_report(final=False)
        return 1

    # ---- 4. records -----------------------------------------------------------------------------
    labels = [json.loads(l) for l in (run_dir / "labels_archived3_judge.jsonl").read_text(encoding="utf-8").splitlines()]
    traces = {json.loads(l)["trace_id"]: json.loads(l) for l in (run_dir / "traces_archived3_judge.jsonl").read_text(encoding="utf-8").splitlines()}
    ok = True
    nums = []
    for t in ids:
        recs = [r for r in labels if r["trace_id"] == t]
        tr = traces[t]
        fields_ok = all(all(k in r for k in ("batch_id", "custom_id", "attempt", "stop_reason", "thinking_tokens", "cost_usd", "valid", "r4_applied")) for r in recs)
        first = recs[0] if recs else {}
        cost_ok = bool(recs) and abs(first["cost_usd"] - S.cost_usd(first["usage"], args.model, batch=True)) < 1e-9
        this = len(recs) == counts[t] and fields_ok and cost_ok and first.get("usage") is not None and tr["valid"]
        ok &= this
        nums.append(f"{t}: {len(recs)} label records (expected {counts[t]}), fields present {fields_ok}, batch_id {first.get('batch_id')}, custom_id {first.get('custom_id')}, "
                    f"attempt {first.get('attempt')}, stop_reason {first.get('stop_reason')}, thinking tokens {first.get('thinking_tokens')}, usage {json.dumps(first.get('usage'))}, "
                    f"cost ${first.get('cost_usd', 0):.6f} (= usage at batch prices: {cost_ok}); R4 sentences {sum(1 for r in recs if r['r4_applied'])}, labels changed by enforcement {tr.get('r4_changed')}")
    check(ok, "check 4, records", "; ".join(nums))

    # ---- 5. derivation, first new node, block sequences -----------------------------------------
    blocks = {json.loads(l)["trace_id"]: json.loads(l) for l in (run_dir / "blocks_archived3_judge.jsonl").read_text(encoding="utf-8").splitlines()}
    ok = len(blocks) == 3 and all(b["r4"] and "first_new_node" in b for b in blocks.values())
    rows = ["## Check 5: the three continuations", "", "| continuation | arm | cut | prefix sentences | continuation sentences | first new node | L1 | opens block (rule) | first sentence is Wait | block sequence from the cut |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for t in ids:
        b = blocks[t]
        fn = b["first_new_node"]
        rows.append(f"| {t} | {b['trace_arm']} | {b['cut']} | {b['prefix_n']} | {b['n_cont']} | {fn['name']} | {fn['L1']} | {fn['opens_block']} ({fn['opener_rule']}) | {b['first_sentence_r4']} | {S.block_sequence_text(b).replace('|', '\\|')} |")
    pn = run_dir / "pnext_archived3.csv"
    pn_lines = pn.read_text(encoding="utf-8").splitlines() if pn.exists() else []
    ok &= len(pn_lines) == 4 and (run_dir / "psource_c004.csv").exists() and (run_dir / "psource_e036.csv").exists()
    check(ok, "check 5, derivation with R4: blocks records, first new node, block sequences, pnext and psource files",
          "; ".join(f"{t}: first new node {blocks[t]['first_new_node']['name']} ({blocks[t]['first_new_node']['L1']}, opens block {blocks[t]['first_new_node']['opens_block']}), "
                    f"{len(blocks[t]['cont_blocks'])} blocks from the cut, {len(blocks[t]['cont_node_sequence'])} nodes" for t in ids)
          + f"; pnext_archived3.csv rows {max(len(pn_lines) - 1, 0)}; psource_c004.csv {sum(1 for _ in open(run_dir / 'psource_c004.csv', encoding='utf-8')) - 1} cuts, "
          f"psource_e036.csv {sum(1 for _ in open(run_dir / 'psource_e036.csv', encoding='utf-8')) - 1} cuts")
    details.append("\n".join(rows))
    details.append("### pnext_archived3.csv\n\n```\n" + "\n".join(pn_lines) + "\n```")

    # ---- 6. pytest ------------------------------------------------------------------------------
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "scripts/tests"], cwd=REPO, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", env=env)
    out = proc.stdout + (("\n" + proc.stderr) if proc.stderr.strip() else "")
    (folder / "pytest_output.txt").write_text(out, encoding="utf-8")
    check(proc.returncode == 0, "check 6, pytest on scripts/tests", f"exit code {proc.returncode}; last line: {out.strip().splitlines()[-1] if out.strip() else '(none)'}")
    details.append("## pytest output\n\n```\n" + out.rstrip() + "\n```")
    u = summary.get("usage", {})
    head = (f" Cost ${summary['total_cost_usd']:.6f} (usage: input {u.get('input_tokens')}, cache read {u.get('cache_read_input_tokens')}, cache write {u.get('cache_creation_input_tokens')}, "
            f"output {u.get('output_tokens')} of which thinking {u.get('thinking_tokens')}; thinking tokens per labeled sentence {summary.get('thinking_tokens_per_labeled_sentence') or 0:.1f}). "
            f"Batch ids: {', '.join(b['batch_id'] for b in batches)}; wall time {(t1 - t0).total_seconds():.0f} s.")
    (folder / "summary.json").write_text(json.dumps({k: v for k, v in summary.items() if k not in ("pnext_rows",)}, indent=2, default=str) + "\n", encoding="utf-8")
    write_report(final=True, extra_head=head)
    print(f"\nReport: {folder / 'TEST_REPORT.md'}\nGate: {'PASS' if all(verdicts) else 'FAIL'}\nTotal API cost: ${summary['total_cost_usd']:.6f}")
    return 0 if all(verdicts) else 1


if __name__ == "__main__":
    sys.exit(main())
