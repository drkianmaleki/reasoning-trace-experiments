"""Unit tests for scripts/s1_judge.py: request construction, parse-and-retry with a stubbed
client, cost arithmetic, agreement arithmetic.  No API call.  Run: python -m pytest -q scripts/tests/test_s1_judge.py"""
import math
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import judge_codec as J  # noqa: E402
import s1_judge as S  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
SENTENCES = REPO / "runs" / "tests" / "t2_split_2026-09-16_2224" / "sentences_source.jsonl"


@pytest.fixture(scope="module")
def inv():
    return J.Inventory.load(S.LABELS_FILE)


@pytest.fixture(scope="module")
def sents():
    return S.load_sentences(SENTENCES)


# ----------------------------------------------------------------------------
# Requests
# ----------------------------------------------------------------------------

def test_build_request_shape(sents):
    prompt = S.PROMPT_FILE.read_text(encoding="utf-8")
    req = S.build_request("e036", sents["e036"], prompt)
    assert req["model"] == "claude-haiku-4-5-20251001" and req["max_tokens"] == 8000
    assert req["extra_body"] == {"temperature": 0} and "temperature" not in req
    assert req["system"] == [{"type": "text", "text": prompt, "cache_control": {"type": "ephemeral"}}]
    assert len(req["messages"]) == 1 and req["messages"][0]["role"] == "user"
    lines = req["messages"][0]["content"].split("\n")
    assert lines[0] == "Trace e036, 254 sentences, indices s0 to s253. Label every sentence."
    assert lines[-1] == "Output the run-length labels now, nothing else."
    idx = [int(m.group(1)) for l in lines[1:-1] for m in [re.match(r"^s(\d+): ", l)] if m]
    assert idx == list(range(254))  # every index exactly once, in order, one line each
    assert lines[2] == "s1: " + sents["e036"][1]["text"]  # the display form, with the ⏎ mark
    assert S.estimate_input_tokens(req) == round((len(prompt) + len(req["messages"][0]["content"])) / 4)


def test_build_request_sonnet(sents):
    prompt = "PROMPT"
    req = S.build_request("e036", sents["e036"], prompt, "sonnet")
    assert req["model"] == "claude-sonnet-5"
    assert "extra_body" not in req and "temperature" not in req  # Sonnet 5 rejects sampling parameters
    assert req["thinking"] == {"type": "disabled"}
    req_h = S.build_request("e036", sents["e036"], prompt, "haiku")
    assert "thinking" not in req_h and req_h["extra_body"] == {"temperature": 0}
    with pytest.raises(KeyError):
        S.build_request("e036", sents["e036"], prompt, "opus")


def test_prompt_files_and_run_id():
    p, l = S.prompt_files("v2")
    assert p.name == "judge_prompt_v2.md" and l.name == "labels_v2.json"
    with pytest.raises(ValueError):
        S.prompt_files("v9")
    from datetime import datetime
    st = datetime(2026, 9, 17, 8, 5)
    assert S.make_run_id("sonnet", "v2", st) == "judge_source_sonnet_v2_2026-09-17_0805"
    assert S.make_run_id("sonnet", "v2", st, "low", 2) == "judge_source_sonnet_v2_thinklow_r2_2026-09-17_0805"
    assert S.make_run_id("haiku", "v1", st, "off", None) == "judge_source_haiku_v1_2026-09-17_0805"


def test_thinking_none_mode(sents):
    req = S.build_request("e036", sents["e036"], "PROMPT", "sonnet", "none")
    assert req["thinking"] == {"type": "disabled"} and req["max_tokens"] == 8000 and "output_config" not in req
    lines = req["messages"][0]["content"].split("\n")
    assert lines[-2] == "Output the run-length labels now, nothing else."
    assert lines[-1] == S.REPLY_INSTRUCTION == ("Reply with the run-length labels only: no reasoning, no commentary, "
                                                "no tags of any kind, nothing before the first run line.")
    off = S.build_request("e036", sents["e036"], "PROMPT", "sonnet", "off")
    assert off["messages"][0]["content"].split("\n")[-1] == "Output the run-length labels now, nothing else."
    from datetime import datetime
    assert S.make_run_id("sonnet", "v2", datetime(2026, 9, 17, 8, 5), "none") == "judge_source_sonnet_v2_thinknone_2026-09-17_0805"
    assert S.thinking_params("haiku", "none") == {}  # allowed on Haiku too (no adaptive parameters involved)


def test_thinking_request_parameters(sents):
    # documented adaptive-thinking fields for Sonnet 5 (thinking-steering-and-cost and effort pages)
    req = S.build_request("e036", sents["e036"], "PROMPT", "sonnet", "low")
    assert req["thinking"] == {"type": "adaptive", "display": "summarized"}
    assert req["output_config"] == {"effort": "low"}
    assert req["max_tokens"] == 24000 and "extra_body" not in req and "temperature" not in req
    assert S.build_request("e036", sents["e036"], "PROMPT", "sonnet", "medium")["output_config"] == {"effort": "medium"}
    off = S.build_request("e036", sents["e036"], "PROMPT", "sonnet", "off")
    assert off["thinking"] == {"type": "disabled"} and off["max_tokens"] == 8000 and "output_config" not in off
    with pytest.raises(ValueError):
        S.build_request("e036", sents["e036"], "PROMPT", "haiku", "low")  # no adaptive thinking on Haiku 4.5
    with pytest.raises(ValueError):
        S.thinking_params("sonnet", "high")


def test_load_sentences_checks_order(tmp_path):
    p = tmp_path / "sentences_x.jsonl"
    p.write_text('{"trace_id": "a", "s": 0, "text": "x"}\n{"trace_id": "a", "s": 2, "text": "y"}\n', encoding="utf-8")
    with pytest.raises(ValueError):
        S.load_sentences(p)
    assert S.collection_name(p) == "x"


# ----------------------------------------------------------------------------
# Cost
# ----------------------------------------------------------------------------

def test_cost_arithmetic():
    u = {"input_tokens": 1_000_000, "output_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}
    assert S.cost_usd(u) == pytest.approx(1.0)
    u = {"input_tokens": 0, "output_tokens": 200_000, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}
    assert S.cost_usd(u) == pytest.approx(1.0)
    u = {"input_tokens": 100, "output_tokens": 10, "cache_creation_input_tokens": 4000, "cache_read_input_tokens": 4000}
    assert S.cost_usd(u) == pytest.approx((100 * 1 + 10 * 5 + 4000 * 0.10 + 4000 * 1.25) / 1e6)
    assert S.add_usage({"input_tokens": 1}, {"input_tokens": 2, "output_tokens": 3}) == {"input_tokens": 3, "output_tokens": 3}
    # Sonnet 5: $2 / $10 per million, cache write $2.50, cache read $0.20
    u = {"input_tokens": 1_000_000, "output_tokens": 100_000, "cache_creation_input_tokens": 1_000_000, "cache_read_input_tokens": 1_000_000}
    assert S.cost_usd(u, "sonnet") == pytest.approx(2.0 + 1.0 + 2.5 + 0.2)
    assert S.cost_usd(u, "haiku") == pytest.approx(1.0 + 0.5 + 1.25 + 0.1)


# ----------------------------------------------------------------------------
# Parse and retry with a stubbed client
# ----------------------------------------------------------------------------

def fake_response(text, model="claude-haiku-4-5-20251001", usage=(100, 10, 0, 0), stop="end_turn", thinking=None, thinking_tokens=None):
    content = []
    if thinking is not None:
        content.append(SimpleNamespace(type="thinking", thinking=thinking, signature="sig"))
    content.append(SimpleNamespace(type="text", text=text))
    details = SimpleNamespace(thinking_tokens=thinking_tokens) if thinking_tokens is not None else None
    return SimpleNamespace(content=content, model=model, stop_reason=stop,
                           usage=SimpleNamespace(input_tokens=usage[0], output_tokens=usage[1],
                                                 cache_creation_input_tokens=usage[2], cache_read_input_tokens=usage[3],
                                                 output_tokens_details=details))


def test_thinking_blocks_are_stored_not_parsed(inv, tmp_path):
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        return fake_response(VALID, model="claude-sonnet-5", usage=(100, 500, 0, 0), thinking="I reason here.", thinking_tokens=480)

    res = S.judge_trace(create, "toy", TOY, "PROMPT", inv, tmp_path / "replies", model_key="sonnet", thinking_mode="low")
    assert res["valid"] and res["attempts"] == 1 and res["leaks"] == [False]
    assert res["thinking_tokens"] == 480 and res["usage"]["thinking_tokens"] == 480 and res["usage"]["output_tokens"] == 500
    assert res["final_stop_reason"] == "end_turn" and res["thinking_mode"] == "low"
    assert (tmp_path / "replies" / "toy_attempt1_thinking.txt").read_text(encoding="utf-8") == "I reason here."
    assert (tmp_path / "replies" / "toy_attempt1.txt").read_text(encoding="utf-8") == VALID  # text blocks only
    assert calls[0]["thinking"] == {"type": "adaptive", "display": "summarized"} and calls[0]["output_config"] == {"effort": "low"}
    assert calls[0]["max_tokens"] == 24000
    assert res["cost_usd"] == pytest.approx((100 * 2 + 500 * 10) / 1e6)  # thinking billed as output
    recs = S.label_records(res, "run_z", "abc", "2026-09-17T00:00:00", "v2")
    assert all(r["thinking_mode"] == "low" and r["thinking_tokens"] == 480 and r["stop_reason"] == "end_turn" for r in recs)


def test_streaming_create_returns_the_final_message():
    class Stream:
        def __init__(self, kwargs):
            self.kwargs = kwargs

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def get_final_message(self):
            return fake_response(VALID, model="claude-sonnet-5", usage=(1, 2, 0, 0), thinking="t", thinking_tokens=1)

    class Client:
        class messages:
            calls = []

            @staticmethod
            def stream(**kwargs):
                Client.messages.calls.append(kwargs)
                return Stream(kwargs)

    create = S.streaming_create(Client)
    msg = create(model="claude-sonnet-5", max_tokens=24000, messages=[])
    assert msg.model == "claude-sonnet-5" and msg.usage.output_tokens_details.thinking_tokens == 1
    assert Client.messages.calls[0]["max_tokens"] == 24000


def test_think_tag_leak_is_flagged_and_retried(inv, tmp_path):
    stub = StubCreate(["<think>\nlong reasoning cut off", VALID])
    res = S.judge_trace(stub, "toy", TOY, "PROMPT", inv, tmp_path / "replies", model_key="sonnet")
    assert res["valid"] and res["attempts"] == 2 and res["leaks"] == [True, False]
    assert res["error"].startswith("unparsable") and res["thinking_tokens"] == 0


class StubCreate:
    def __init__(self, replies):
        self.replies, self.calls = list(replies), []

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return fake_response(self.replies.pop(0), usage=(100, 10, 50, 0))


TOY = [{"s": i, "text": f"sentence {i}"} for i in range(4)]
VALID = "0 Pl.gp\n1-2 Re.ca.al\n3 Co.fa"


def test_first_attempt_valid(inv, tmp_path):
    stub = StubCreate([VALID])
    res = S.judge_trace(stub, "toy", TOY, "PROMPT", inv, tmp_path / "replies")
    assert res["valid"] and res["attempts"] == 1 and res["retry_message"] is None
    assert res["labels"] == [["Planning > global plan"], ["Reasoning > calculation > algebra"],
                             ["Reasoning > calculation > algebra"], ["Conclusion > final answer"]]
    assert res["usage"] == {"input_tokens": 100, "output_tokens": 10, "cache_creation_input_tokens": 50, "cache_read_input_tokens": 0, "thinking_tokens": 0}
    assert res["cost_usd"] == pytest.approx((100 + 50 + 50 * 1.25) / 1e6)
    assert (tmp_path / "replies" / "toy_attempt1.txt").read_text(encoding="utf-8") == VALID
    assert len(stub.calls) == 1 and stub.calls[0]["extra_body"] == {"temperature": 0}
    assert stub.calls[0]["system"][0]["cache_control"] == {"type": "ephemeral"}


def test_retry_after_a_gap_then_valid(inv, tmp_path):
    stub = StubCreate(["0 Pl.gp\n2 Re.ca.al\n3 Co.fa", VALID])
    res = S.judge_trace(stub, "toy", TOY, "PROMPT", inv, tmp_path / "replies")
    assert res["valid"] and res["attempts"] == 2
    assert res["retry_message"].startswith("Your labeling was rejected: gap: sentences 1..1 are not covered at line 2: 2 Re.ca.al. "
                                           "Output the complete labeling again, every index from 0 to 3 exactly once")
    msgs = stub.calls[1]["messages"]
    assert [m["role"] for m in msgs] == ["user", "assistant", "user"]
    assert msgs[1]["content"] == "0 Pl.gp\n2 Re.ca.al\n3 Co.fa" and msgs[2]["content"] == res["retry_message"]
    assert res["usage"]["input_tokens"] == 200 and res["cost_usd"] == pytest.approx(2 * (100 + 50 + 62.5) / 1e6)
    assert (tmp_path / "replies" / "toy_attempt2.txt").exists()
    assert res["stop_reasons"] == ["end_turn", "end_turn"]


def test_sonnet_call_shape_and_cost(inv, tmp_path):
    stub = StubCreate([VALID])
    res = S.judge_trace(stub, "toy", TOY, "PROMPT", inv, tmp_path / "replies", model_key="sonnet")
    call = stub.calls[0]
    assert call["model"] == "claude-sonnet-5" and call["thinking"] == {"type": "disabled"} and "extra_body" not in call
    assert res["model_key"] == "sonnet" and res["cost_usd"] == pytest.approx((100 * 2 + 10 * 10 + 50 * 2.5) / 1e6)
    recs = S.label_records(res, "run_y", "abc", "2026-09-17T00:00:00", "v2")
    assert recs[0]["temperature"] is None and recs[0]["model_key"] == "sonnet" and recs[0]["prompt_file"] == "judge_prompt_v2.md"


def test_two_failures_leave_the_trace_invalid(inv, tmp_path):
    stub = StubCreate(["0 Pl.gp\n1 Zz.zz\n2-3 Co.fa", "```\n0-3 Pl.gp\n```\nextra prose"])
    res = S.judge_trace(stub, "toy", TOY, "PROMPT", inv, tmp_path / "replies")
    assert not res["valid"] and res["attempts"] == 2 and res["labels"] is None
    assert res["error"].startswith("unparsable")
    assert len(stub.calls) == 2


def test_code_fence_is_tolerated_with_a_warning(inv, tmp_path):
    stub = StubCreate(["```\n" + VALID + "\n```"])
    res = S.judge_trace(stub, "toy", TOY, "PROMPT", inv, tmp_path / "replies")
    assert res["valid"] and res["attempts"] == 1 and len(res["warnings"]) == 2


def test_label_records(inv, tmp_path):
    stub = StubCreate([VALID])
    res = S.judge_trace(stub, "toy", TOY, "PROMPT", inv, tmp_path / "replies")
    recs = S.label_records(res, "run_x", "abc", "2026-09-16T00:00:00")
    assert [r["s"] for r in recs] == [0, 1, 2, 3]
    assert recs[1]["labels"] == [{"L1": "Reasoning", "L2": "calculation", "L3": "algebra"}]
    assert recs[0]["labels"] == [{"L1": "Planning", "L2": "global plan", "L3": None}]
    assert recs[0]["raw_reply"] == VALID and recs[1]["raw_reply"] is None
    assert recs[0]["usage"]["input_tokens"] == 100 and recs[1]["usage"] is None and recs[1]["cost_usd"] is None
    assert all(r["attempt"] == 1 and r["valid"] and not r["combined"] and r["run_id"] == "run_x"
               and r["prompt_version"] == "abc" and r["temperature"] == 0 for r in recs)
    assert S.path_of(recs[1]["labels"][0]) == "Reasoning > calculation > algebra"


# ----------------------------------------------------------------------------
# Agreement on a six-sentence toy with a known kappa
# ----------------------------------------------------------------------------

def test_agreement_arithmetic():
    GP, CA, LR, IC, RF = ("Planning > global plan", "Reasoning > calculation > algebra", "Reasoning > logical reasoning",
                          "Conclusion > intermediate conclusion", "Reflection > meta-evaluation of a step")
    reviewed = {"t": [[GP], [CA], [CA], [LR], [IC], [RF]]}
    judge = {"t": [[GP], [CA], [CA, RF], [RF], [IC], [RF]]}
    texts = {"t": [f"s{i}" for i in range(6)]}
    agr = S.agreement(judge, reviewed, texts)
    l1 = agr["levels"][0]
    # Level 1 primaries: reviewed Pl Re Re Re Co Rf, judge Pl Re Re Rf Co Rf -> po 5/6,
    # pe = (1*1 + 3*2 + 1*1 + 1*2)/36 = 10/36, kappa = (30/36 - 10/36)/(26/36) = 20/26
    assert l1["kappa"] == pytest.approx(20 / 26)
    assert l1["primary_agreement"] == pytest.approx(5 / 6)
    assert l1["exact_match"] == pytest.approx(4 / 6)  # s2 (set differs) and s3
    assert l1["mean_jaccard"] == pytest.approx((1 + 1 + 0.5 + 0 + 1 + 1) / 6)
    l3 = agr["levels"][2]
    assert l3["exact_match"] == pytest.approx(4 / 6)
    rows = {(r["level"], r["label"]): r for r in agr["per_label"]}
    re1 = rows[(1, "Reasoning")]
    assert (re1["n_reviewed"], re1["n_judge"], re1["tp"]) == (3, 2, 2)
    assert re1["precision"] == pytest.approx(1.0) and re1["recall"] == pytest.approx(2 / 3) and re1["f1"] == pytest.approx(0.8)
    rf1 = rows[(1, "Reflection")]
    assert (rf1["n_reviewed"], rf1["n_judge"], rf1["tp"]) == (1, 3, 1)
    assert [ (r["s"], r["reviewed"], r["judge"]) for r in agr["residue"]] == [(2, CA, CA + " || " + RF), (3, LR, RF)]
    assert agr["confusions"][1] == [(("Reasoning", "Reflection"), 1)]
    assert agr["confusions"][2][0] == (("Reasoning > logical reasoning", "Reflection > meta-evaluation of a step"), 1)


def test_kappa_edge_cases():
    assert S.kappa(["a", "a"], ["a", "a"]) == 1.0
    assert S.kappa(["a", "a"], ["b", "b"]) == 0.0
    assert math.isnan(S.kappa([], []))
    assert S.kappa(["a", "b"], ["a", "b"]) == pytest.approx(1.0)


def test_rejection_message_format(inv):
    err = J.ReplyError("overlap", 3, "2-4 Re.ca.al", "sentences 2..2 are covered twice")
    msg = S.rejection_message(err, 10)
    assert msg == ("Your labeling was rejected: overlap: sentences 2..2 are covered twice at line 3: 2-4 Re.ca.al. "
                   "Output the complete labeling again, every index from 0 to 9 exactly once, one run per line, codes only.")


def test_batch_mode_is_not_implemented():
    with pytest.raises(NotImplementedError):
        S.main(["--sentences", str(SENTENCES), "--mode", "batch", "--out", "x"])
