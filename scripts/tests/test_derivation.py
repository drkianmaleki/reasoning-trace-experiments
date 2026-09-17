"""Unit tests for scripts/derivation.py: the derivation gate on the reviewed labels of listing v3
and small synthetic cases.  Run: python -m pytest -q scripts/tests/test_derivation.py"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import derivation as D  # noqa: E402

GP, LP, IV = "Planning > global plan", "Planning > local plan", "Planning > initiate verification"
CA, LR = "Reasoning > calculation > algebra", "Reasoning > logical reasoning"
BR, FA, IC = "Assumption > branching (case split) > algebra", "Conclusion > final answer", "Conclusion > intermediate conclusion"
RS, RF = "Restatement > rephrasing the prompt > question text", "Reflection > meta-evaluation of a step"


@pytest.fixture(scope="module")
def listing():
    return D.parse_listing()


# ----------------------------------------------------------------------------
# The gate on the reviewed labels
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("trace_id,n,blocks,nodes", [("c004", 375, 46, 193), ("e036", 254, 37, 146)])
def test_gate_reproduces_the_listing(listing, trace_id, n, blocks, nodes):
    exp = listing[trace_id]
    assert len(exp["labels"]) == len(exp["names"]) == len(exp["texts"]) == n
    assert len(exp["blocks"]) == blocks
    g = D.gate(trace_id, exp["labels"], exp)
    assert g["blocks_derived"] == g["blocks_expected"] == blocks
    assert g["nodes_derived"] == g["nodes_expected"] == nodes
    assert g["block_diffs"] == [] and g["rule_diffs"] == [] and g["name_diffs"] == []
    assert g["pass"]


def test_listing_block_headers_are_contiguous(listing):
    for tid in ("c004", "e036"):
        b = listing[tid]["blocks"]
        assert b[0][1] == 0 and b[-1][2] == len(listing[tid]["labels"]) - 1
        assert all(b[k][2] + 1 == b[k + 1][1] for k in range(len(b) - 1))
        assert [x[0] for x in b] == list(range(len(b)))


# ----------------------------------------------------------------------------
# Synthetic cases
# ----------------------------------------------------------------------------

def names(labels):
    return D.derive(labels, "t", "test")["sentence_names"]


def blocks(labels):
    return [(b["s_start"], b["s_end"], b["opener_rule"]) for b in D.derive(labels, "t", "test")["blocks"]]


def test_local_plan_only_run_opens_nothing():
    labels = [[GP], [CA], [LP], [LP], [CA], [IC]]
    assert blocks(labels) == [(0, 5, "R1")]


def test_planning_run_with_one_nonlocal_plan_opens_at_its_first_sentence():
    labels = [[GP], [CA], [LP], [IV], [CA]]
    assert blocks(labels) == [(0, 1, "R1"), (2, 4, "R1")]


def test_two_consecutive_branching_sentences_open_one_block():
    labels = [[GP], [CA], [BR], [BR], [CA], [BR], [CA]]
    assert blocks(labels) == [(0, 1, "R1"), (2, 4, "R2"), (5, 6, "R2")]


def test_final_answer_opens_and_a_run_of_them_opens_once():
    labels = [[GP], [CA], [FA], [FA]]
    assert blocks(labels) == [(0, 1, "R1"), (2, 3, "R3")]


def test_combined_sentence_with_a_global_plan_half_opens_a_block():
    labels = [[GP], [CA], [GP, RS], [CA], [LP, RS], [CA]]
    assert blocks(labels) == [(0, 1, "R1"), (2, 5, "R1")]  # [LP, RS] does not open


def test_combined_sentence_breaks_a_planning_run():
    labels = [[GP], [LP, RS], [LP], [LP], [CA]]  # the run after the combined sentence is local plans only
    assert blocks(labels) == [(0, 4, "R1")]
    labels = [[GP], [LP, RS], [IV], [CA]]
    assert blocks(labels) == [(0, 1, "R1"), (2, 3, "R1")]


def test_combined_branching_and_final_halves_open():
    assert blocks([[GP], [CA], [CA, BR], [CA]]) == [(0, 1, "R1"), (2, 3, "R2")]
    assert blocks([[GP], [CA], [RF, FA]]) == [(0, 1, "R1"), (2, 2, "R3")]


def test_sentence_zero_always_opens():
    assert blocks([[RS], [CA]]) == [(0, 1, "S0")]
    assert blocks([[BR], [CA]]) == [(0, 1, "R2")]


def test_node_naming_without_and_with_superscripts():
    labels = [[GP], [GP], [GP], [RS], [RS], [RS], [RS], [RS]]
    assert names(labels) == ["Pl₀(3)"] * 3 + ["Rs₀(5)"] * 5
    labels = [[GP], [CA], [CA], [LP], [CA], [RF]]  # two Pl and two Re nodes in block 0
    assert names(labels) == ["Pl₀¹", "Re₀¹(2)", "Re₀¹(2)", "Pl₀²", "Re₀²", "Rf₀"]
    rec = D.derive(labels, "t", "test")
    assert [n["name_plain"] for n in rec["nodes"]] == ["Pl_0^1", "Re_0^1(2)", "Pl_0^2", "Re_0^2", "Rf_0"]


def test_combined_node_naming_and_block_subscripts():
    labels = [[GP], [CA], [CA, "Assumption > assuming a missing premise by common practice"], [CA], [IV], [CA]]
    rec = D.derive(labels, "t", "test")
    assert rec["sentence_names"] == ["Pl₀", "Re₀¹", "[Re+As]₀", "Re₀²", "Pl₁", "Re₁"]
    assert rec["nodes"][2] == {"name": "[Re+As]₀", "name_plain": "[Re+As]_0", "L1": "Reasoning + Assumption",
                               "s_start": 2, "s_end": 2, "n": 1, "block": 0}
    assert rec["blocks"][1]["opener_label"] == IV and rec["blocks"][1]["opener_rule"] == "R1"
    assert rec["blocks"][0]["tokens"] is None


def test_block_boundary_ends_a_node():
    labels = [[GP], [CA], [IV], [CA]]  # Reasoning at s1 and s3 are separate nodes in different blocks
    assert names(labels) == ["Pl₀", "Re₀", "Pl₁", "Re₁"]


def test_derive_rejects_bad_input():
    with pytest.raises(ValueError):
        D.derive([[]], "t", "test")
    with pytest.raises(ValueError):
        D.derive([["Nonsense > x"]], "t", "test")


def test_name_normalization():
    assert D.normalize_listing_name("Rs₁(1)") == "Rs₁"
    assert D.normalize_listing_name("Re₃(7)") == "Re₃(7)"
    assert D.node_name("Pl", 12, 3, 4) == ("Pl₁₂³(4)", "Pl_12^3(4)")
