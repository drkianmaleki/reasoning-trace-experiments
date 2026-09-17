"""Unit tests for scripts/transitions.py on toy derivation records with hand-computed answers.
Run: python -m pytest -q scripts/tests/test_transitions.py"""
import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import derivation as D  # noqa: E402
import transitions as T  # noqa: E402

GP, IV, CA, IC, FA, KW, BR = ("Planning > global plan", "Planning > initiate verification", "Reasoning > calculation > algebra",
                              "Conclusion > intermediate conclusion", "Conclusion > final answer", "Knowledge > world knowledge",
                              "Assumption > branching (case split) > algebra")


def rec(labels, tid="t", texts=None):
    return D.derive(labels, tid, "test", texts)


def test_pcorpus_counts_and_rownorm(tmp_path):
    # t1 nodes: Pl Re Co Pl Re -> pairs Pl>Re, Re>Co, Co>Pl, Pl>Re ; t2 nodes: [Pl+Kn] Re -> Pl>Re (combined under its first path)
    r1 = rec([[GP], [CA], [IC], [IV], [CA]], "t1")
    r2 = rec([[GP, KW], [CA]], "t2")
    res = T.pcorpus([r1, r2])
    c = res["counts"]
    assert c["Planning"]["Reasoning"] == 3 and c["Reasoning"]["Conclusion"] == 1 and c["Conclusion"]["Planning"] == 1
    assert res["pairs"] == 5 and res["traces"] == 2
    assert res["marginal"] == {"Planning": 3, "Reasoning": 3, "Reflection": 0, "Knowledge": 0, "Restatement": 0, "Assumption": 0, "Example": 0, "Conclusion": 1}
    assert res["rownorm"]["Planning"]["Reasoning"] == pytest.approx(1.0) and res["rownorm"]["Reasoning"]["Conclusion"] == pytest.approx(1.0)
    assert sum(res["counts"]["Reasoning"].values()) == 1  # the Reasoning nodes at the end of each trace have no successor
    assert res["rownorm"]["Knowledge"]["Planning"] != res["rownorm"]["Knowledge"]["Planning"]  # nan row for an absent label
    assert res["blocks_per_trace"] == {"min": 1, "median": 1.5, "max": 2} and res["nodes_per_trace"] == {"min": 2, "median": 3.5, "max": 5}
    p1, p2 = T.write_pcorpus(tmp_path, res)
    rows = list(csv.reader(open(p1, encoding="utf-8")))
    assert rows[0][:3] == ["X_current_node", "Y_Planning", "Y_Reasoning"] and rows[1][0] == "Planning" and rows[1][2] == "3" and rows[1][-2:] == ["3", "3"]
    rows2 = list(csv.reader(open(p2, encoding="utf-8")))
    assert rows2[2][0] == "Reasoning" and rows2[2][8] == "1.0000" and rows2[2][1] == "0.0000"
    md = T.markdown_pcorpus(res, "toy")
    assert "| Planning | 0 | 3 |" in md and "Blocks per trace min / median / max: 1 / 1.5 / 2" in md


def test_psource_rows(tmp_path):
    r = rec([[GP], [CA], [IC], [BR], [CA], [FA]], "s")  # blocks [0-2] R1, [3-4] R2, [5] R3
    rows = T.psource(r)
    assert [(x["m"], x["s_cut"], x["last_node_label"], x["source_next_label"], x["next_opener_rule"]) for x in rows] == \
        [(0, 2, "Conclusion", "Assumption", "R2"), (1, 4, "Reasoning", "Conclusion", "R3")]
    assert rows[0]["last_node"] == "Co₀" and rows[0]["source_next_node"] == "As₁"
    p = T.write_psource(tmp_path / "psource_s.csv", rows)
    lines = p.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "m,s_cut,last_node,last_node_label,source_next_node,source_next_label,next_opener_rule" and len(lines) == 3
    assert "Conclusion → Assumption 1" in T.markdown_psource(rows, "toy")


def test_pnext_rows(tmp_path):
    def crec(tid, pid, arm, cut, l1, opens, wait, last="Reasoning"):
        return {"trace_id": tid, "prefix_id": pid, "trace_arm": arm, "cut": cut, "last_prefix_node_label": last,
                "first_new_node": {"L1": l1, "opens_block": opens}, "first_sentence_r4": wait}
    recs = [crec("e1", "pe60", "e036", 60, "Planning", True, True), crec("e2", "pe60", "e036", 60, "Reasoning", False, False),
            crec("c1", "pc15", "c004", 15, "Planning", True, False), crec("s1", "p0", "shared", 0, "Planning", True, False, None)]
    failures = {"e3": {"prefix_id": "pe60", "trace_arm": "e036", "cut": 60, "last_prefix_node_label": "Reasoning"}}
    rows = T.pnext(recs, failures)
    assert [r["prefix_id"] for r in rows] == ["p0", "pc15", "pe60"]  # shared, then c004, then e036, by cut
    e = rows[2]
    assert (e["n"], e["n_labeled"], e["n_failed"], e["next_Planning"], e["next_Reasoning"], e["opens_block"], e["first_is_wait"]) == (3, 2, 1, 1, 1, 1, 1)
    assert rows[0]["last_node_label"] is None and rows[1]["next_Planning"] == 1
    p = T.write_pnext(tmp_path / "pnext.csv", rows)
    lines = p.read_text(encoding="utf-8").splitlines()
    assert lines[0] == ",".join(T.PNEXT_FIELDS) and len(lines) == 4
    md = T.markdown_pnext(rows, "toy", limit=2)
    assert "| p0 |" in md and "| pc15 |" in md and "| pe60 |" not in md
