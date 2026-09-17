"""Module test of scripts/scorer.py (pre-registration 3.7): the verbatim archived scorer must
recompute the archived per-prefix table exactly; the answer rule on synthetic replies.
Run: python -m pytest -q scripts/tests/test_scorer.py"""
import csv
import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import scorer as SC  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
ARCHIVED = REPO / "archive" / "decided-mid-thought" / "runs" / "resample_cuts_2026-08-25_1503.jsonl"
SUMMARY = REPO / "archive" / "decided-mid-thought" / "runs" / "resample_cuts_2026-08-25_1503_summary.csv"
ARCHIVED_SCRIPT = REPO / "archive" / "decided-mid-thought" / "scripts" / "sweep_2x2.py"


def test_extract_letters_is_verbatim():
    src = ARCHIVED_SCRIPT.read_text(encoding="utf-8")
    m = re.search(r"def extract_letters\(reply, valid\):\n(?:    .*\n){3}", src)
    assert m, "archived definition not found"
    ours = Path(SC.__file__).read_text(encoding="utf-8")
    body = m.group(0).replace("def extract_letters(reply, valid):\n", "")
    assert body in ours  # the three-line body, character for character


def test_archived_table_is_reproduced():
    records = [json.loads(l) for l in open(ARCHIVED, encoding="utf-8") if l.strip()]
    with open(SUMMARY, encoding="utf-8") as fh:
        expected = list(csv.DictReader(fh))
    rows = SC.archived_table(records, order=[r["prefix_id"] for r in expected])
    assert len(rows) == len(expected) == 20
    for got, exp in zip(rows, expected):
        assert got["prefix_id"] == exp["prefix_id"] and got["trace"] == exp["trace"] and str(got["cut"]) == exp["cut"]
        assert got["succeeded"] == int(exp["succeeded"]) == 25
        assert f"{got['p_C']}" == exp["p_C"] and f"{got['p_E']}" == exp["p_E"], (got, exp)
        assert got["distribution"] == exp["distribution"]


@pytest.mark.parametrize("text,answer,letters,closed", [
    ("thinking...</think>\nAnswer: C", "C", ["C"], True),
    ("thinking...</think>\nThe answer is (E).\nAnswer: E.", "E", ["E"], True),
    ("thinking...</think>\nAnswer: D, E", "?", ["D", "E"], True),
    ("thinking...</think>\nno letter here", "?", [], True),
    ("no tag, cap hit ... Answer: B", "B", ["B"], False),     # whole text scored when the tag is absent
    ("Answer: A in thinking</think>\nAnswer: F", "F", ["F"], True),  # only the reply after the tag
    ("answer: c", "C", ["C"], False),                          # case-insensitive
    ("Answer: Z", "?", [], False),                             # outside the valid set
])
def test_score(text, answer, letters, closed):
    s = SC.score(text)
    assert s["answer"] == answer and s["letters"] == letters and s["think_closed"] == closed
