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


# ----------------------------------------------------------------------------
# Parse and retry with a stubbed client
# ----------------------------------------------------------------------------

def fake_response(text, model="claude-haiku-4-5-20251001", usage=(100, 10, 0, 0), stop="end_turn"):
    return SimpleNamespace(content=[SimpleNamespace(type="text", text=text)], model=model, stop_reason=stop,
                           usage=SimpleNamespace(input_tokens=usage[0], output_tokens=usage[1],
                                                 cache_creation_input_tokens=usage[2], cache_read_input_tokens=usage[3]))


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
    assert res["usage"] == {"input_tokens": 100, "output_tokens": 10, "cache_creation_input_tokens": 50, "cache_read_input_tokens": 0}
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
