"""Unit tests for scripts/s0_split.py (pipeline step 2/9, the sentence splitter).

Run:  python -m pytest -q scripts/tests/test_s0_split.py
Offline: the only files read are the archived raw traces (read only).
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import s0_split as S  # noqa: E402

NL = S.NEWLINE_MARK


def texts(text):
    return [S.sentence_text(text, a, b) for a, b in S.split_offsets(text)]


def base_texts(text):
    return [S.sentence_text(text, a, b) for a, b in S.base_offsets(text)]


# ----------------------------------------------------------------------------
# Rule (a): a comma closing a segment with a relation symbol acts as a period
# ----------------------------------------------------------------------------

def test_rule_a_example_from_section_0c():
    t = "If Ball = $0.05, then Bat = 1.10 - 0.05 = $1.05."
    assert texts(t) == ["If Ball = $0.05,", "then Bat = 1.10 - 0.05 = $1.05."]
    assert base_texts(t) == [t]


def test_rule_a_comma_inside_parentheses_never_splits():
    t = "Let f(x, y) = 2, then."
    assert texts(t) == ["Let f(x, y) = 2,", "then."]
    # the comma inside the parentheses follows a relation symbol in its own segment and still
    # does not split (this is the case the depth guard exists for)
    assert texts("Let f(x = 1, y) = 2, then.") == ["Let f(x = 1, y) = 2,", "then."]
    assert texts("(a = b, c) = d, e") == ["(a = b, c) = d,", "e"]


def test_rule_a_stray_closing_parenthesis_keeps_depth_at_zero():
    assert texts("a = b) c = d, e") == ["a = b) c = d,", "e"]


def test_rule_a_segment_reset_at_sentence_start():
    assert texts("x = 5. However, this is fine.") == ["x = 5.", "However, this is fine."]
    assert texts("x = 5\nHowever, this is fine.") == ["x = 5", NL + "However, this is fine."]


def test_rule_a_segment_without_relation_does_not_split():
    t = "In the classic version, the ball costs 0.05, and that is that."
    assert texts(t) == [t]


def test_rule_a_segment_reset_by_delimiters():
    # the relation symbol is in the segment before the `;`, not in the one the comma closes
    t = "x = 5; however, this is fine."
    assert texts(t) == [t]
    # the relation symbol is inside parentheses; the segment after `)` has none
    t = "If (x = 2), then stop."
    assert texts(t) == [t]


def test_rule_a_comma_must_be_followed_by_whitespace_like_a_period():
    t = "So x = 1,000 here, fine."
    assert texts(t) == [t]
    # ... but a comma at the very end of the text counts (end of text is allowed)
    assert texts("x = 1,") == ["x = 1,"]


def test_rule_a_unicode_relation_symbols():
    assert texts("Since x ≤ 3, stop.") == ["Since x ≤ 3,", "stop."]
    assert texts("Since x ≥ 3, stop.") == ["Since x ≥ 3,", "stop."]
    assert texts("Since x ≠ 3, stop.") == ["Since x ≠ 3,", "stop."]


# ----------------------------------------------------------------------------
# Arrow exclusion
# ----------------------------------------------------------------------------

def test_arrow_exclusion():
    assert texts("Ball -> Bat, then done.") == ["Ball -> Bat, then done."]
    assert texts("If x >= 3, stop.") == ["If x >= 3, stop."]
    assert texts("If x > 3, stop.") == ["If x > 3,", "stop."]
    assert texts("If x <= 3, stop.") == ["If x <= 3, stop."]
    assert texts("If x < 3, stop.") == ["If x < 3,", "stop."]
    assert texts("A => B, so C.") == ["A => B, so C."]
    assert texts("A = B, so C.") == ["A = B,", "so C."]


def test_is_relation_symbol_characterwise():
    t = "a -> b => c >= d <= e = f < g > h"
    rel = [t[i] for i in range(len(t)) if S.is_relation_symbol(t, i)]
    assert rel == ["=", "<", ">"]


# ----------------------------------------------------------------------------
# Rule (b): an opening parenthesis after a relation segment, capitalized clause
# ----------------------------------------------------------------------------

def test_rule_b_capitalized_clause_starts_a_sentence():
    t = "Ball = $x$, Bat = $x + 1.00$ (Wait, this is the standard riddle.)"
    assert texts(t) == ["Ball = $x$,", "Bat = $x + 1.00$", "(Wait, this is the standard riddle.)"]
    assert base_texts(t) == [t]


def test_rule_b_lowercase_clause_stays_attached():
    t = "Bat = $x + 1.00$ (where $x$ is the ball)"
    assert texts(t) == [t]


def test_rule_b_single_word_clause():
    t = "$x + (1.10 - x) = 1.10$ (Identity)"
    assert texts(t) == ["$x + (1.10 - x) = 1.10$", "(Identity)"]


def test_rule_b_needs_a_relation_in_the_preceding_segment():
    assert texts("[Output] -> *Proceeds* (Note: done)") == ["[Output] -> *Proceeds* (Note:", "done)"]
    assert texts("Options (A) and (B) here.") == ["Options (A) and (B) here."]


def test_rule_b_boundary_before_the_whitespace_that_precedes_the_parenthesis():
    t = "x = 2 (Identity)"
    assert S.split_offsets(t) == [(0, 5), (5, 16)]
    assert t[5:16] == " (Identity)"
    assert texts("x = 2(Identity)") == ["x = 2", "(Identity)"]


def test_rule_b_prime_option_labels_are_operands():
    # Kian, 2026-09-16: an option label (A)..(Z) is an operand, not a clause
    assert texts("So (E) > (C).") == ["So (E) > (C)."]
    assert texts("Strict correctness = (E).") == ["Strict correctness = (E)."]
    # the segment "= (C)" keeps its relation symbol, so the comma after the label still splits
    assert texts("The answer = (C), so we stop.") == ["The answer = (C),", "so we stop."]
    # everything else about rule (b) is unchanged
    assert texts("Ball = $x$, Bat = $x + 1.00$ (Wait, this is the standard riddle.)") == \
        ["Ball = $x$,", "Bat = $x + 1.00$", "(Wait, this is the standard riddle.)"]
    assert texts("Bat = $x + 1.00$ (Wait, this is the riddle.)") == \
        ["Bat = $x + 1.00$", "(Wait, this is the riddle.)"]
    assert texts("x = 2 (Identity)") == ["x = 2", "(Identity)"]
    # only a single capital letter is a label: (Ab), (1), (AB) are ordinary parentheses
    assert texts("x = 2 (AB) fine, yes.") == ["x = 2", "(AB) fine, yes."]
    assert texts("x = 2 (1), yes.") == ["x = 2 (1), yes."]


def test_tag_angle_brackets_are_not_relation_symbols():
    # Kian, 2026-09-16: the < and > of a tag are not relation symbols
    assert texts("</think>\nAnswer: E") == ["</think>", NL + "Answer:", "E"]
    assert texts("</think>, then x = 1.") == ["</think>, then x = 1."]
    assert texts("See <think>, then stop.") == ["See <think>, then stop."]
    assert texts("<br>, x") == ["<br>, x"]
    assert texts("If x<y, stop.") == ["If x<y,", "stop."]
    assert texts("Bat > Ball, so yes.") == ["Bat > Ball,", "so yes."]
    t = "a </think> b < c"
    assert [i for i in range(len(t)) if S.is_relation_symbol(t, i)] == [t.index("< c")]
    assert S.tag_bracket_positions("x <think>y</think> <=") == frozenset({2, 8, 10, 17})


def test_rule_b_only_at_parenthesis_depth_zero():
    t = "So x = 2 (with y = 3 (Wait, no), ok), done."
    assert texts(t) == [t]


def test_rule_b_capitalized_means_uppercase_letter():
    for t in ("So x = 2 (1) fine, yes.", "So x = 2 ($y$) fine, yes.", "So x = 2 (*Wait*) fine, yes."):
        assert texts(t) == [t]


# ----------------------------------------------------------------------------
# Base rule and offsets
# ----------------------------------------------------------------------------

def test_base_rule_terminators_need_following_whitespace():
    t = 'He said "the ball." But no.'
    assert base_texts(t) == [t]
    assert base_texts("A. B? C! D: E") == ["A.", "B?", "C!", "D:", "E"]
    assert base_texts("Ratio 2:1 and 3.5 here") == ["Ratio 2:1 and 3.5 here"]


def test_base_rule_line_breaks():
    t = "answer:\n\n1.  **Analyze:**\n    *   x\n"
    assert S.split_offsets(t) == [(0, 7), (7, 11), (11, 25), (25, len(t))]
    assert [t[a:b] for a, b in S.split_offsets(t)] == ["answer:", "\n\n1.", "  **Analyze:**", "\n    *   x\n"]
    assert base_texts(t) == ["answer:", NL + NL + "1.", "**Analyze:**", NL + "    *   x"]


def test_line_break_preceded_by_a_space_is_not_a_boundary():
    # clarification 6: the confirmed listing keeps `ball." \n   Mathematically` in one sentence
    t = 'only states that "more than the ball." \n   Mathematically, we have two conditions: \n   1) Bat + Ball = $1.10\n   2) Bat > Ball\n'
    assert texts(t) == [
        'only states that "more than the ball." ' + NL + "   Mathematically, we have two conditions:",
        NL + "   1) Bat + Ball = $1.10",
        NL + "   2) Bat > Ball",
    ]


def test_blank_line_after_a_trailing_space_is_a_boundary():
    # a paragraph break always separates, even when the previous line ends with a space
    t = "First paragraph \n\nSecond, x = 1."
    assert texts(t) == ["First paragraph", NL + NL + "Second, x = 1."]
    assert texts("First \n   \nSecond") == ["First", NL + "   " + NL + "Second"]
    assert base_texts(t) == texts(t)


def test_crlf_line_endings():
    t = "Line one\r\nLine two.\r\nLine three"
    assert S.split_offsets(t) == [(0, 8), (8, 19), (19, len(t))]
    assert texts(t) == ["Line one", NL + "Line two.", NL + "Line three"]


def test_whitespace_between_sentences_belongs_to_the_following_sentence():
    t = "One.  Two.   \n  Three"
    spans = S.split_offsets(t)
    assert spans == [(0, 4), (4, 10), (10, len(t))]
    assert [t[a:b] for a, b in spans] == ["One.", "  Two.", "   \n  Three"]


def test_sentence_text_display_form():
    t = "  \n\t Hello\n  world.  \n"
    assert S.sentence_text(t, 0, len(t)) == NL + "\t Hello" + NL + "  world."
    # only spaces and tabs are stripped on the left; newlines are kept and shown
    assert S.sentence_text("\n  x", 0, 4) == NL + "  x"
    # the trailing whitespace of the text (only the last span can carry it) is dropped
    assert texts("Done.\n")[-1] == "Done."


def test_empty_and_whitespace_only_text():
    assert S.split_offsets("") == []
    assert S.base_offsets("") == []
    assert S.split_offsets("  \n ") == [(0, 4)]


def test_old_index_and_part():
    t = "If Ball = $0.05, then Bat = $1.05. Fine.\nBall = $x$, Bat = $x + 1.00$ (Wait, no.)"
    assert S.old_index_and_part(t) == [(0, 1), (0, 2), (1, 1), (2, 1), (2, 2), (2, 3)]
    recs = S.split_records("t", t, with_old=True)
    assert [(r["old_s"], r["part"]) for r in recs] == [(0, 1), (0, 2), (1, 1), (2, 1), (2, 2), (2, 3)]
    assert list(recs[0]) == ["trace_id", "s", "old_s", "part", "char_start", "char_end", "text"]


def test_records_without_old_fields():
    recs = S.split_records("t", "A. B.")
    assert recs == [
        {"trace_id": "t", "s": 0, "char_start": 0, "char_end": 2, "text": "A."},
        {"trace_id": "t", "s": 1, "char_start": 2, "char_end": 5, "text": "B."},
    ]


# ----------------------------------------------------------------------------
# The two source traces
# ----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def sources():
    return S.load_source_traces()


def check_partition(text, spans):
    assert spans[0][0] == 0
    assert spans[-1][1] == len(text)
    for (a, b), (c, d) in zip(spans, spans[1:]):
        assert b == c
    for a, b in spans:
        assert a < b
        assert text[a:b].strip() != ""


@pytest.mark.parametrize("trace_id", ["c004", "e036"])
def test_partition_properties_on_source_traces(sources, trace_id):
    text = sources[trace_id]
    check_partition(text, S.split_offsets(text))
    check_partition(text, S.base_offsets(text))


def test_counts_on_source_traces(sources):
    assert len(sources["c004"]) == 18690 and len(sources["e036"]) == 11401
    assert len(S.split_offsets(sources["c004"])) == 375
    assert len(S.split_offsets(sources["e036"])) == 254
    assert len(S.base_offsets(sources["c004"])) == 366
    assert len(S.base_offsets(sources["e036"])) == 247


@pytest.mark.parametrize("trace_id", ["c004", "e036"])
def test_every_base_boundary_is_kept(sources, trace_id):
    text = sources[trace_id]
    base_ends = {b for _, b in S.base_offsets(text)}
    eq_ends = {b for _, b in S.split_offsets(text)}
    assert base_ends <= eq_ends


@pytest.mark.parametrize("trace_id", ["c004", "e036"])
def test_records_text_equals_display_form(sources, trace_id):
    text = sources[trace_id]
    for r in S.split_records(trace_id, text, with_old=True):
        assert r["text"] == S.sentence_text(text, r["char_start"], r["char_end"])
        assert r["part"] >= 1


def test_continuation_rule_splits_only_before_the_think_tag():
    # Kian, 2026-09-17: continuations are split up to the first </think>; the reply is not labeled
    t = "First thought. Second thought.\n</think>\n\nThe reply, which is not split. Answer: E"
    recs = S.split_records("c", t, continuation=True)
    assert [r["text"] for r in recs] == ["First thought.", "Second thought."]
    assert all(r["think_end"] == t.index("</think>") for r in recs) and recs[-1]["char_end"] == t.index("</think>")
    assert t[recs[-1]["char_start"]:recs[-1]["char_end"]] == " Second thought.\n"
    # without the tag (the cap was hit) the whole text is split and think_end is null
    recs = S.split_records("c", "First thought. Second thought.", continuation=True)
    assert len(recs) == 2 and all(r["think_end"] is None for r in recs)
    # a non-continuation collection ignores the tag and carries no field
    recs = S.split_records("c", t, continuation=False)
    assert [r["text"] for r in recs] == ["First thought.", "Second thought.", NL + "</think>", NL + NL + "The reply, which is not split.", "Answer:", "E"]
    assert "think_end" not in recs[0]
    # a tag at the very start leaves nothing to split
    assert S.split_records("c", "</think>Reply.", continuation=True) == []
    assert "archived500" in S.CONTINUATION_COLLECTIONS and "source" not in S.CONTINUATION_COLLECTIONS


def test_collections_and_trace_ids(sources):
    sweep = S.load_collection("sweep44")
    assert [tid for tid, _ in sweep] == [f"s0819_eval0multi0_{k:03d}" for k in range(1, 45)]
    assert dict(sweep)["s0819_eval0multi0_004"] == sources["c004"]
    assert dict(sweep)["s0819_eval0multi0_036"] == sources["e036"]
    archived = S.load_collection("archived500")
    assert len(archived) == 500 and len({tid for tid, _ in archived}) == 500
    assert archived[0][0] == "rs0823_cut000_003"
    # ids: rs0823_cutNNN_NNN (the 25 shared cut-0 samples), rs0823_c004_cutNNN_NNN (325),
    # rs0823_e036_cutNNN_NNN (150)
    import re
    pat = re.compile(r"rs0823(_c004|_e036)?_cut\d{3}_\d{3}")
    assert all(pat.fullmatch(tid) for tid, _ in archived)
    arms = [pat.fullmatch(tid).group(1) for tid, _ in archived]
    assert (arms.count(None), arms.count("_c004"), arms.count("_e036")) == (25, 325, 150)


def test_source_part_rows(sources):
    """The listing's equation-rule sentences (parts 2 and 3) at their known indices."""
    c = S.split_records("c004", sources["c004"], with_old=True)
    e = S.split_records("e036", sources["e036"], with_old=True)
    c_parts = [(r["s"], r["old_s"], r["part"]) for r in c if r["part"] > 1]
    e_parts = [(r["s"], r["old_s"], r["part"]) for r in e if r["part"] > 1]
    assert c_parts == [(16, 15, 2), (24, 22, 2), (32, 29, 2), (49, 45, 2), (51, 46, 2), (54, 48, 2),
                       (57, 50, 2), (221, 213, 2), (369, 360, 2)]
    assert e_parts == [(18, 17, 2), (19, 17, 3), (35, 32, 2), (37, 33, 2), (39, 34, 2), (61, 55, 2),
                       (110, 103, 2)]
    assert c[221]["text"] == "(Identity)"
    assert e[19]["text"].startswith("(Wait, the classic problem says")
    assert e[220]["text"] == NL + "   [Output] -> *Proceeds* (Note:"
