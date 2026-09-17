"""Unit tests for scripts/structural_agreement.py on a synthetic pair of label lists with
hand-computed answers.  Run: python -m pytest -q scripts/tests/test_structural_agreement.py"""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import structural_agreement as SA  # noqa: E402

GP, LP, IV = "Planning > global plan", "Planning > local plan", "Planning > initiate verification"
CA, CA2, LR = "Reasoning > calculation > algebra", "Reasoning > calculation", "Reasoning > logical reasoning"
IC, FA, BR, RF = "Conclusion > intermediate conclusion", "Conclusion > final answer", "Assumption > branching (case split) > algebra", "Reflection > meta-evaluation of a step"

# reviewed: blocks [0-3] R1, [4-6] R1, [7-8] R2, [9] R3; nodes Pl0 Re(1-2) Co3 | Pl4 Re5 Rf6 | As7 Re8 | Co9
REVIEWED = [[GP], [CA], [CA], [IC], [IV], [CA], [RF], [BR], [CA], [FA]]
# judge: s2, s3 -> logical reasoning; s4 -> calculation (no Planning opener at 4); s8 -> calculation without Level 3
JUDGE = [[GP], [CA], [LR], [LR], [CA], [CA], [RF], [BR], [CA2], [FA]]


@pytest.fixture(scope="module")
def m():
    return SA.trace_metrics("t", REVIEWED, JUDGE)


def test_block_metrics(m):
    b = m["blocks"]
    assert (b["n_reviewed"], b["n_judge"], b["hits"], b["misses"], b["extras"], b["near_misses"]) == (4, 3, 3, 1, 0, 0)
    assert b["precision"] == pytest.approx(1.0) and b["recall"] == pytest.approx(0.75) and b["f1"] == pytest.approx(2 * 0.75 / 1.75)
    assert b["rule_agree"] == 3 and b["misses_idx"] == [4] and b["extras_idx"] == []


def test_near_miss_and_extra():
    rev = [[GP], [CA], [IV], [CA], [CA]]        # openers 0, 2
    jud = [[GP], [CA], [CA], [IV], [CA]]        # openers 0, 3
    b = SA.trace_metrics("t", rev, jud)["blocks"]
    assert (b["hits"], b["misses"], b["near_misses"], b["extras"]) == (1, 1, 1, 1)


def test_next_node_metrics(m):
    nn = m["next_node"]
    assert (nn["n_cuts"], nn["agree"]) == (3, 2) and nn["rate"] == pytest.approx(2 / 3)
    assert nn["confusions"] == [(("Planning", "Reasoning"), 1)]


def test_node_metrics(m):
    nd = m["nodes"]
    assert (nd["n_reviewed"], nd["n_judge"], nd["end_hits"], nd["end_misses"], nd["end_extras"]) == (9, 6, 6, 3, 0)
    assert nd["precision"] == pytest.approx(1.0) and nd["recall"] == pytest.approx(6 / 9) and nd["f1"] == pytest.approx(0.8)
    assert nd["matched_l1_agree"] == 7 and nd["matched_l1_rate"] == pytest.approx(7 / 9)
    assert nd["split"] == 0 and nd["merged"] == 4


def test_split_detection():
    rev = [[GP], [CA], [CA], [CA], [FA]]        # one Reasoning node 1-3
    jud = [[GP], [CA], [IC], [CA], [FA]]        # the judge cuts it into Re, Co, Re
    nd = SA.trace_metrics("t", rev, jud)["nodes"]
    assert nd["split"] == 1


def test_sentence_decomposition(m):
    s = m["sentences"]
    assert (s["l1_wrong"], s["l2_wrong"], s["l3_wrong"], s["all_right"], s["n"]) == (2, 1, 1, 6, 10)
    assert s["all_right_share"] == pytest.approx(0.6) and s["l1_share_of_disagreements"] == pytest.approx(0.5)


def test_pooled_and_csv(tmp_path):
    res = SA.compute({"a": JUDGE, "b": JUDGE}, {"a": REVIEWED, "b": REVIEWED})
    p = res["pooled"]
    assert p["blocks"]["hits"] == 6 and p["blocks"]["recall"] == pytest.approx(0.75)
    assert p["next_node"]["agree"] == 4 and p["next_node"]["n_cuts"] == 6
    assert p["nodes"]["end_hits"] == 12 and p["nodes"]["f1"] == pytest.approx(0.8) and p["nodes"]["merged"] == 8
    assert p["sentences"]["n"] == 20 and p["sentences"]["l1_wrong"] == 4
    SA.write_csv(tmp_path / "s.csv", res)
    text = (tmp_path / "s.csv").read_text(encoding="utf-8")
    assert text.startswith("scope,group,metric,value") and "pooled,nodes,f1,0.8000" in text
    md = SA.markdown(res, "test")
    assert "| pooled |" in md and "Planning → Reasoning 2" in md


def test_length_mismatch():
    with pytest.raises(ValueError):
        SA.trace_metrics("t", REVIEWED, JUDGE[:-1])


def test_judge_labels_from_file(tmp_path):
    p = tmp_path / "labels.jsonl"
    p.write_text('{"trace_id": "a", "s": 0, "labels": [{"L1": "Planning", "L2": "global plan", "L3": null}]}\n'
                 '{"trace_id": "a", "s": 1, "labels": [{"L1": "Reasoning", "L2": "calculation", "L3": "algebra"}, {"L1": "Assumption", "L2": "branching (case split)", "L3": null}]}\n', encoding="utf-8")
    assert SA.judge_labels_from_file(p) == {"a": [[GP], [CA, "Assumption > branching (case split)"]]}
