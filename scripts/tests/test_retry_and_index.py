"""Unit tests for s1_judge.retry_failed (with a stubbed batch client) and scripts/large_files_index.py.
Run: python -m pytest -q scripts/tests/test_retry_and_index.py"""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import large_files_index as LFI  # noqa: E402
import s1_judge as S  # noqa: E402
from test_s1_judge_batch import stub_client, write_sentences  # noqa: E402


def test_retry_failed_merges_the_parsed_traces(tmp_path):
    meta = tmp_path / "archived.jsonl"
    meta.write_text(json.dumps({"id": "rs_c004_cut015_000", "prefix_id": "rs_c004_cut015", "trace_arm": "c004", "cut": 15, "seq": 0}) + "\n"
                    + json.dumps({"id": "rs_c004_cut015_001", "prefix_id": "rs_c004_cut015", "trace_arm": "c004", "cut": 15, "seq": 1}) + "\n"
                    + json.dumps({"id": "rs_cut000_000", "prefix_id": "rs_cut000", "trace_arm": "shared", "cut": 0, "seq": 0}) + "\n", encoding="utf-8")
    sp = tmp_path / "sentences_archived3.jsonl"
    write_sentences(sp, {"rs_c004_cut015_000": ["Wait, re-read.", "x < 0.55."], "rs_c004_cut015_001": ["So x < 0.55.", "Answer: E."], "rs_cut000_000": ["Plan:", "x = 1."]})
    good = {"rs_c004_cut015_000": "0 Pl.iv.wdm\n1 Re.lr.al", "rs_c004_cut015_001": "0 Co.ic\n1 Co.fa", "rs_cut000_000": "0 Pl.gp\n1 Re.ca.al"}
    bad = "0 Pl.gp\n0 Re.ca.al"  # overlap

    def replies(cid, attempt):  # two traces fail on both attempts of the run
        return ("succeeded", bad) if cid.startswith("rs_c004") else ("succeeded", good[cid])

    out = tmp_path / "run"
    summary = S.run_judge(sp, out, client=stub_client(replies), model_key="sonnet", prompt_version="v3", thinking_mode="low", mode="batch",
                          archived_meta_path=meta, sleep=lambda s: None, log=lambda s: None)
    assert summary["n_valid"] == 1 and sorted(summary["failures"]) == ["rs_c004_cut015_000", "rs_c004_cut015_001"]
    rows = {r["prefix_id"]: r for r in summary["pnext_rows"]}
    assert rows["rs_c004_cut015"]["n_failed"] == 2 and rows["rs_c004_cut015"]["n_labeled"] == 0
    n_labels_before = len((out / "labels_archived3_judge.jsonl").read_text(encoding="utf-8").splitlines())

    # the retry: one parses, one still fails
    def retry_replies(cid, attempt):
        return ("succeeded", good[cid] if cid.endswith("_000") else bad)

    client = stub_client(retry_replies)
    res = S.retry_failed(out, client=client, log=lambda s: None, sleep=lambda s: None)
    assert res["retried"] == ["rs_c004_cut015_000", "rs_c004_cut015_001"] and res["parsed"] == ["rs_c004_cut015_000"]
    assert [f["trace_id"] for f in res["failed"]] == ["rs_c004_cut015_001"] and res["stopped"] is None
    assert len(res["batches"]) == 1 and res["batches"][0]["attempt"] == 3 and res["batches"][0]["n_entries"] == 2
    entry = {e["custom_id"]: e for e in client.messages.batches.created[0][1]}
    msg = entry["rs_c004_cut015_000"]["params"]["messages"][0]["content"]
    assert msg.endswith("\n" + S.FORMAT_CHECK) and len(entry["rs_c004_cut015_000"]["params"]["messages"]) == 1  # fresh request, line appended
    assert res["cost_usd"] > 0 and res["cost_usd"] == pytest.approx(2 * (100 * 1 + 50 * 5 + 8000 * 0.10) / 1e6)
    labels = [json.loads(l) for l in (out / "labels_archived3_judge.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(labels) == n_labels_before + 2
    new = [r for r in labels if r["trace_id"] == "rs_c004_cut015_000"]
    assert new[0]["attempt"] == 3 and new[0]["batch_id"] == "msgbatch_test1" and new[0]["r4_applied"] and new[0]["prefix_id"] == "rs_c004_cut015"
    traces = {json.loads(l)["trace_id"]: json.loads(l) for l in (out / "traces_archived3_judge.jsonl").read_text(encoding="utf-8").splitlines()}
    t = traces["rs_c004_cut015_000"]
    assert t["valid"] and t["attempts"] == 3 and len(t["batch_ids"]) == 3 and len(t["stop_reasons"]) == 3 and t["retry_extra_line"] == S.FORMAT_CHECK
    assert t["usage"]["input_tokens"] == 300 and t["cost_usd"] == pytest.approx(3 * (100 * 1 + 50 * 5 + 8000 * 0.10) / 1e6)
    assert not traces["rs_c004_cut015_001"]["valid"] and traces["rs_c004_cut015_001"]["attempts"] == 3 and traces["rs_cut000_000"]["attempts"] == 1
    blocks = [json.loads(l) for l in (out / "blocks_archived3_judge.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [b["trace_id"] for b in blocks] == ["rs_cut000_000", "rs_c004_cut015_000"]
    assert (out / "replies" / "rs_c004_cut015_000_attempt3.txt").exists() and (out / "batch_state_retry.json").exists()
    assert (out / "requests" / "rs_c004_cut015_000_retry.json").exists()
    pn = [l.split(",") for l in (out / "pnext_archived3.csv").read_text(encoding="utf-8").splitlines()]
    row = dict(zip(pn[0], next(r for r in pn[1:] if r[0] == "rs_c004_cut015")))
    assert (row["n"], row["n_labeled"], row["n_failed"], row["next_Planning"], row["first_is_wait"]) == ("2", "1", "1", "1", "1")
    summary_md = (out / "summary.md").read_text(encoding="utf-8")
    assert "Retry of the failed traces" in summary_md and "3 documents, 2 labeled, 1 failed" in summary_md
    config = json.loads((out / "config.json").read_text(encoding="utf-8"))
    assert config["retry_failed"]["parsed"] == ["rs_c004_cut015_000"] and len(config["batches"]) == 3
    # a second retry finds one failed trace, and nothing to do when all are valid
    res2 = S.retry_failed(out, client=stub_client(lambda cid, attempt: ("succeeded", good[cid])), log=lambda s: None, sleep=lambda s: None)
    assert res2["retried"] == ["rs_c004_cut015_001"] and res2["parsed"] == ["rs_c004_cut015_001"] and res2["batches"][0]["attempt"] == 4
    res3 = S.retry_failed(out, client=None, log=lambda s: None)
    assert res3["retried"] == [] and res3["batches"] == []


def test_retry_failed_rejects_an_ordinary_run(tmp_path):
    (tmp_path / "config.json").write_text(json.dumps({"collection": "x", "mode": "ordinary", "model_key": "sonnet", "prompt_version": "v3",
                                                       "thinking_mode": "low", "prompt_sha256": "x"}), encoding="utf-8")
    with pytest.raises(ValueError):
        S.retry_failed(tmp_path, client=None, log=lambda s: None)


def test_large_files_index_provenance_and_render(tmp_path):
    root = tmp_path
    split = root / "runs" / "experiments" / "s0_split_x"
    split.mkdir(parents=True)
    (split / "config.json").write_text(json.dumps({"script": "scripts/s0_split.py", "git_commit": "abcdef1234567890", "collections": {
        "archived500": {"records": 3, "traces": 1, "inputs": [{"path": "archive/x.jsonl", "sha256": "0123456789abcdef0123"}]}}}), encoding="utf-8")
    sf = split / "sentences_archived500.jsonl"
    sf.write_text('{"a":1}\n{"a":2}\n{"a":3}\n', encoding="utf-8")
    judge = root / "runs" / "experiments" / "judge_archived500_x"
    judge.mkdir(parents=True)
    (judge / "config.json").write_text(json.dumps({"run_id": "judge_archived500_x", "model": "claude-sonnet-5", "mode": "batch", "prompt_version": "v3",
                                                   "prompt_sha256": "e999f7081d5a", "thinking_mode": "low", "git_commit": "cb37247411", "batches": [{"batch_id": "msgbatch_1"}]}), encoding="utf-8")
    (judge / "batch_state_retry.json").write_text(json.dumps({"batches": [{"batch_id": "msgbatch_2"}]}), encoding="utf-8")
    (judge / "traces_archived500_judge.jsonl").write_text('{"trace_id":"a","cost_usd":1.5}\n{"trace_id":"b","cost_usd":0.25}\n', encoding="utf-8")
    lf = judge / "labels_archived500_judge.jsonl"
    lf.write_text('{"s":0}\n{"s":1}\n', encoding="utf-8")
    d1 = LFI.describe(sf, root)
    assert d1["records"] == 3 and d1["regenerable"] == "yes" and d1["regenerate"] == "python scripts/s0_split.py --collection archived500 --out runs/experiments/s0_split_x/"
    assert "scripts/s0_split.py" in d1["produced_by"] and "no API cost" in d1["produced_by"] and d1["path"] == "runs/experiments/s0_split_x/sentences_archived500.jsonl"
    assert d1["sha256"] == LFI.sha256_of_file(sf) and len(d1["sha256"]) == 64
    d2 = LFI.describe(lf, root)
    assert d2["regenerable"].startswith("no") and "msgbatch_1, msgbatch_2" in d2["produced_by"] and "cost $1.75 at batch prices" in d2["produced_by"]
    assert "claude-sonnet-5" in d2["produced_by"] and d2["records"] == 2
    text = LFI.render([d1, d2], 20)
    assert text.startswith("# Large data files held locally (not in git)") and LFI.AVAILABILITY in text
    assert text.index("judge_archived500_x") < text.index("s0_split_x")  # sorted by path
    assert f"| `runs/experiments/s0_split_x/sentences_archived500.jsonl` | 0.0 MB ({sf.stat().st_size} bytes) | 3 |" in text
    assert "(no ignored file over the threshold is present)" in LFI.render([], 20)
    unknown = root / "runs" / "other" / "big.bin"
    unknown.parent.mkdir(parents=True)
    unknown.write_bytes(b"x" * 10)
    assert LFI.describe(unknown, root)["regenerable"] == "unknown"


def test_large_files_index_on_the_repo():
    entries = LFI.build(LFI.REPO, 20)
    paths = {e["path"] for e in entries}
    assert all(p.startswith("runs/") for p in paths)
    assert all(e["mb"] > 20 for e in entries)
    for e in entries:
        if e["path"].endswith("labels_archived500_judge.jsonl"):
            assert e["regenerable"].startswith("no") and "scripts/s1_judge.py" in e["produced_by"]
        if e["path"].endswith("sentences_archived500.jsonl"):
            assert e["regenerable"] == "yes"
