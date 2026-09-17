"""Unit tests for scripts/s4_analyze.py on hand-computable toys: a 4-row pcut (P_hat, Delta,
Newcombe, gap, shares), the permutation test on a 3-cut toy with the null true and false by
construction, the plots and tables.  Run: python -m pytest -q scripts/tests/test_s4_analyze.py"""
import csv
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import s4_analyze as A  # noqa: E402
import stats_utils as ST  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
PCORPUS = REPO / "runs" / "experiments" / "judge_sweep44_2026-09-17_1334" / "pcorpus_L1.csv"
L1 = A.L1


def write_toy_run(folder: Path, cut_answers: dict[str, list[str]], meta: dict[str, dict], judged: dict[str, list[tuple[str, bool, bool]]] | None = None,
                  noise: dict[str, list[tuple[str, bool, bool]]] | None = None) -> tuple[Path, Path]:
    """pcut.csv + continuations.jsonl from answers per prefix; a judge folder from labels per prefix."""
    folder.mkdir(parents=True, exist_ok=True)
    rows = []
    recs = []
    for pid, answers in cut_answers.items():
        m = meta[pid]
        counts = {L: sum(1 for a in answers if a == L) for L in "ABCDEF"}
        rows.append({"trace_id": m["trace_id"], "m": m["m"], "condition": m["condition"], "prefix_id": pid, "block_end_s": m.get("block_end_s", ""),
                     "prefix_char_end": 0, "n": len(answers), **{f"count_{L}": counts[L] for L in "ABCDEF"},
                     "count_other": 0, "count_unresolved": sum(1 for a in answers if a == "?"), "p_hat": "", "ci_low": "", "ci_high": "",
                     "prompt_tokens": m.get("prompt_tokens", ""), "tk_block": m.get("tk", ""), "mean_completion_tokens": 0, "cost_usd": 0, "stopped": False,
                     "think_reopened": 0, "timestamp": ""})
        for i, a in enumerate(answers):
            recs.append({"id": f"{pid}_{i:03d}", "prefix_id": pid, "trace_arm": m["trace_id"], "condition": m["condition"], "cut": m.get("block_end_s"),
                         "block": m["m"] if m["condition"] == "cut" else None, "seq": i, "letters": [a] if a != "?" else [], "answer": a})
    with open(folder / "pcut.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (folder / "continuations.jsonl").write_text("".join(json.dumps(r) + "\n" for r in recs), encoding="utf-8")
    judge = folder / "judge"
    for name, data in (("rb_c004", judged or {}), ("noise_c004_B01", noise or {})):
        d = judge / name
        d.mkdir(parents=True, exist_ok=True)
        with open(d / f"blocks_{name}_judge.jsonl", "w", encoding="utf-8") as fh:
            for pid, labels in data.items():
                for i, (l1, opens, wait) in enumerate(labels):
                    fh.write(json.dumps({"trace_id": f"{pid}_{i:03d}", "prefix_id": pid, "trace_arm": meta[pid]["trace_id"], "cut": meta[pid].get("block_end_s"),
                                         "first_new_node": {"L1": l1, "opens_block": opens, "opener_rule": "R1" if opens else None}, "first_sentence_r4": wait}) + "\n")
        (d / "config.json").write_text(json.dumps({"model": "stub", "prompt": "judge_prompt_v3.md", "prompt_sha256": "x", "thinking_mode": "low"}), encoding="utf-8")
    return folder, judge


META = {"rb_cut0": {"trace_id": "shared", "m": "cut0", "condition": "cut0", "prompt_tokens": 140},
        "rb_c004_B00": {"trace_id": "c004", "m": 0, "condition": "cut", "block_end_s": 7, "tk": 120, "prompt_tokens": 260},
        "rb_c004_B01": {"trace_id": "c004", "m": 1, "condition": "cut", "block_end_s": 12, "tk": 40, "prompt_tokens": 300},
        "rb_c004_B02": {"trace_id": "c004", "m": 2, "condition": "cut", "block_end_s": 14, "tk": 15, "prompt_tokens": 315}}
ANSWERS = {"rb_cut0": ["C"] * 3 + ["E"] * 20 + ["A", "?"], "rb_c004_B00": ["C"] * 9 + ["?"] * 8 + ["E"] * 7 + ["B"],
           "rb_c004_B01": ["C"] * 16 + ["E"] * 4 + ["B"] * 2 + ["?"] * 3, "rb_c004_B02": ["C"] * 25}


def test_mediation_hand_values(tmp_path):
    run, judge = write_toy_run(tmp_path / "toy", ANSWERS, META)
    res = A.analyze(run, judge, tmp_path / "out", PCORPUS, draws=400, perms=50, seed=1, log=lambda s: None)
    s = res["mediation"][0]
    assert s["trace_id"] == "c004" and s["cuts_sampled"] == 3 and s["M"] == 2
    assert s["p_cut0"] == pytest.approx(0.12) and s["p_M"] == 1.0 and s["total_movement"] == pytest.approx(0.88)
    assert s["B_top"] == 2 and s["delta_top"] == pytest.approx(0.36) and s["gap"] == pytest.approx(0.08) and s["tk_B_top"] == 15
    assert s["tk_B_top_share"] == pytest.approx(15 / 4740) and s["tk_trace"] == 4740
    assert s["share_top1"] == pytest.approx(0.36 / 0.88) and s["share_top2"] == pytest.approx(0.64 / 0.88) and s["share_top3"] == pytest.approx(1.0)
    assert s["blocks_to_half"] == 2 and s["trivial_blocks"] == 0 and s["gap_low"] <= s["gap"] <= s["gap_high"]
    delta = {int(r["m"]): r for r in A.read_csv(tmp_path / "out" / "mediation_delta.csv")}
    assert float(delta[0]["delta"]) == pytest.approx(0.24) and float(delta[1]["delta"]) == pytest.approx(0.28) and float(delta[2]["delta"]) == pytest.approx(0.36)
    # Newcombe for Delta_1 = 16/25 - 9/25, hand: Wilson(16,25) = [0.4452, 0.7975], Wilson(9,25) = [0.2025, 0.5548]
    # low = 0.28 - sqrt((0.64-0.4452)^2 + (0.5548-0.36)^2) = 0.0045; high = 0.28 + sqrt((0.7975-0.64)^2 + (0.36-0.2025)^2) = 0.5027
    assert float(delta[1]["delta_low"]) == pytest.approx(0.0045, abs=2e-3) and float(delta[1]["delta_high"]) == pytest.approx(0.5027, abs=2e-3)
    assert ST.newcombe(16, 25, 9, 25) == pytest.approx((0.0045, 0.5027), abs=2e-3)
    pc = {r["m"]: r for r in A.read_csv(tmp_path / "out" / "mediation_pcut.csv")}
    assert pc["cut0"]["p_E"] == "0.8000" and pc["0"]["p_aT"] == "0.3600" and pc["2"]["p_aT_low"] == "0.8668"
    assert (tmp_path / "out" / "stage1_summary.md").read_text(encoding="utf-8").count("The largest shift, Δ = +0.36, sits in B_02") == 1
    figs = [Path(p) for p in res["figures"]]
    assert [p.name for p in figs] == ["toy_c004_phat.png", "toy_c004_delta.png"] and all(p.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n" for p in figs)
    for p in figs:
        p.unlink()  # the toy's figures do not stay in figures/


def labels_from(dist: dict[str, int], seed: int, opens=True) -> list[tuple[str, bool, bool]]:
    import numpy as np
    rng = np.random.default_rng(seed)
    labels = [l for l, k in dist.items() for _ in range(k)]
    rng.shuffle(labels)
    return [(l, opens, l == "Planning" and i % 2 == 0) for i, l in enumerate(labels)]


def test_permutation_null_true_and_false(tmp_path):
    # X of the c004 cuts after s7, s12, s14 under listing v4: Restatement, Restatement, Planning -> the Restatement group has two cuts, Planning is a singleton
    same = {"Planning": 15, "Reasoning": 7, "Restatement": 3}
    judged_true = {"rb_c004_B00": labels_from(same, 1), "rb_c004_B01": labels_from(same, 2), "rb_c004_B02": labels_from(same, 3)}
    run, judge = write_toy_run(tmp_path / "null_true", ANSWERS, META, judged_true)
    res = A.analyze(run, judge, tmp_path / "out_true", PCORPUS, draws=200, perms=400, seed=0, log=lambda s: None)
    perm = {r["scope"]: r for r in res["permutation"]}
    assert perm["c004"]["cuts_included"] == 2 and perm["c004"]["groups"] == 1 and perm["c004"]["singleton_X_excluded"] == "Planning"
    assert perm["c004"]["p"] > 0.05 and perm["pooled"]["p"] == perm["c004"]["p"]  # e036 has no cuts here
    assert perm["e036"]["cuts_included"] == 0
    pn = {r["m"]: r for r in A.read_csv(tmp_path / "out_true" / "transition_pnext.csv")}
    assert pn["0"]["X"] == "Restatement" and pn["1"]["X"] == "Restatement" and pn["2"]["X"] == "Planning"
    assert pn["0"]["Y_source"] == "Planning" and pn["0"]["source_opens"] == "True" and float(pn["0"]["p_Planning"]) == pytest.approx(0.6)
    assert float(pn["0"]["opens_block_frac"]) == 1.0 and 0 < float(pn["0"]["wait_frac"]) < 1
    for p in res["figures"]:
        Path(p).unlink()  # the toy's figures do not stay in figures/
    judged_false = {"rb_c004_B00": labels_from({"Planning": 24, "Reasoning": 1}, 1), "rb_c004_B01": labels_from({"Reasoning": 24, "Planning": 1}, 2),
                    "rb_c004_B02": labels_from(same, 3)}
    run, judge = write_toy_run(tmp_path / "null_false", ANSWERS, META, judged_false)
    res = A.analyze(run, judge, tmp_path / "out_false", PCORPUS, draws=200, perms=400, seed=0, log=lambda s: None)
    perm = {r["scope"]: r for r in res["permutation"]}
    # pooled over the two Restatement cuts: (0.5, 0.5); each cut's TV to it = 0.5 * (0.46 + 0.46) = 0.46; S = mean = 0.46
    assert perm["c004"]["p"] < 0.02 and perm["c004"]["S_obs"] == pytest.approx(0.46)
    tvc = {(r["scope"], r["X"]): r for r in A.read_csv(tmp_path / "out_false" / "transition_tv_corpus.csv")}
    assert tvc[("pooled", "Restatement")]["cuts"] == "2" and tvc[("pooled", "Restatement")]["continuations"] == "50"
    assert 0 <= float(tvc[("pooled", "Restatement")]["tv_corpus"]) <= 1
    for p in res["figures"]:
        Path(p).unlink()


def test_noise_subset_and_history(tmp_path):
    same = {"Planning": 15, "Reasoning": 7, "Restatement": 3}
    judged = {"rb_c004_B00": labels_from(same, 1), "rb_c004_B01": labels_from(same, 2), "rb_c004_B02": labels_from(same, 3)}
    noise = {"rb_c004_B01": labels_from({"Planning": 14, "Reasoning": 8, "Restatement": 3}, 9)}
    run, judge = write_toy_run(tmp_path / "noise", ANSWERS, META, judged, noise)
    res = A.analyze(run, judge, tmp_path / "out", PCORPUS, draws=200, perms=200, seed=0, log=lambda s: None)
    assert len(res["noise"]) == 1 and res["noise"][0]["m"] == 1 and res["noise"][0]["n_second"] == 25
    assert res["noise"][0]["tv_first_vs_second"] == pytest.approx(0.04) and res["noise"][0]["first_node_common"] == 25
    perm = {r["scope"]: r for r in A.read_csv(tmp_path / "out" / "transition_permutation.csv")}
    assert "c004_second_labeling" in perm and "pooled_second_labeling" in perm
    assert res["n_history_rows"] == 0 and res["n_order_rows"] == 0  # three cuts: no pair with three on each side
    md = (tmp_path / "out" / "stage1_summary.md").read_text(encoding="utf-8")
    assert "second labeling" in md and "_second_labeling" in md and "no verdict" in md
    for p in res["figures"]:
        Path(p).unlink()


def test_load_pcorpus_rows_normalized():
    pc = A.load_pcorpus(PCORPUS)
    assert set(pc) == set(L1) and all(abs(sum(pc[x].values()) - 1) < 1e-9 for x in L1)
    assert pc["Conclusion"]["Planning"] == pytest.approx(651 / 1030, abs=1e-6)
