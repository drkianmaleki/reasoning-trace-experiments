"""Unit tests for the batch mode and the continuation documents of scripts/s1_judge.py (pipeline
v2, step 5/9), with a stubbed batch client.  No API call.
Run: python -m pytest -q scripts/tests/test_s1_judge_batch.py"""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import derivation as D  # noqa: E402
import judge_codec as J  # noqa: E402
import s1_judge as S  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
LABELS_V3 = REPO / "prompts" / "labels_v3.json"
GP, LP, IV, CA, IC, FA, KW = ("Planning > global plan", "Planning > local plan", "Planning > initiate verification",
                              "Reasoning > calculation > algebra", "Conclusion > intermediate conclusion", "Conclusion > final answer",
                              "Knowledge > world knowledge")


@pytest.fixture(scope="module")
def inv():
    return J.Inventory.load(LABELS_V3)


def fake_message(text, usage=(100, 50, 0, 8000), stop="end_turn", thinking="thought", thinking_tokens=40, model="claude-sonnet-5"):
    content = [SimpleNamespace(type="thinking", thinking=thinking, signature="sig"), SimpleNamespace(type="text", text=text)]
    return SimpleNamespace(content=content, model=model, stop_reason=stop,
                           usage=SimpleNamespace(input_tokens=usage[0], output_tokens=usage[1], cache_creation_input_tokens=usage[2],
                                                 cache_read_input_tokens=usage[3], output_tokens_details=SimpleNamespace(thinking_tokens=thinking_tokens)))


class StubBatches:
    """replies(cid, attempt) -> ("succeeded", text) | ("errored", message) | ("expired", None)."""

    def __init__(self, replies):
        self.replies = replies
        self.created: list[tuple[str, list]] = []
        self.polls: list[str] = []

    def create(self, requests):
        bid = f"msgbatch_test{len(self.created) + 1}"
        self.created.append((bid, list(requests)))
        return SimpleNamespace(id=bid, processing_status="in_progress",
                               request_counts=SimpleNamespace(processing=len(requests), succeeded=0, errored=0, canceled=0, expired=0))

    def retrieve(self, bid):
        self.polls.append(bid)
        n = len(dict(self.created)[bid])
        return SimpleNamespace(id=bid, processing_status="ended", created_at="t0", ended_at="t1",
                               request_counts=SimpleNamespace(processing=0, succeeded=n, errored=0, canceled=0, expired=0))

    def results(self, bid):
        attempt = [b for b, _ in self.created].index(bid) + 1
        for entry in dict(self.created)[bid]:
            kind, payload = self.replies(entry["custom_id"], attempt)
            if kind == "succeeded":
                yield SimpleNamespace(custom_id=entry["custom_id"], result=SimpleNamespace(type="succeeded", message=fake_message(payload)))
            elif kind == "errored":
                err = SimpleNamespace(error=SimpleNamespace(type="api_error", message=payload))
                yield SimpleNamespace(custom_id=entry["custom_id"], result=SimpleNamespace(type="errored", error=err))
            else:
                yield SimpleNamespace(custom_id=entry["custom_id"], result=SimpleNamespace(type=kind))


def stub_client(replies):
    return SimpleNamespace(messages=SimpleNamespace(batches=StubBatches(replies)))


def write_sentences(path, traces):
    with open(path, "w", encoding="utf-8") as fh:
        for tid, texts in traces.items():
            for s, t in enumerate(texts):
                fh.write(json.dumps({"trace_id": tid, "s": s, "text": t}) + "\n")


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def test_safe_custom_id():
    taken = set()
    assert S.safe_custom_id("rs0823_cut000_003", taken) == "rs0823_cut000_003"
    assert S.safe_custom_id("a b/c:d.e", taken) == "a_b_c_d_e"
    assert S.safe_custom_id("a b/c:d.e", taken) == "a_b_c_d_e_1"  # collision
    long = "x" * 80
    cid = S.safe_custom_id(long, taken)
    assert len(cid) == 64 and cid == "x" * 64
    assert len(S.safe_custom_id(long, taken)) == 64 and S.safe_custom_id(long, taken).endswith("_2")
    assert S.safe_custom_id("") == "trace"


def test_batch_params_flattens_extra_body():
    req = {"model": "m", "max_tokens": 1, "extra_body": {"temperature": 0}, "messages": []}
    assert S.batch_params(req) == {"model": "m", "max_tokens": 1, "temperature": 0, "messages": []}
    assert S.batch_params({"model": "m"}) == {"model": "m"}


def test_batch_prices_are_half():
    u = {"input_tokens": 1_000_000, "output_tokens": 1_000_000, "cache_creation_input_tokens": 1_000_000, "cache_read_input_tokens": 1_000_000}
    assert S.cost_usd(u, "sonnet", batch=True) == pytest.approx(1.0 + 5.0 + 1.25 + 0.10)
    assert S.cost_usd(u, "sonnet") == pytest.approx(2.0 + 10.0 + 2.5 + 0.2)
    assert S.BATCH_PRICES["sonnet"] == {"input": 1.0, "output": 5.0, "cache_read": 0.10, "cache_write": 1.25}


def test_max_tokens_for_long_documents():
    assert S.max_tokens_for(375, "sonnet", "low") == 24000
    assert S.max_tokens_for(600, "sonnet", "low") == 24000
    assert S.max_tokens_for(601, "sonnet", "low") == 48000
    assert S.max_tokens_for(1163, "sonnet", "low") == 48000
    assert S.max_tokens_for(1163, "sonnet", "off") == 8000
    sents = [{"s": i, "text": "x"} for i in range(700)]
    assert S.build_request("t", sents, "P", "sonnet", "low")["max_tokens"] == 48000


def test_continuation_message_format(inv):
    prefix = [("Here's a plan:", "Pl.gp"), ("x = 1.", "Re.ca.al"), ("But wait, the classic says more.", "Pl.iv.wdm+Kn.wk.fpc")]
    cont = [{"s": 0, "text": "Wait, is that right?"}, {"s": 1, "text": "Yes."}]
    msg = S.continuation_message("rs_x", prefix, cont)
    lines = msg.split("\n")
    assert lines[0].startswith("Continuation rs_x: a prefix of 3 sentences already labeled")
    assert lines[1] == "Prefix, already labeled (do not relabel):"
    assert lines[2] == "s0: Here's a plan:\tPl.gp" and lines[4] == "s2: But wait, the classic says more.\tPl.iv.wdm+Kn.wk.fpc"
    assert lines[5] == "Continuation to label:"
    assert lines[6] == "c0: Wait, is that right?" and lines[7] == "c1: Yes."
    assert lines[8] == "Output the run-length labels for c0 to c1 now (indices 0 to 1), nothing else."
    empty = S.continuation_message("rs_0", [], cont).split("\n")
    assert "Prefix, already labeled (do not relabel):" not in empty and empty[1] == "Continuation to label:" and empty[2] == "c0: Wait, is that right?"
    assert empty[0].startswith("Continuation rs_0 from an empty prefix: 2 sentences c0 to c1.")
    assert S.label_code([IV + " > " + D.WAIT_LEAF, "Knowledge > world knowledge > famous problem (CRT)"], inv) == "Pl.iv.wdm+Kn.wk.fpc"


def test_label_records_lean_and_full():
    res = {"trace_id": "t", "labels": [[GP], [CA], [CA]], "replies": ["0 Pl.gp\n1-2 Re.ca.al"], "model": "claude-sonnet-5", "model_key": "sonnet",
           "thinking_mode": "low", "usage": {"input_tokens": 1}, "cost_usd": 0.5, "attempts": 2, "valid": True, "thinking_tokens": 7,
           "final_stop_reason": "end_turn", "batch_ids": ["b1", "b2"], "custom_id": "t", "max_tokens": [24000, 48000],
           "r4_notes": [None, {"action": "prepended", "changed": True, "before": [CA]}, None]}
    lean = S.label_records(res, "run", "sha", "ts", "v3", {"prefix_id": "p"}, lean=True)
    assert lean[0]["usage"] == {"input_tokens": 1} and "usage" not in lean[1] and lean[0]["raw_reply"] == "0 Pl.gp\n1-2 Re.ca.al"
    assert all(r["batch_id"] == "b2" and r["custom_id"] == "t" and r["attempt"] == 2 and r["cost_usd"] == 0.5 and r["stop_reason"] == "end_turn"
               and r["thinking_tokens"] == 7 and r["prefix_id"] == "p" for r in lean)
    assert lean[1]["r4_applied"] and lean[1]["labels_before_r4"] == [{"L1": "Reasoning", "L2": "calculation", "L3": "algebra"}] and not lean[0]["r4_applied"]
    assert "labels_before_r4" not in lean[0] and lean[0]["max_tokens"] == [24000, 48000]
    full = S.label_records(res, "run", "sha", "ts", "v3")
    assert full[1]["model"] == "claude-sonnet-5" and full[1]["usage"] is None and full[1]["cost_usd"] is None and full[0]["cost_usd"] == 0.5
    assert full[1]["prompt_file"] == "judge_prompt_v3.md" and full[1]["batch_id"] == "b2"


def test_finalize_document_on_a_continuation():
    doc = {"trace_id": "c", "n": 3, "sents": [{"s": i, "text": t} for i, t in enumerate(["Wait, check.", "x = 2.", "So x = 2."])],
           "texts": ["Wait, check.", "x = 2.", "So x = 2."], "continuation": True, "meta": {"prefix_id": "p", "trace_arm": "c004", "cut": 3, "seq": 1},
           "prefix_labels": [[GP], [CA], [CA]], "prefix_texts": ["Plan.", "x = 1.", "x + 1 = 2."], "prefix_codes": ["Pl.gp", "Re.ca.al", "Re.ca.al"], "prefix_s": [0, 1, 2]}
    res = {"labels": [[CA], [CA], [IC]]}
    rec = S.finalize_document(doc, res)
    assert res["labels"] == [[D.R4_PATH, CA], [CA], [IC]] and res["labels_raw"] == [[CA], [CA], [IC]]
    assert rec["prefix_n"] == 3 and rec["last_prefix_node_label"] == "Reasoning" and rec["first_sentence_r4"]
    fn = rec["first_new_node"]
    assert fn["L1"] == "Planning" and fn["opens_block"] and fn["opener_rule"] == "R4" and fn["s_start"] == 3 and not fn["spans_cut"]
    assert rec["cont_node_sequence"] == ["Planning", "Reasoning", "Conclusion"] and [b["m"] for b in rec["cont_blocks"]] == [1]
    assert S.block_sequence_text(rec).startswith("B1 (R4): [Pl+Re]₁ Re₁ Co₁")
    # a continuation that continues the prefix's last node
    doc2 = dict(doc, texts=["x = 3.", "x = 4.", "So."], sents=[{"s": i, "text": t} for i, t in enumerate(["x = 3.", "x = 4.", "So."])])
    res2 = {"labels": [[CA], [CA], [IC]]}
    rec2 = S.finalize_document(doc2, res2)
    fn2 = rec2["first_new_node"]
    assert fn2["L1"] == "Reasoning" and not fn2["opens_block"] and fn2["spans_cut"] and fn2["s_start"] == 1 and not rec2["first_sentence_r4"]
    # a whole trace
    doc3 = {"trace_id": "w", "n": 2, "sents": [{"s": 0, "text": "Plan."}, {"s": 1, "text": "x = 1."}], "texts": ["Plan.", "x = 1."], "continuation": False,
            "meta": None, "prefix_labels": [], "prefix_texts": [], "prefix_codes": [], "prefix_s": []}
    rec3 = S.finalize_document(doc3, {"labels": [[GP], [CA]]})
    assert rec3["label_source"] == "judge" and "first_new_node" not in rec3 and S.block_sequence_text(rec3) == "Pl₀ Re₀"


def test_follow_up_request():
    req = {"model": "m", "max_tokens": 24000, "messages": [{"role": "user", "content": "u"}]}
    parse_fail = {"text": "0 Pl.gp", "retry_message": "again", "stop_reason": "max_tokens"}
    r = S.follow_up_request(req, parse_fail)
    assert r["max_tokens"] == 48000 and [m["role"] for m in r["messages"]] == ["user", "assistant", "user"] and r["messages"][2]["content"] == "again"
    r = S.follow_up_request(req, {"text": "0 Pl.gp", "retry_message": "again", "stop_reason": "end_turn"})
    assert r["max_tokens"] == 24000
    r = S.follow_up_request(req, {"text": None, "retry_message": None, "stop_reason": None})
    assert r == req
    assert S.follow_up_request({"model": "m", "max_tokens": 60000, "messages": []}, parse_fail)["max_tokens"] == 96000
    # an empty reply (cap exhausted inside the thinking): fresh request, cap doubled, no empty assistant turn
    r = S.follow_up_request(req, {"text": "", "retry_message": "again", "stop_reason": "max_tokens"})
    assert r["messages"] == req["messages"] and r["max_tokens"] == 48000
    r = S.follow_up_request(req, {"text": "  \n", "retry_message": "again", "stop_reason": "end_turn"})
    assert r["messages"] == req["messages"] and r["max_tokens"] == 48000


def test_ordinary_retry_after_an_empty_reply_sends_no_empty_assistant_turn(inv, tmp_path):
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        return fake_message("" if len(calls) == 1 else "0 Pl.gp\n1-3 Re.ca.al", stop="max_tokens" if len(calls) == 1 else "end_turn")

    sents = [{"s": i, "text": f"s{i}"} for i in range(4)]
    res = S.judge_trace(create, "t", sents, "P", inv, tmp_path / "replies", "sonnet", "low")
    assert res["valid"] and res["attempts"] == 2 and len(calls[1]["messages"]) == 1 and calls[1]["max_tokens"] == 48000


def test_poll_batch_returns_none_on_timeout():
    calls = []

    class C:
        class messages:
            class batches:
                @staticmethod
                def retrieve(bid):
                    calls.append(bid)
                    return SimpleNamespace(processing_status="in_progress", request_counts=SimpleNamespace(processing=1, succeeded=0, errored=0, canceled=0, expired=0))

    slept = []
    assert S.poll_batch(C, "b", log=lambda s: None, poll_seconds=60, max_wait_seconds=0, sleep=slept.append) is None
    assert calls == ["b"] and slept == []


# ----------------------------------------------------------------------------
# judge_batch with the stub: a parse failure and an API failure go to one follow-up batch
# ----------------------------------------------------------------------------

def test_judge_batch_follow_up(inv, tmp_path):
    good = "0 Pl.gp\n1-2 Re.ca.al\n3 Co.fa"

    def replies(cid, attempt):
        if cid == "b" and attempt == 1:
            return "succeeded", "0 Pl.gp\n2-3 Re.ca.al"  # gap
        if cid == "c" and attempt == 1:
            return "errored", "overloaded"
        if cid == "d":
            return "expired", None
        return "succeeded", good

    client = stub_client(replies)
    docs = [{"trace_id": t, "n": 4, "texts": ["Plan.", "x", "y", "Answer: B."], "sents": [], "continuation": False, "prefix_labels": [], "prefix_texts": []} for t in "abcd"]
    requests = {t: {"model": "claude-sonnet-5", "max_tokens": 24000, "system": [], "messages": [{"role": "user", "content": t}], "thinking": {"type": "adaptive"}} for t in "abcd"}
    logs = []
    out = S.judge_batch(client, docs, requests, {t: t for t in "abcd"}, tmp_path, inv, "sonnet", "low", logs.append, sleep=lambda s: None)
    res = out["results"]
    assert out["stopped"] is None and [b["batch_id"] for b in out["batches"]] == ["msgbatch_test1", "msgbatch_test2"]
    assert out["batches"][0]["n_entries"] == 4 and out["batches"][1]["n_entries"] == 3 and out["batches"][1]["custom_ids"] == ["b", "c", "d"]
    assert res["a"]["valid"] and res["a"]["attempts"] == 1 and res["a"]["batch_ids"] == ["msgbatch_test1"]
    assert res["b"]["valid"] and res["b"]["attempts"] == 2 and res["b"]["batch_ids"] == ["msgbatch_test1", "msgbatch_test2"] and res["b"]["error_kinds"] == ["gap"]
    assert res["b"]["retry_message"].startswith("Your labeling was rejected: gap")
    follow = dict(client.messages.batches.created)["msgbatch_test2"]
    b_entry = next(e for e in follow if e["custom_id"] == "b")
    assert [m["role"] for m in b_entry["params"]["messages"]] == ["user", "assistant", "user"] and b_entry["params"]["max_tokens"] == 24000
    c_entry = next(e for e in follow if e["custom_id"] == "c")
    assert c_entry["params"]["messages"] == [{"role": "user", "content": "c"}]
    assert res["c"]["valid"] and res["c"]["attempts"] == 2 and res["c"]["error_kinds"] == ["errored"] and res["c"]["error"] is None
    assert not res["d"]["valid"] and res["d"]["attempts"] == 2 and res["d"]["error_kinds"] == ["expired", "expired"] and res["d"]["error"].startswith("expired")
    assert res["a"]["cost_usd"] == pytest.approx((100 * 1 + 50 * 5 + 8000 * 0.10) / 1e6)  # batch prices
    assert res["b"]["usage"]["input_tokens"] == 200 and res["b"]["thinking_tokens"] == 80
    assert (tmp_path / "replies" / "b_attempt1.txt").read_text(encoding="utf-8") == "0 Pl.gp\n2-3 Re.ca.al"
    assert (tmp_path / "replies" / "b_attempt2_thinking.txt").read_text(encoding="utf-8") == "thought"
    state = json.loads((tmp_path / "batch_state.json").read_text(encoding="utf-8"))
    assert state["status"] == "ended" and len(state["batches"]) == 2 and state["custom_ids"] == {t: t for t in "abcd"}
    assert any("request_counts" in l for l in logs)


def test_judge_batch_resume_skips_submission(inv, tmp_path):
    client = stub_client(lambda cid, attempt: ("succeeded", "0-3 Pl.gp"))
    client.messages.batches.created.append(("msgbatch_old", [{"custom_id": "a", "params": {}}]))
    docs = [{"trace_id": "a", "n": 4, "texts": ["1", "2", "3", "4"], "sents": [], "continuation": False, "prefix_labels": [], "prefix_texts": []}]
    out = S.judge_batch(client, docs, {"a": {"model": "m", "max_tokens": 1, "messages": []}}, {"a": "a"}, tmp_path, inv, "sonnet", "low",
                        lambda s: None, resume_batch="msgbatch_old", sleep=lambda s: None)
    assert out["results"]["a"]["valid"] and out["batches"][0]["batch_id"] == "msgbatch_old" and len(client.messages.batches.created) == 1


# ----------------------------------------------------------------------------
# run_judge end to end in batch mode with the stub (whole traces, then continuations)
# ----------------------------------------------------------------------------

def test_run_judge_batch_whole_traces(tmp_path):
    sp = tmp_path / "sentences_toy.jsonl"
    write_sentences(sp, {"t1": ["Plan.", "x = 1.", "Wait, no.", "x = 2.", "Answer: B."], "t2": ["Plan.", "y = 1.", "Answer: A."]})
    replies = {"t1": "0 Pl.gp\n1-3 Re.ca.al\n4 Co.fa", "t2": "0 Pl.gp\n1 Re.ca.al\n2 Co.fa"}
    client = stub_client(lambda cid, attempt: ("succeeded", replies[cid]))
    out = tmp_path / "run"
    summary = S.run_judge(sp, out, client=client, model_key="sonnet", prompt_version="v3", thinking_mode="low", mode="batch",
                          archived_meta_path=None, sleep=lambda s: None, log=lambda s: None)
    assert summary["stopped"] is None and summary["n_valid"] == 2 and summary["mode"] == "batch" and not summary["continuations"]
    labels = [json.loads(l) for l in (out / "labels_toy_judge.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(labels) == 8 and labels[2]["r4_applied"] and labels[2]["labels"] == [{"L1": "Planning", "L2": "initiate verification", "L3": D.WAIT_LEAF},
                                                                                     {"L1": "Reasoning", "L2": "calculation", "L3": "algebra"}]
    assert labels[2]["combined"] and labels[2]["batch_id"] == "msgbatch_test1" and labels[2]["custom_id"] == "t1"
    blocks = [json.loads(l) for l in (out / "blocks_toy_judge.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [(b["s_start"], b["opener_rule"]) for b in blocks[0]["blocks"]] == [(0, "R1"), (2, "R4"), (4, "R3")]
    traces = [json.loads(l) for l in (out / "traces_toy_judge.jsonl").read_text(encoding="utf-8").splitlines()]
    assert traces[0]["r4_changed"] == 1 and traces[0]["blocks"] == 3 and traces[0]["batch_ids"] == ["msgbatch_test1"]
    assert (out / "pcorpus_L1.csv").exists() and (out / "pcorpus_L1_rownorm.csv").exists() and (out / "summary.md").exists()
    assert json.loads((out / "custom_ids.json").read_text(encoding="utf-8")) == {"t1": "t1", "t2": "t2"}
    req = json.loads((out / "requests" / "t1.json").read_text(encoding="utf-8"))
    assert req["system"][0]["text"].startswith("<prompt judge_prompt_v3.md sha256 ")  # the prompt itself is not copied 44 times
    config = json.loads((out / "config.json").read_text(encoding="utf-8"))
    assert config["mode"] == "batch" and config["prices_usd_per_million"]["output"] == 5.0 and config["batches"][0]["batch_id"] == "msgbatch_test1"
    # t1 nodes Pl Re [Pl+Re] Re Co (the combined Wait sentence counts under Planning), t2 nodes Pl Re Co: Planning -> Reasoning 3 times
    assert summary["pcorpus"]["counts"]["Planning"]["Reasoning"] == 3 and summary["pcorpus"]["blocks_per_trace"] == {"min": 2, "median": 2.5, "max": 3}


def test_run_judge_batch_continuations(tmp_path):
    meta = tmp_path / "archived.jsonl"
    meta.write_text(json.dumps({"id": "rs_c004_cut015_000", "prefix_id": "rs_c004_cut015", "trace_arm": "c004", "cut": 15, "seq": 0}) + "\n"
                    + json.dumps({"id": "rs_cut000_000", "prefix_id": "rs_cut000", "trace_arm": "shared", "cut": 0, "seq": 0}) + "\n", encoding="utf-8")
    sp = tmp_path / "sentences_archived2.jsonl"
    write_sentences(sp, {"rs_c004_cut015_000": ["Wait, let me re-read.", "The prompt says 1.10.", "So x < 0.55."], "rs_cut000_000": ["Here's a plan:", "x = 1."]})
    replies = {"rs_c004_cut015_000": "0 Pl.iv.wdm\n1 Rs.rtp.qt\n2 Co.ic", "rs_cut000_000": "0 Pl.gp\n1 Re.ca.al"}
    created = []
    client = stub_client(lambda cid, attempt: ("succeeded", replies[cid]))
    out = tmp_path / "run"
    summary = S.run_judge(sp, out, client=client, model_key="sonnet", prompt_version="v3", thinking_mode="low", mode="batch",
                          archived_meta_path=meta, sleep=lambda s: None, log=lambda s: None)
    assert summary["stopped"] is None and summary["continuations"] and summary["n_valid"] == 2
    entry = {e["custom_id"]: e for e in client.messages.batches.created[0][1]}
    msg = entry["rs_c004_cut015_000"]["params"]["messages"][0]["content"]
    n_prefix = sum(1 for r in S.load_sentences(S.SENTENCES_SOURCE)["c004"] if r["old_s"] <= 15)
    assert n_prefix == 17 and f"a prefix of {n_prefix} sentences" in msg.split("\n")[0]  # old s0..s15 = 16 old sentences, one split in two
    assert msg.split("\n")[2] == "s0: Here's a thinking process that leads to the suggested answer:\tPl.gp"
    assert "Continuation to label:\nc0: Wait, let me re-read.\n" in msg
    assert "Prefix, already labeled" not in entry["rs_cut000_000"]["params"]["messages"][0]["content"]
    assert (out / "labels_source_reviewed_v4.jsonl").exists()
    rev = [json.loads(l) for l in (out / "labels_source_reviewed_v4.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(rev) == 629 and rev[0]["source"] == "reviewed_v4" and rev[0]["old_s"] == 0
    blocks = {json.loads(l)["trace_id"]: json.loads(l) for l in (out / "blocks_archived2_judge.jsonl").read_text(encoding="utf-8").splitlines()}
    b = blocks["rs_c004_cut015_000"]
    assert b["prefix_n"] == 17 and b["first_new_node"]["L1"] == "Planning" and b["first_new_node"]["opens_block"] and b["first_new_node"]["opener_rule"] == "R4"
    assert b["first_sentence_r4"] and b["label_source"] == "reviewed_v4+judge" and b["last_prefix_node_label"] == "Reasoning"
    b0 = blocks["rs_cut000_000"]
    assert b0["prefix_n"] == 0 and b0["first_new_node"]["opens_block"] and b0["last_prefix_node_label"] is None and b0["cut"] == 0
    rows = summary["pnext_rows"]
    assert [r["prefix_id"] for r in rows] == ["rs_cut000", "rs_c004_cut015"]
    assert rows[1]["next_Planning"] == 1 and rows[1]["opens_block"] == 1 and rows[1]["first_is_wait"] == 1 and rows[1]["n"] == 1 and rows[1]["last_node_label"] == "Reasoning"
    assert (out / "pnext_archived2.csv").exists() and (out / "psource_c004.csv").exists() and (out / "psource_e036.csv").exists()
    ps = (out / "psource_c004.csv").read_text(encoding="utf-8").splitlines()
    assert len(ps) == 47 and ps[0].startswith("m,s_cut,last_node,last_node_label,source_next_node,source_next_label,next_opener_rule")  # 46 cuts + header
    labels = [json.loads(l) for l in (out / "labels_archived2_judge.jsonl").read_text(encoding="utf-8").splitlines()]
    assert labels[0]["prefix_id"] == "rs_c004_cut015" and labels[0]["prefix_n"] == 17 and labels[0]["cut"] == 15 and labels[0]["trace_arm"] == "c004"


def test_run_judge_rejects_a_mixed_collection(tmp_path):
    meta = tmp_path / "archived.jsonl"
    meta.write_text(json.dumps({"id": "rs_cut000_000", "prefix_id": "rs_cut000", "trace_arm": "shared", "cut": 0, "seq": 0}) + "\n", encoding="utf-8")
    sp = tmp_path / "sentences_mixed.jsonl"
    write_sentences(sp, {"rs_cut000_000": ["a"], "other": ["b"]})
    with pytest.raises(ValueError):
        S.run_judge(sp, tmp_path / "run", dry_run=True, model_key="sonnet", prompt_version="v3", thinking_mode="low", mode="batch", archived_meta_path=meta, log=lambda s: None)


def test_ordinary_retry_doubles_the_cap_after_max_tokens(inv, tmp_path):
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        return fake_message("0 Pl.gp" if len(calls) == 1 else "0 Pl.gp\n1-3 Re.ca.al", stop="max_tokens" if len(calls) == 1 else "end_turn")

    sents = [{"s": i, "text": f"s{i}"} for i in range(4)]
    res = S.judge_trace(create, "t", sents, "P", inv, tmp_path / "replies", "sonnet", "low")
    assert res["valid"] and res["attempts"] == 2 and res["max_tokens"] == [24000, 48000] and calls[1]["max_tokens"] == 48000
