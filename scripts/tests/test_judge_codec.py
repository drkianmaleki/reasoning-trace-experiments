"""Unit tests for scripts/judge_codec.py (the judge's reply format) and the inventory of
prompts/labels_v1.json.  Run s1a_make_prompt.py first (it writes the inventory).

Run:  python -m pytest -q scripts/tests/test_judge_codec.py
"""
import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import judge_codec as J  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
LABELS = REPO / "prompts" / "labels_v1.json"
LISTING = REPO / "docs" / "shared" / "2026-09-16_source_traces_labeled_v3.md"
SENTENCES = REPO / "runs" / "tests" / "t2_split_2026-09-16_2224" / "sentences_source.jsonl"

ROW = re.compile(r"^\| s(\d+)\(new\)-s(\d+)\(old(?:, part (\d))?\) \| (.*?) \| (.*) \|\s*$")
NODE_NAME = re.compile(r" \(\[?[A-Z][a-z](?:\+[A-Z][a-z])?\]?[\u2080-\u2089]+[\u00b9\u00b2\u00b3\u2070-\u2079]*(?:\(\d+\))?\)")
SEP = re.compile(r" \\?\|\\?\| ")  # the listing's escaped `\|\|`
NEW_LEAF = "Reasoning > logical reasoning > algebra"  # added to Section 3a in scheme v5 (item 17)


def reviewed_labels() -> dict[str, list[list[str]]]:
    """{trace: [[path, ...] per sentence]} from the listing's Node column."""
    out: dict[str, list[list[str]]] = {"c004": [], "e036": []}
    trace = None
    with open(LISTING, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("## C-trace"):
                trace = "c004"
            elif line.startswith("## E-trace"):
                trace = "e036"
            elif line.startswith("## "):
                trace = None
            m = ROW.match(line)
            if not (m and trace):
                continue
            assert int(m.group(1)) == len(out[trace])
            node = NODE_NAME.sub("", m.group(4))
            paths = list(dict.fromkeys(p.strip() for p in SEP.split(node)))
            assert 1 <= len(paths) <= 2, node
            out[trace].append(paths)
    return out


@pytest.fixture(scope="module")
def inv():
    return J.Inventory.load(LABELS)


@pytest.fixture(scope="module")
def sentence_counts():
    counts = {}
    with open(SENTENCES, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            counts[r["trace_id"]] = counts.get(r["trace_id"], 0) + 1
    return counts


# ----------------------------------------------------------------------------
# Inventory
# ----------------------------------------------------------------------------

def test_inventory_shape(inv):
    data = json.loads(LABELS.read_text(encoding="utf-8"))
    assert data["version"] == "v1"
    assert data["scheme"] == "2026-09-16_labeling_scheme_v5.md"
    assert len(data["paths"]) == 75
    assert inv.path_to_code[NEW_LEAF] == "Re.lr.al"
    assert re.fullmatch(r"[0-9a-f]{64}", data["scheme_sha256"])
    assert data["level1"] == {"Pl": "Planning", "Re": "Reasoning", "Rf": "Reflection", "Kn": "Knowledge",
                              "Rs": "Restatement", "As": "Assumption", "Ex": "Example", "Co": "Conclusion"}
    codes = [e["code"] for e in data["paths"]]
    assert len(codes) == len(set(codes)) == len(inv)
    for e in data["paths"]:
        assert 2 <= len(e["path"]) <= 3
        parts = e["code"].split(".")
        assert len(parts) == len(e["path"])
        assert parts[0] == {v: k for k, v in data["level1"].items()}[e["path"][0]]
        for part in parts[1:]:
            assert re.fullmatch(r"[a-z]{2,3}|[A-F]", part), e["code"]
    assert "Re.ca.al" in inv and inv.code_to_path["Re.ca.al"] == "Reasoning > calculation > algebra"
    assert inv.path_to_code["Reasoning > option evaluation > (C)"] == "Re.oe.C"
    assert all(f"Re.oe.{x}" in inv for x in "ABCDEF")
    assert "Pl" not in inv and "Re" not in inv  # Level 1 alone is not a label


def test_every_reviewed_path_is_in_the_inventory(inv):
    used = {p for labels in reviewed_labels().values() for paths in labels for p in paths}
    missing = {p for p in used if p not in inv.path_to_code}
    assert missing == set(), missing
    assert len(used) == 44


# ----------------------------------------------------------------------------
# Round trip on the reviewed labels of both source traces
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("trace_id,n_expected", [("c004", 375), ("e036", 254)])
def test_round_trip_reviewed_labels(inv, sentence_counts, trace_id, n_expected):
    labels = reviewed_labels()[trace_id]
    assert len(labels) == n_expected == sentence_counts[trace_id]
    text = J.encode(labels, inv)
    parsed, warnings = J.parse_reply_with_warnings(text, len(labels), inv)
    assert parsed == labels and warnings == []  # exact round trip, no special-casing
    assert sum(1 for paths in labels if len(paths) == 2) == {"c004": 8, "e036": 5}[trace_id]
    n_new_leaf = sum(1 for paths in labels for p in paths if p == NEW_LEAF)
    assert n_new_leaf == {"c004": 14, "e036": 4}[trace_id]  # 18 in all, encoded as Re.lr.al
    assert text.count("Re.lr.al") >= 1
    # the canonical form is stable and compact
    assert J.encode(parsed, inv) == text
    assert all(J.LINE_RE.match(l) for l in text.splitlines())


# ----------------------------------------------------------------------------
# encode / parse on synthetic data
# ----------------------------------------------------------------------------

def test_encode_runs_and_combined_lines(inv):
    A, B, C = "Planning > global plan", "Reasoning > calculation > algebra", "Reflection > meta-evaluation of a step > option (B)"
    labels = [[A], [A], [B], [B, C], [B], [B], [A]]
    assert J.encode(labels, inv) == "0-1 Pl.gp\n2 Re.ca.al\n3 Re.ca.al+Rf.meo.B\n4-5 Re.ca.al\n6 Pl.gp"
    assert J.parse_reply(J.encode(labels, inv), 7, inv) == labels


def test_encode_rejects_bad_input(inv):
    with pytest.raises(ValueError):
        J.encode([[]], inv)
    with pytest.raises(ValueError):
        J.encode([["Planning"]], inv)  # Level 1 alone
    with pytest.raises(ValueError):
        J.encode([["Reasoning > logical reasoning > geometry"]], inv)  # not in the inventory


def test_blank_lines_and_whitespace_tolerated(inv):
    text = "\n\n  0-1 Pl.gp  \n\n2 Re.ca.al\n   \n"
    assert J.parse_reply(text, 3, inv) == [["Planning > global plan"]] * 2 + [["Reasoning > calculation > algebra"]]


def test_code_fence_stripped_with_warning(inv):
    text = "```\n0-1 Pl.gp\n2 Re.ca.al\n```"
    labels, warnings = J.parse_reply_with_warnings(text, 3, inv)
    assert len(labels) == 3 and len(warnings) == 2
    text = "```text\n0-1 Pl.gp\n2 Re.ca.al\n```\n"
    labels, warnings = J.parse_reply_with_warnings(text, 3, inv)
    assert len(labels) == 3 and warnings[0].startswith("opening code fence stripped")
    assert J.parse_reply_with_warnings("0-2 Pl.gp", 3, inv)[1] == []


def test_inventory_argument_forms(inv):
    d = {"Pl.gp": "Planning > global plan"}
    assert J.parse_reply("0 Pl.gp", 1, d) == [["Planning > global plan"]]
    assert J.parse_reply("0 Pl.gp", 1, inv) == [["Planning > global plan"]]
    with pytest.raises(TypeError):
        J.parse_reply("0 Pl.gp", 1, 42)


# ----------------------------------------------------------------------------
# Every error kind, one synthetic reply each
# ----------------------------------------------------------------------------

def kind_of(text, n, inv):
    with pytest.raises(J.ReplyError) as e:
        J.parse_reply(text, n, inv)
    return e.value.kind


def test_every_error_kind(inv):
    assert kind_of("0-1 Pl.gp\nhello world", 3, inv) == "unparsable"
    assert kind_of("0-1 Pl.gp\n2 Zz.qq", 3, inv) == "unknown_code"
    assert kind_of("0-1 Pl.gp\n3 Re.ca.al", 4, inv) == "gap"
    assert kind_of("0-1 Pl.gp", 3, inv) == "gap"  # missing tail
    assert kind_of("", 1, inv) == "gap"  # nothing at all
    assert kind_of("0-2 Pl.gp\n2 Re.ca.al", 3, inv) == "overlap"
    assert kind_of("0-1 Pl.gp\n2-5 Re.ca.al", 3, inv) == "out_of_range"
    assert kind_of("0-1 Pl.gp\n2 Re.ca.al+Rf.meo+Co.ic", 3, inv) == "too_many_codes"
    assert kind_of("2 Re.ca.al\n0-1 Pl.gp", 3, inv) == "gap"  # first run does not start at 0
    assert kind_of("0-1 Pl.gp\n2-3 Re.ca.al\n1 Co.ic", 4, inv) == "descending"
    assert kind_of("0-1 Pl.gp\n3-2 Re.ca.al", 4, inv) == "descending"
    assert kind_of("0-1 Pl.gp+Re.ca.al\n2 Co.ic", 3, inv) == "unparsable"  # combined label on a run
    assert kind_of("0 Pl.gp+Pl.gp\n1 Co.ic", 2, inv) == "unparsable"  # identical codes
    assert set(J.KINDS) == {"unparsable", "unknown_code", "gap", "overlap", "out_of_range", "too_many_codes", "descending"}


def test_error_carries_position_and_detail(inv):
    with pytest.raises(J.ReplyError) as e:
        J.parse_reply("0-1 Pl.gp\n\n2 Zz.qq", 3, inv)
    assert (e.value.kind, e.value.line_no, e.value.line) == ("unknown_code", 3, "2 Zz.qq")
    assert "Zz.qq" in e.value.detail and "line 3" in str(e.value)


# ----------------------------------------------------------------------------
# The six synthetic replies of pipeline v1, Section 9 item 5
# ----------------------------------------------------------------------------

SIX = [
    ("valid", "0-1 Pl.gp\n2-4 Re.ca.al\n5 Re.hwa.er+Rf.meo.B\n6-7 Rs.rtp.qt\n8 Co.fa", None),
    ("a gap", "0-1 Pl.gp\n3-4 Re.ca.al\n5 Re.hwa.er+Rf.meo.B\n6-7 Rs.rtp.qt\n8 Co.fa", "gap"),
    ("an overlap", "0-2 Pl.gp\n2-4 Re.ca.al\n5 Re.hwa.er+Rf.meo.B\n6-7 Rs.rtp.qt\n8 Co.fa", "overlap"),
    ("an unknown code", "0-1 Pl.gp\n2-4 Re.ca.xx\n5 Re.hwa.er+Rf.meo.B\n6-7 Rs.rtp.qt\n8 Co.fa", "unknown_code"),
    ("three codes on one sentence", "0-1 Pl.gp\n2-4 Re.ca.al\n5 Re.hwa.er+Rf.meo.B+Co.ic\n6-7 Rs.rtp.qt\n8 Co.fa", "too_many_codes"),
    ("a run past the last sentence", "0-1 Pl.gp\n2-4 Re.ca.al\n5 Re.hwa.er+Rf.meo.B\n6-7 Rs.rtp.qt\n8-9 Co.fa", "out_of_range"),
]


@pytest.mark.parametrize("name,text,kind", SIX)
def test_six_synthetic_replies(inv, name, text, kind):
    if kind is None:
        labels = J.parse_reply(text, 9, inv)
        assert len(labels) == 9 and labels[5] == ["Reasoning > hedge word analysis > everyday reading",
                                                  "Reflection > meta-evaluation of a step > option (B)"]
    else:
        assert kind_of(text, 9, inv) == kind


def test_exactly_the_first_of_the_six_parses(inv):
    ok = [name for name, text, _ in SIX if _parses(text, inv)]
    assert ok == ["valid"]


def _parses(text, inv):
    try:
        J.parse_reply(text, 9, inv)
        return True
    except J.ReplyError:
        return False
