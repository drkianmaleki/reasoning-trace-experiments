"""Unit tests for scripts/s2_resample.py with a stubbed DeepInfra endpoint: the design and the
registered block ends, the conditions in order, the prompts, the per-cut summary, the run loop
(records, pcut rows, Tk, stopping rule, resume, cost guard, departures).  No API call.
Run: python -m pytest -q scripts/tests/test_s2_resample.py"""
import csv
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import s2_resample as R  # noqa: E402


@pytest.fixture(scope="module")
def design():
    return R.load_design()


def test_design_matches_the_registration(design):
    for tid in ("c004", "e036"):
        t = design["traces"][tid]
        assert t["block_ends"] == R.REGISTERED_ENDS[tid] and len(t["prefixes"]) == len(R.REGISTERED_ENDS[tid])
        assert t["a_T"] == R.A_T[tid] and t["tk_trace"] == R.TK_TRACE[tid] == t["reasoning_tokens"]
        for p in t["prefixes"]:
            assert p["text"] == t["text"][:p["char_end"]] and t["text"][:p["char_end"]].endswith(t["text"][t["sentences"][p["block_end_s"]]["char_start"]:p["char_end"]])
    assert len(design["item_prompt"]) == 447 and design["options"]["E"] == "The question is not well posed"
    chk = R.check_prefixes(design)
    assert chk == {"c004": {"prefixes": 46, "matched": 46, "registered": 46}, "e036": {"prefixes": 37, "matched": 37, "registered": 37}}


def test_conditions_in_registered_order(design):
    conds = R.conditions(design)
    assert len(conds) == 2 + 46 + 37
    assert [c["condition"] for c in conds[:2]] == ["nothink", "cut0"] and conds[0]["n"] == 100 and conds[1]["n"] == 25
    assert conds[0]["max_tokens"] == 2000 and conds[1]["max_tokens"] == 16000
    assert conds[0]["prompt"].endswith("<|im_start|>assistant\n<think>\n\n</think>\n\n") and conds[1]["prompt"].endswith("<|im_start|>assistant\n<think>\n")
    assert conds[0]["prompt"].startswith("<|im_start|>user\n" + design["item_prompt"] + "<|im_end|>\n")
    c_cuts = [c for c in conds if c["trace_id"] == "c004"]
    e_cuts = [c for c in conds if c["trace_id"] == "e036"]
    assert [c["m"] for c in c_cuts] == list(range(46)) and [c["m"] for c in e_cuts] == list(range(37))
    assert conds[2]["prefix_id"] == "rb_c004_B00" and conds[2]["block_end_s"] == 7 and conds[2]["prompt"].endswith(design["traces"]["c004"]["prefixes"][0]["text"])
    assert conds[-1]["prefix_id"] == "rb_e036_B36" and conds[-1]["block_end_s"] == 250
    only = R.conditions(design, ["e036"], skip_baselines=True, max_cuts=3)
    assert [c["prefix_id"] for c in only] == ["rb_e036_B00", "rb_e036_B01", "rb_e036_B02"]
    est = R.estimate(conds)
    assert est["total"]["calls"] == 100 + 25 + 83 * 25 and est["total"]["cost_est_stop_usd"] < est["total"]["cost_est_usd"]
    assert set(est["per_trace"]) == {"nothink", "cut0", "c004", "e036"}


def test_summarize_and_stopping():
    cond = {"condition": "cut", "trace_id": "c004", "m": 3, "prefix_id": "rb_c004_B03", "block_end_s": 22, "prefix_char_end": 1000}
    recs = [{"answer": a, "usage": {"prompt_tokens": 500, "completion_tokens": 100}, "cost_usd": 0.01} for a in ["C"] * 21 + ["?"] * 3 + ["E"]]
    row = R.summarize(recs, cond, "C", 380)
    assert row["n"] == 25 and row["count_C"] == 21 and row["count_E"] == 1 and row["count_unresolved"] == 3 and row["count_other"] == 0
    assert row["p_hat"] == 0.84 and row["ci_low"] == pytest.approx(0.6535, abs=2e-4) and row["tk_block"] == 120 and row["prompt_tokens"] == 500
    assert not row["stopped"] and row["cost_usd"] == pytest.approx(0.25) and row["m"] == 3 and row["mean_completion_tokens"] == 100.0
    full = R.summarize([{"answer": "C", "usage": {"prompt_tokens": 500, "completion_tokens": 1}, "cost_usd": 0.0}] * 25, cond, "C", None)
    assert full["stopped"] and full["p_hat"] == 1.0 and full["tk_block"] is None
    base = R.summarize(recs, {"condition": "nothink", "trace_id": "shared", "m": None, "prefix_id": "rb_nothink", "block_end_s": None, "prefix_char_end": 0}, None, None)
    assert base["p_hat"] is None and base["m"] == "nothink" and not base["stopped"]


class StubPost:
    """Returns canned completions: the answer sequence per prefix_id cycles over `answers`."""

    def __init__(self, answers_by_prefix, prompt_tokens_by_prefix, fail_first=()):
        self.answers, self.pt, self.fail_first, self.calls, self.failed = answers_by_prefix, prompt_tokens_by_prefix, set(fail_first), [], set()

    def __call__(self, payload, timeout=None):
        self.calls.append(payload)
        if payload.get("max_tokens") == 1:
            return {"_status": 200, "model": R.MODEL, "choices": [{"text": "!", "finish_reason": "length"}], "usage": {"prompt_tokens": 1, "completion_tokens": 1, "estimated_cost": 0.0}}
        pid = next(p for p in self.answers if payload["prompt"].endswith(self.prefix_tail[p]))
        k = sum(1 for c in self.calls if c["prompt"] == payload["prompt"]) - 1
        if pid in self.fail_first and pid not in self.failed:
            self.failed.add(pid)
            return {"_status": 503, "error": "overloaded"}
        a = self.answers[pid][k % len(self.answers[pid])]
        text = ("</think>\n\nAnswer: " + a) if a != "?" else "</think>\n\nI cannot decide."
        if payload["prompt"].endswith("</think>\n\n"):  # no-think: reply only
            text = ("Answer: " + a) if a != "?" else "no letter"
        return {"_status": 200, "model": R.MODEL, "choices": [{"text": text, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": self.pt[pid], "completion_tokens": 50, "total_tokens": self.pt[pid] + 50, "estimated_cost": 0.001}}


def make_stub(design, conds, answers, pts, fail_first=()):
    stub = StubPost(answers, pts, fail_first)
    stub.prefix_tail = {c["prefix_id"]: c["prompt"][-200:] for c in conds}
    return stub


def test_run_loop_records_pcut_tk_stop_resume_and_departures(design, tmp_path):
    conds = R.conditions(design, ["c004"], n=4, n0=6, max_cuts=3)
    answers = {"rb_nothink": ["C", "E", "?"], "rb_cut0": ["E", "E", "C", "?"], "rb_c004_B00": ["C", "E", "C", "?"], "rb_c004_B01": ["C"], "rb_c004_B02": ["E"]}
    pts = {"rb_nothink": 150, "rb_cut0": 140, "rb_c004_B00": 260, "rb_c004_B01": 300, "rb_c004_B02": 310}
    stub = make_stub(design, conds, answers, pts, fail_first=("rb_c004_B00",))
    out = tmp_path / "run"
    s = R.run(out, design, conds, post=stub, workers=2, log=lambda m: None, sleep=lambda x: None)
    assert s["stopped"] is None and s["M"] == {"c004": 1}
    rows = R.read_pcut(out / "pcut.csv")
    assert [r["prefix_id"] for r in rows] == ["rb_nothink", "rb_cut0", "rb_c004_B00", "rb_c004_B01"]  # B02 skipped by the rule
    assert rows[0]["n"] == "6" and rows[0]["p_hat"] == "" and rows[1]["p_hat"] == ""  # baselines: no a_T
    b0 = rows[2]
    assert b0["n"] == "4" and b0["count_C"] == "2" and b0["p_hat"] == "0.5" and b0["tk_block"] == "120" and b0["stopped"] == "False"
    assert rows[3]["p_hat"] == "1.0" and rows[3]["stopped"] == "True" and rows[3]["tk_block"] == "40"
    recs = [json.loads(l) for l in (out / "continuations.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(recs) == 6 + 4 + 4 + 4
    r = next(x for x in recs if x["id"] == "rb_c004_B00_000")
    assert r["prompt"].endswith(design["traces"]["c004"]["prefixes"][0]["text"]) and r["block"] == 0 and r["cut"] == 7 and r["prefix_char_end"] == 450
    assert r["condition"] == "cut" and r["trace_arm"] == "c004" and set(r) >= {"letters", "chosen", "answer", "usage", "cost_usd", "think_closed", "finish", "cont_text", "seq"}
    assert any(x["answer"] == "?" and x["letters"] == [] for x in recs if x["prefix_id"] == "rb_cut0")
    nothink = [x for x in recs if x["condition"] == "nothink"]
    assert all(x["think_closed"] and not x["think_reopened"] for x in nothink)
    dep = (out / "DEPARTURES.md").read_text(encoding="utf-8")
    assert "retried call rb_c004_B00_" in dep and "attempt 1 of 3 failed" in dep and dep.count("\n") == 1
    assert next(x for x in recs if x["prefix_id"] == "rb_c004_B00" and x["attempt"] == 2)
    log = (out / "_log.txt").read_text(encoding="utf-8")
    assert "slug check PASS" in log and "stopping rule: c004 P_hat = 1 at m = 1" in log and "rb_c004_B02\tskipped" in log
    config = json.loads((out / "config.json").read_text(encoding="utf-8"))
    assert config["slug_check"]["ok"] and config["stop"] == ["<|im_end|>"] and config["M"] == {"c004": 1} and config["prefix_check"]["c004"]["matched"] == 46
    assert stub.calls[0]["max_tokens"] == 1  # the slug check came first
    assert all(c["temperature"] == 1.0 and c["stop"] == ["<|im_end|>"] for c in stub.calls[1:])
    assert {c["max_tokens"] for c in stub.calls[1:]} == {2000, 16000}
    # resume: nothing new to do
    s2 = R.run(out, design, conds, post=stub, workers=2, log=lambda m: None, sleep=lambda x: None, resume=True)
    assert s2["rows"] == [] and len(R.read_pcut(out / "pcut.csv")) == 4 and s2["cost_usd"] == pytest.approx(18 * 0.001)


def test_cost_guard_and_dry_run(design, tmp_path):
    conds = R.conditions(design, ["e036"], skip_baselines=True, n=2, max_cuts=3)
    answers = {c["prefix_id"]: ["E", "C"] for c in conds}
    pts = {c["prefix_id"]: 1000 + 10 * c["m"] for c in conds}
    stub = make_stub(design, conds, answers, pts)
    s = R.run(tmp_path / "guard", design, conds, post=stub, workers=1, log=lambda m: None, sleep=lambda x: None, cost_ceiling=0.0015)
    assert s["stopped"].startswith("cost ceiling before rb_e036_B01") and len(s["rows"]) == 1
    dep = (tmp_path / "guard" / "DEPARTURES.md").read_text(encoding="utf-8")
    assert "cost ceiling" in dep and "Tk(B_m) left empty" in dep  # cut-0 not in this folder
    d = R.run(tmp_path / "dry", design, R.conditions(design), dry_run=True, log=lambda m: None)
    assert d["prefix_check"]["e036"]["matched"] == 37 and (tmp_path / "dry" / "prompts_dry_run.jsonl").exists()
    lines = (tmp_path / "dry" / "prompts_dry_run.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 85 and (tmp_path / "dry" / "DEPARTURES.md").read_text(encoding="utf-8") == ""
    assert not (tmp_path / "dry" / "continuations.jsonl").exists()
