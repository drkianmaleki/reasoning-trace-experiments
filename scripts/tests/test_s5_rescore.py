"""Module test of scripts/s5_rescore.py: the strict reading of the answer letter (decision P6,
2026-09-19) on synthetic replies, and the derived files on a small synthetic run.  When the
stage-one run is present, the reading is also checked against the numbers of Kian's own check.
Run: python -m pytest -q scripts/tests/test_s5_rescore.py"""
import csv
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import s5_rescore as S5  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
RUN = REPO / "runs" / "experiments" / "resample_blocks_2026-09-17_1759"

THINK = "some thinking\n</think>\n\n"


@pytest.mark.parametrize("text,finish,closed,answer", [
    (THINK + "Reasoning.\n\nAnswer: C", "stop", True, "C"),
    (THINK + "Reasoning.\n\nAnswer: (C)", "stop", True, "C"),                      # missed by the registered scorer
    (THINK + "Reasoning.\n\n**Answer:** C.", "stop", True, "C"),
    (THINK + "Reasoning.\n\n**Answer: E**", "stop", True, "E"),
    (THINK + "Reasoning.\n\nTherefore, Answer: C.", "stop", True, "C"),
    (THINK + "Reasoning.\n\nAnswer: [F]\n\n", "stop", True, "F"),
    (THINK + "Reasoning.\n\nAnswer: (E) The question is not well posed.", "stop", True, "E"),
    (THINK + "Reasoning.\n\nAnswer: The question is not well posed", "stop", True, "E"),
    (THINK + "Reasoning.\n\nAnswer: (E) It is \\$0.05", "stop", True, "?"),        # letter and text disagree
    (THINK + "Reasoning.\n\nAnswer: Cannot be determined.", "stop", True, "?"),   # a word, not a letter
    (THINK + "Reasoning.\n\nAnswer: Indeterminate.", "stop", True, "?"),
    (THINK + "Reasoning.\n\nAnswer: A trick question", "stop", True, "?"),
    (THINK + "Reasoning.\n\nAnswer: C or E", "stop", True, "?"),
    (THINK + "Answer: C\n\nOn reflection the question is flawed.", "stop", True, "?"),  # the last line is not the answer line
    ("thinking ...\nAnswer: C\nBut wait, let me check again", "length", False, "?"),     # never finished: a draft is not an answer
    (THINK + "Reasoning.\n\nAnswer: C", "length", True, "?"),                       # reply cut off at the cap
    ("Reasoning without a think tag.\n\nAnswer: A", "stop", True, "A"),             # the no-think condition
    (THINK + "", "stop", True, "?"),
])
def test_strict_score(text, finish, closed, answer):
    sc = S5.strict_score(text, finish, closed)
    assert sc["answer"] == answer
    assert sc["letters"] == ([] if answer == "?" else [answer])


def _record(i, prefix, condition, arm, block, text, finish, closed, letters):
    return {"id": f"{prefix}_{i:03d}", "prefix_id": prefix, "trace_arm": arm, "block": block, "condition": condition, "seq": i,
            "letters": letters, "answer": letters[0] if len(letters) == 1 else "?", "think_closed": closed, "finish": finish,
            "cont_text": text, "prompt": "PROMPT"}


def test_rescore_run_writes_derived_files(tmp_path):
    run = tmp_path / "run"
    run.mkdir()
    recs = [_record(0, "rb_c004_B00", "cut", "c004", 0, THINK + "x\n\nAnswer: (C)", "stop", True, []),          # ? -> C
            _record(1, "rb_c004_B00", "cut", "c004", 0, "draft\nAnswer: Cannot be determined", "length", False, ["C"]),  # C -> ?
            _record(2, "rb_c004_B00", "cut", "c004", 0, THINK + "x\n\nAnswer: E", "stop", True, ["E"])]          # unchanged
    (run / "continuations.jsonl").write_text("".join(json.dumps(r) + "\n" for r in recs), encoding="utf-8")
    fields = ["trace_id", "m", "condition", "prefix_id", "n"] + [f"count_{L}" for L in "ABCDEF"] + ["count_other", "count_unresolved", "p_hat", "ci_low", "ci_high", "stopped"]
    row = {"trace_id": "c004", "m": "0", "condition": "cut", "prefix_id": "rb_c004_B00", "n": "3", "count_A": 0, "count_B": 0, "count_C": 1, "count_D": 0,
           "count_E": 1, "count_F": 0, "count_other": 0, "count_unresolved": 1, "p_hat": 0.3333, "ci_low": 0.0, "ci_high": 1.0, "stopped": False}
    with open(run / "pcut.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerow(row)
    before = (run / "continuations.jsonl").read_bytes(), (run / "pcut.csv").read_bytes()
    out = tmp_path / "run_strict"
    summary = S5.rescore_run(run, out, log=lambda *_: None)
    assert ((run / "continuations.jsonl").read_bytes(), (run / "pcut.csv").read_bytes()) == before   # the registered run is untouched
    assert summary["records"] == 3 and summary["changed"] == 2
    derived = [json.loads(l) for l in open(out / "continuations.jsonl", encoding="utf-8")]
    assert [d["answer"] for d in derived] == ["C", "?", "E"] and [d["answer_v1"] for d in derived] == ["?", "C", "E"]
    assert all("cont_text" not in d and "prompt" not in d and len(d["cont_text_sha256"]) == 64 for d in derived)
    new = list(csv.DictReader(open(out / "pcut.csv", encoding="utf-8")))[0]
    assert (new["count_C"], new["count_E"], new["count_unresolved"], new["count_other"]) == ("1", "1", "1", "0")
    changes = list(csv.DictReader(open(out / "rescore_changes.csv", encoding="utf-8")))
    assert {c["id"] for c in changes} == {"rb_c004_B00_000", "rb_c004_B00_001"}
    with pytest.raises(SystemExit):
        S5.rescore_run(run, run, log=lambda *_: None)          # never write into the registered run folder


@pytest.mark.skipif(not (RUN / "continuations.jsonl").exists(), reason="stage-one run not present")
def test_stage_one_run_matches_the_independent_checks(tmp_path):
    """The numbers of Kian's own check and of the two other derivations (2026-09-19)."""
    summary = S5.rescore_run(RUN, tmp_path / "strict", log=lambda *_: None)
    assert summary["records"] == 625 and summary["changed"] == 36
    assert summary["finished"] == 534 and summary["finished_without_answer"] == 0 and summary["unfinished"] == 91
    assert summary["first_all_target_cut"] == {"registered": {"c004": 11, "e036": 7}, "strict": {"c004": 9, "e036": 7}}
    c = [summary["per_cut"][f"rb_c004_B{m:02d}"]["strict"]["C"] for m in range(12)]
    assert c == [12, 7, 13, 6, 4, 6, 15, 10, 10, 25, 25, 25]
    e = [summary["per_cut"][f"rb_e036_B{m:02d}"]["strict"]["E"] for m in range(8)]
    assert e == [24, 20, 14, 20, 24, 19, 24, 25]
    assert summary["per_cut"]["rb_cut0"]["strict"] == {"A": 0, "B": 0, "C": 3, "D": 0, "E": 18, "F": 0, "?": 4}
    assert summary["per_cut"]["rb_nothink"]["strict"] == summary["per_cut"]["rb_nothink"]["registered"]
    for m in range(8):                                                  # the E-trace does not change
        assert summary["per_cut"][f"rb_e036_B{m:02d}"]["strict"] == summary["per_cut"][f"rb_e036_B{m:02d}"]["registered"]
