"""Module test of scripts/s6_order.py: the three kinds, the first appearance across prefix and
continuation, the pattern, and the pooled tables.  When the stage-one run and its judge folder are
present, the registered numbers must reproduce results v1, Section 8, which was computed ad hoc.
Run: python -m pytest -q scripts/tests/test_s6_order.py"""
import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import s6_order as S6  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
RUN = REPO / "runs" / "experiments" / "resample_blocks_2026-09-17_1759"
JUDGE = RUN / "judge_2026-09-17_2229"


@pytest.mark.parametrize("path,kind", [
    (["Reasoning", "calculation", "algebra"], "algebra"),
    (["Reasoning", "logical reasoning", "algebra"], "algebra"),
    (["Reasoning", "defining symbols", "algebra"], "algebra"),
    (["Assumption", "branching (case split)", "algebra"], "algebra"),
    (["Example", "non-exhaustive listing", "algebra"], "algebra"),
    (["Knowledge", "world knowledge", "famous problem (CRT)"], "famous"),
    (["Reasoning", "hedge word analysis"], "hedge"),
    (["Reasoning", "hedge word analysis", "everyday reading"], "hedge"),
    (["Reasoning", "hedge word analysis", "mathematical reading"], "hedge"),
    (["Knowledge", "world knowledge"], None),
    (["Planning", "global plan"], None),
    (["Reasoning", "comparison", "option vs option"], None),
    ([], None),
])
def test_kind_of(path, kind):
    assert S6.kind_of(path) == kind


def test_combined_sentence_carries_both_labels():
    labels = [{"L1": "Planning", "L2": "initiate verification", "L3": "Wait (doubt marker)"},
              {"L1": "Knowledge", "L2": "world knowledge", "L3": "famous problem (CRT)"}]
    assert S6.kinds_of_sentence(labels) == {"famous"}
    both = [{"L1": "Reasoning", "L2": "calculation", "L3": "algebra"},
            {"L1": "Knowledge", "L2": "world knowledge", "L3": "famous problem (CRT)"}]
    assert S6.kinds_of_sentence(both) == {"algebra", "famous"}


def test_first_indices_and_pattern():
    prefix = {0: set(), 1: {"algebra"}, 2: set(), 5: {"famous"}}       # sentence 5 is beyond the cut
    cont = {0: set(), 1: {"famous"}, 4: {"hedge"}}
    first = S6.first_indices(prefix, 3, cont)                          # the prefix ends after sentence 2
    assert first == {"algebra": 1, "famous": 4, "hedge": 7}            # continuation index s -> 3 + s
    assert S6.pattern_of(first) == "algebra --> famous problem --> hedge word"
    assert S6.pattern_of({"algebra": None, "famous": 2, "hedge": None}) == "famous problem"
    assert S6.pattern_of({"algebra": None, "famous": None, "hedge": None}) == "(none)"


def test_prefix_beats_continuation():
    """A kind already in the prefix is placed there, however early it recurs in the continuation."""
    first = S6.first_indices({0: {"famous"}}, 1, {0: {"famous"}, 1: {"algebra"}})
    assert first["famous"] == 0 and first["algebra"] == 2
    assert S6.pattern_of(first) == "famous problem --> algebra"


def test_pooled_and_pairs_on_synthetic_rows():
    rows = [{"id": "a", "cut": "C-B00", "trace_arm": "c004", "condition": "cut", "answer": "C",
             "first_algebra": 1, "first_famous": 5, "first_hedge": "", "pattern": "algebra --> famous problem"},
            {"id": "b", "cut": "C-B00", "trace_arm": "c004", "condition": "cut", "answer": "?",
             "first_algebra": 1, "first_famous": 5, "first_hedge": "", "pattern": "algebra --> famous problem"},
            {"id": "c", "cut": "E-B00", "trace_arm": "e036", "condition": "cut", "answer": "E",
             "first_algebra": 9, "first_famous": 2, "first_hedge": "", "pattern": "famous problem --> algebra"}]
    pooled = {r["pattern"]: r for r in S6.pooled_rows(rows)}
    assert pooled["algebra --> famous problem"]["n"] == 2                      # the "?" stays in the denominator
    assert pooled["algebra --> famous problem"]["count_C"] == 1 and pooled["algebra --> famous problem"]["p_C"] == 0.5
    assert pooled["algebra --> famous problem"]["from_c004"] == 2
    pair = next(r for r in S6.pair_rows(rows) if r["scope"] == "all" and r["first"] == "algebra" and r["then"] == "famous problem")
    assert pair["XY_n"] == 2 and pair["YX_n"] == 1 and pair["YX_p_E"] == 1.0


@pytest.mark.skipif(not (JUDGE.exists() and (RUN / "continuations.jsonl").exists()), reason="stage-one run not present")
def test_section_8_of_results_v1_is_reproduced(tmp_path):
    """results v1, Section 8.2 and 8.4, under the reading the run recorded."""
    res = S6.run_one(RUN, JUDGE, tmp_path / "registered", "registered", log=lambda *_: None)
    assert res["labeled"] == 523                                              # 525 continuations, 2 unlabeled
    pair = next(r for r in res["pairs"] if r["scope"] == "all" and r["first"] == "algebra" and r["then"] == "famous problem")
    assert (pair["XY_n"], round(pair["XY_p_C"], 2), round(pair["XY_p_E"], 2)) == (293, 0.58, 0.19)
    assert (pair["YX_n"], round(pair["YX_p_C"], 2), round(pair["YX_p_E"], 2)) == (225, 0.16, 0.81)
    assert pair["YX_from_e036"] == 197                                        # the pooling caveat of Section 8.2
    pooled = {r["pattern"]: r for r in res["pooled"]}
    top = pooled["algebra --> famous problem --> hedge word"]
    assert (top["n"], round(top["p_C"], 2), round(top["p_E"], 2), top["from_c004"]) == (248, 0.63, 0.15, 246)
    cut0 = next(r for r in res["pairs"] if r["scope"] == "cut-0" and r["first"] == "algebra" and r["then"] == "famous problem")
    assert (cut0["XY_n"], cut0["YX_n"], cut0["YX_count_E"]) == (4, 19, 16)    # Section 8.2, the honest test


@pytest.mark.skipif(not (RUN / "continuations.jsonl").exists(), reason="stage-one run not present")
def test_strict_reading_changes_only_the_C_side(tmp_path):
    """The strict reading turns unfinished continuations into "?"; they sit on the C side of the pair."""
    res = S6.run_one(RUN, JUDGE, tmp_path / "strict", "strict", log=lambda *_: None)
    pair = next(r for r in res["pairs"] if r["scope"] == "all" and r["first"] == "algebra" and r["then"] == "famous problem")
    assert (pair["XY_n"], pair["YX_n"]) == (293, 225)                         # the patterns do not depend on the letters
    assert round(pair["XY_p_C"], 2) == 0.53 and pair["XY_count_unresolved"] == 83
    assert round(pair["YX_p_E"], 2) == 0.81 and pair["YX_count_unresolved"] == 7
    assert pair["diff_C"] > 0 and pair["diff_C_low"] > 0                      # the direction survives
    files = sorted(p.name for p in (tmp_path / "strict").glob("order_*"))
    assert files == ["order_by_cut.csv", "order_cut0.csv", "order_pairs.csv", "order_patterns.csv", "order_pooled.csv", "order_summary.md"]
    rows = list(csv.DictReader(open(tmp_path / "strict" / "order_patterns.csv", encoding="utf-8")))
    assert len(rows) == 523 and {r["pattern"] for r in rows} <= {
        "algebra --> famous problem", "famous problem --> algebra", "algebra --> famous problem --> hedge word",
        "famous problem --> algebra --> hedge word", "algebra --> hedge word --> famous problem", "algebra --> hedge word", "algebra"}
