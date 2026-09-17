"""Unit tests for scripts/derivation.py: the derivation gate on the reviewed labels of listing v4
under rule R4 (47/193 and 38/147), the pre-R4 regression on the archived listing v3 (46/193 and
37/146), the R4 label enforcement, and small synthetic cases.
Run: python -m pytest -q scripts/tests/test_derivation.py"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import derivation as D  # noqa: E402

GP, LP, IV, IB = "Planning > global plan", "Planning > local plan", "Planning > initiate verification", "Planning > initiate backtracking"
CA, LR = "Reasoning > calculation > algebra", "Reasoning > logical reasoning"
BR, FA, IC = "Assumption > branching (case split) > algebra", "Conclusion > final answer", "Conclusion > intermediate conclusion"
RS, RF, KW = "Restatement > rephrasing the prompt > question text", "Reflection > meta-evaluation of a step", "Knowledge > world knowledge"
IVW, IBW = IV + " > " + D.WAIT_LEAF, IB + " > " + D.WAIT_LEAF
R4_SENTENCES = {"c004": [42, 137, 254, 288, 340, 352], "e036": [19, 71, 100, 179]}  # scheme v6, Section 6b


@pytest.fixture(scope="module")
def listing():
    return D.parse_listing()


@pytest.fixture(scope="module")
def listing_v3():
    return D.parse_listing(D.LISTING_V3)


@pytest.fixture(scope="module")
def texts():
    return D.load_sentence_texts()


# ----------------------------------------------------------------------------
# The gate on the reviewed labels (listing v4, rule R4, texts from sentences_source.jsonl)
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("trace_id,n,blocks,nodes", [("c004", 375, 47, 193), ("e036", 254, 38, 147)])
def test_gate_reproduces_listing_v4_under_r4(listing, texts, trace_id, n, blocks, nodes):
    exp = listing[trace_id]
    assert len(exp["labels"]) == len(exp["names"]) == len(exp["texts"]) == len(texts[trace_id]) == n
    assert len(exp["blocks"]) == blocks
    g = D.gate(trace_id, exp["labels"], exp, texts[trace_id])
    assert g["blocks_derived"] == g["blocks_expected"] == blocks
    assert g["nodes_derived"] == g["nodes_expected"] == nodes
    assert g["block_diffs"] == [] and g["rule_diffs"] == [] and g["name_diffs"] == []
    assert g["r4_openers"] == R4_SENTENCES[trace_id]
    assert g["pass"] and g["r4"]


def test_r4_regex_hits_exactly_the_ten_scheme_sentences(texts):
    for tid, expected in R4_SENTENCES.items():
        assert [s for s, t in enumerate(texts[tid]) if D.is_r4(t)] == expected


def test_enforcement_changes_nothing_on_the_reviewed_labels(listing, texts):
    for tid, expected in R4_SENTENCES.items():
        new, notes = D.apply_r4_labels(listing[tid]["labels"], texts[tid])
        assert new == listing[tid]["labels"]
        assert [s for s, n in enumerate(notes) if n] == expected
        assert all(n["action"] == "set_level3" and not n["changed"] for n in notes if n)


def test_listing_v4_defect_is_recorded_not_fatal(listing):
    # listing v4, E s19: a fragment "|\| Reasoning > comparison > prompt vs original text" is left
    # after the node name (an editing leftover of the pre-R4 row); the parser tolerates it and
    # records it so that the document can be corrected.  The labels of the row are unaffected.
    assert listing["c004"]["defects"] == []
    assert [d["s"] for d in listing["e036"]["defects"]] == [19]
    assert listing["e036"]["labels"][19] == [IVW, "Reasoning > comparison > prompt vs original text"]


@pytest.mark.parametrize("trace_id,n,blocks,nodes", [("c004", 375, 46, 193), ("e036", 254, 37, 146)])
def test_pre_r4_derivation_reproduces_the_archived_listing_v3(listing_v3, trace_id, n, blocks, nodes):
    exp = listing_v3[trace_id]
    assert len(exp["labels"]) == n and len(exp["blocks"]) == blocks and exp["defects"] == []
    g = D.gate(trace_id, exp["labels"], exp, None, "reviewed_v3")
    assert g["blocks_derived"] == blocks and g["nodes_derived"] == nodes and g["pass"] and not g["r4"]


def test_listing_block_headers_are_contiguous(listing):
    for tid in ("c004", "e036"):
        b = listing[tid]["blocks"]
        assert b[0][1] == 0 and b[-1][2] == len(listing[tid]["labels"]) - 1
        assert all(b[k][2] + 1 == b[k + 1][1] for k in range(len(b) - 1))
        assert [x[0] for x in b] == list(range(len(b)))
        assert {x[3] for x in b} <= {"R1", "R2", "R3", "R4"}


# ----------------------------------------------------------------------------
# Rule R4 on synthetic cases
# ----------------------------------------------------------------------------

def names(labels, texts=None):
    return D.derive(labels, "t", "test", texts)["sentence_names"]


def blocks(labels, texts=None):
    return [(b["s_start"], b["s_end"], b["opener_rule"]) for b in D.derive(labels, "t", "test", texts)["blocks"]]


@pytest.mark.parametrize("text,hit", [
    ("Wait, is that right?", True), ("But wait, the classic says $1.00 more.", True), ("⏎⏎    **Wait, hold on.**", True),
    ("(Wait, the classic problem says …", True), ("Oh wait.", True), ("Oh, wait — no.", True), ("Okay, wait.", True), ("And wait, what?", True),
    ("1. Wait a moment.", True), ("- wait, no", True), ("> WAIT", True), ("   ⏎ * *Wait*", True), ("_Wait, no.", True),
    ("Actually, wait.", False), ("Waiting for the sum.", False), ("await the result", False), ("Let me wait.", False),
    ("_Wait_", False),  # a trailing underscore is a word character: the specified regex does not match an underscore-italic "Wait"
    ("Hmm, wait.", False), ("", False), ("But", False), ("Wait", True), ("wait.", True),
])
def test_r4_regex(text, hit):
    assert D.is_r4(text) is hit


def test_r4_opener_opens_whatever_its_labels_and_ends_the_node_before_it():
    labels = [[GP], [CA], [CA], [CA]]
    texts = ["Plan.", "x = 1.", "Wait, x = 2.", "so x = 2."]
    assert blocks(labels) == [(0, 3, "R1")]
    assert blocks(labels, texts) == [(0, 1, "R1"), (2, 3, "R4")]
    assert names(labels, texts) == ["Pl₀", "Re₀", "Re₁(2)", "Re₁(2)"]  # the Reasoning node is cut at the block boundary


def test_r4_takes_precedence_over_r1_in_the_recorded_rule():
    labels = [[GP], [CA], [IVW], [CA]]
    texts = ["Plan.", "x = 1.", "Wait, let me check.", "x = 1 indeed."]
    assert blocks(labels, texts) == [(0, 1, "R1"), (2, 3, "R4")]
    assert blocks(labels) == [(0, 1, "R1"), (2, 3, "R1")]


def test_r4_inside_a_planning_run_does_not_change_the_run_opener():
    # the run s1..s3 opens at s1 by R1 as before; the R4 sentence adds an opener at s2 (E s179 case)
    labels = [[CA], [GP], [IBW], [LP], [CA]]
    texts = ["x = 1.", "Now the reply.", "Wait, reconsider.", "- step:", "x = 2."]
    assert blocks(labels, texts) == [(0, 0, "S0"), (1, 1, "R1"), (2, 4, "R4")]


def test_r4_on_sentence_zero():
    assert blocks([[CA], [CA]], ["Wait, what?", "x = 1."]) == [(0, 1, "R4")]


def test_r4_texts_length_must_match():
    with pytest.raises(ValueError):
        D.derive([[GP], [CA]], "t", "test", ["only one"])
    with pytest.raises(ValueError):
        D.apply_r4_labels([[GP], [CA]], ["only one"])


def test_enforcement_sets_level3_on_a_verification_or_backtracking_path():
    texts = ["Wait, check.", "Wait, no.", "x = 1."]
    new, notes = D.apply_r4_labels([[IV], [IB], [CA]], texts)
    assert new == [[IVW], [IBW], [CA]]
    assert [n and n["action"] for n in notes] == ["set_level3", "set_level3", None]
    assert notes[0]["changed"] and notes[0]["before"] == [IV] and notes[2] is None
    new, notes = D.apply_r4_labels([[IVW]], ["Wait."])  # already carrying the leaf: unchanged
    assert new == [[IVW]] and notes[0]["action"] == "set_level3" and not notes[0]["changed"]
    new, notes = D.apply_r4_labels([[KW, IV]], ["But wait, the classic says more."])  # the R4 path goes first
    assert new == [[IVW, KW]] and notes[0]["changed"]


def test_enforcement_prepends_the_r4_path_to_a_content_sentence():
    new, notes = D.apply_r4_labels([[KW]], ["But wait, the classic says $1.00 more."])
    assert new == [[D.R4_PATH, KW]] and notes[0]["action"] == "prepended" and notes[0]["changed"]
    rec = D.derive(new, "t", "test", ["But wait, the classic says $1.00 more."])
    assert rec["sentence_names"] == ["[Pl+Kn]₀"] and rec["blocks"][0]["opener_rule"] == "R4"
    assert rec["blocks"][0]["opener_label"] == D.R4_PATH + " || " + KW


def test_enforcement_replaces_a_planning_path_of_another_leaf():
    new, notes = D.apply_r4_labels([[GP]], ["Wait, let me re-check."])
    assert new == [[D.R4_PATH]] and notes[0]["action"] == "planning_leaf_replaced"
    new, notes = D.apply_r4_labels([[RS, LP]], ["Wait, the prompt says 9:00."])
    assert new == [[D.R4_PATH, RS]] and notes[0]["action"] == "planning_leaf_replaced"


def test_enforcement_keeps_the_two_path_cap():
    new, notes = D.apply_r4_labels([[CA, KW]], ["Wait, 1 + 1 = 2 by the usual rule."])
    assert new == [[D.R4_PATH, CA]] and notes[0]["action"] == "prepended_second_dropped"
    D.derive(new, "t", "test", ["Wait, 1 + 1 = 2 by the usual rule."])  # valid input


def test_node_level1_of_a_combined_node():
    rec = D.derive([[D.R4_PATH, KW], [CA]], "t", "test", ["Wait, the classic.", "x = 1."])
    assert [D.node_level1(n) for n in rec["nodes"]] == ["Planning", "Reasoning"]


# ----------------------------------------------------------------------------
# Synthetic cases without texts (the pre-R4 rules, unchanged)
# ----------------------------------------------------------------------------

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
    assert rec["blocks"][0]["tokens"] is None and rec["r4"] is False


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
