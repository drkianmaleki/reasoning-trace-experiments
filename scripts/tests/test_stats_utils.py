"""Unit tests for scripts/stats_utils.py against hand calculations.
Run: python -m pytest -q scripts/tests/test_stats_utils.py"""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import stats_utils as ST  # noqa: E402

L1 = ["Planning", "Reasoning", "Reflection", "Knowledge", "Restatement", "Assumption", "Example", "Conclusion"]


def test_wilson_hand_values():
    # k = 21, n = 25, z = 1.959964: p = 0.84; centre = (0.84 + 0.076830)/1.153664 = 0.79471;
    # half = 1.959964 * sqrt(0.84*0.16/25 + z^2/(4*625)) / 1.153664 = 1.959964 * sqrt(0.005376 + 0.0015366)/1.153664 = 0.14126
    lo, hi = ST.wilson(21, 25)
    assert lo == pytest.approx(0.6535, abs=2e-4) and hi == pytest.approx(0.9360, abs=2e-4)
    # P_hat = 1 at n = 25: centre = (1 + z^2/50)/(1 + z^2/25) = 1.076830/1.153664 = 0.93340, half = (z^2/50)/1.153664 = 0.06660 -> 0.8668
    assert ST.wilson(25, 25) == pytest.approx((0.8668, 1.0), abs=2e-4)
    assert ST.wilson(0, 25)[0] == 0.0 and ST.wilson(0, 25)[1] == pytest.approx(0.1332, abs=2e-4)  # 1 - 0.8668, by symmetry
    assert all(math.isnan(x) for x in ST.wilson(0, 0))
    # registration 3.6 quotes the exact (Clopper-Pearson) one-sided 95% bound at P_hat = 1, 0.05^(1/25) = 0.887;
    # the one-sided Wilson bound is 0.902 -- the report quotes the exact one
    assert 0.05 ** (1 / 25) == pytest.approx(0.887, abs=2e-3)
    assert ST.wilson(25, 25, z=1.644854)[0] == pytest.approx(0.902, abs=2e-3)
    assert 0.95 ** 25 == pytest.approx(0.277, abs=1e-3)  # P(P_hat = 1 | true P = 0.95) = 0.28 (registration 3.6)


def test_newcombe_hand_values():
    # p1 = 21/25, p2 = 14/25: d = 0.28; Wilson: l1 0.6535 u1 0.9360; l2 0.3712 u2 0.7327
    # low = 0.28 - sqrt((0.84-0.6535)^2 + (0.7327-0.56)^2) = 0.28 - sqrt(0.03478 + 0.02983) = 0.28 - 0.2542 = 0.0258
    # high = 0.28 + sqrt((0.9360-0.84)^2 + (0.56-0.3712)^2) = 0.28 + sqrt(0.009216 + 0.03565) = 0.28 + 0.2118 = 0.4918
    lo, hi = ST.newcombe(21, 25, 14, 25)
    assert lo == pytest.approx(0.0258, abs=1e-3) and hi == pytest.approx(0.4918, abs=1e-3)
    lo, hi = ST.newcombe(5, 25, 5, 25)
    assert lo == pytest.approx(-hi, abs=1e-9) and lo < 0 < hi


def test_tv_and_distribution():
    p = ST.distribution(["Planning", "Planning", "Reasoning", "Conclusion"], L1)
    assert p["Planning"] == 0.5 and p["Reasoning"] == 0.25 and p["Example"] == 0.0 and abs(sum(p.values()) - 1) < 1e-12
    q = ST.distribution(["Reasoning"] * 4, L1)
    assert ST.tv(p, q) == pytest.approx(0.75)  # 0.5 * (0.5 + 0.75 + 0.25)
    assert ST.tv(p, p) == 0.0 and ST.tv({"a": 1.0}, {"b": 1.0}) == 1.0
    assert math.isnan(ST.distribution([], L1)["Planning"])


def test_gap_and_bootstrap_reproducible():
    assert ST.gap_of([0.1, 0.5, 0.2]) == pytest.approx(0.3) and math.isnan(ST.gap_of([0.4]))
    cut0 = ["E"] * 20 + ["C"] * 3 + ["A", "?"]
    cuts = [["C"] * 9 + ["?"] * 8 + ["E"] * 7 + ["B"], ["C"] * 16 + ["E"] * 4 + ["B"] * 2 + ["?"] * 3, ["C"] * 25]
    r1 = ST.bootstrap_gap(cut0, cuts, "C", draws=500, seed=7)
    r2 = ST.bootstrap_gap(cut0, cuts, "C", draws=500, seed=7)
    assert r1["deltas"] == pytest.approx([0.36 - 0.12, 0.64 - 0.36, 1.0 - 0.64]) and r1["top"] == 2
    assert r1["gap"] == pytest.approx(0.36 - 0.28) and r1["ci_low"] <= r1["gap"] <= r1["ci_high"]
    assert r1["ci_low"] == r2["ci_low"] and r1["ci_high"] == r2["ci_high"]  # fixed seed
    assert ST.bootstrap_gap(cut0, cuts, "C", draws=500, seed=8)["mean_draw"] != r1["mean_draw"]  # another seed, another draw


def test_permutation_null_true_is_uniform_and_false_is_small():
    import numpy as np
    rng = np.random.default_rng(1)
    keys = L1[:3]
    # null true: three cuts sharing X drawn from one distribution -> p roughly uniform over seeds
    ps = []
    for seed in range(60):
        cuts = [list(rng.choice(keys, size=25, p=[0.5, 0.3, 0.2])) for _ in range(3)]
        ps.append(ST.permutation_test({"Reasoning": cuts}, keys, n_perm=300, seed=seed)["p"])
    ps = np.array(ps)
    assert 0.25 < np.mean(ps) < 0.75 and np.mean(ps < 0.1) < 0.3 and np.mean(ps > 0.9) < 0.3
    # null false by construction: three cuts with different distributions -> small p
    cuts = [["Planning"] * 22 + ["Reasoning"] * 3, ["Reasoning"] * 23 + ["Planning"] * 2, ["Reflection"] * 20 + ["Planning"] * 5]
    r = ST.permutation_test({"Reasoning": cuts}, keys, n_perm=500, seed=3)
    assert r["p"] < 0.01 and r["S_obs"] > 0.5 and r["cuts"] == 3 and r["groups"] == 1 and r["singletons"] == []
    assert len(r["per_cut_tv"]) == 3 and all(0 <= v <= 1 for v in r["per_cut_tv"].values())
    # singleton groups are excluded and listed; an all-singleton input gives nan
    r2 = ST.permutation_test({"Reasoning": cuts, "Planning": [cuts[0]]}, keys, n_perm=50, seed=0)
    assert r2["singletons"] == ["Planning"] and r2["cuts"] == 3
    assert math.isnan(ST.permutation_test({"Planning": [cuts[0]]}, keys)["p"])


def test_permutation_statistic_hand_value():
    # two cuts sharing X: [P,P,R,R] and [P,P,P,P]; pooled = (6/8 P, 2/8 R); TV = 0.25 each; S = 0.25
    r = ST.permutation_test({"X": [["Planning", "Planning", "Reasoning", "Reasoning"], ["Planning"] * 4]}, ["Planning", "Reasoning"], n_perm=20, seed=0)
    assert r["S_obs"] == pytest.approx(0.25) and 0 < r["p"] <= 1


def test_bootstrap_tv():
    ref = {"Planning": 0.5, "Reasoning": 0.5}
    r = ST.bootstrap_tv(["Planning"] * 10, ref, ["Planning", "Reasoning"], draws=100, seed=0)
    assert r["tv"] == pytest.approx(0.5) and r["ci_low"] == pytest.approx(0.5) and r["ci_high"] == pytest.approx(0.5) and r["n"] == 10
    r = ST.bootstrap_tv(["Planning"] * 5 + ["Reasoning"] * 5, ref, ["Planning", "Reasoning"], draws=200, seed=0)
    assert r["tv"] == 0.0 and r["ci_low"] == 0.0 and r["ci_high"] > 0
    assert math.isnan(ST.bootstrap_tv([], ref, ["Planning", "Reasoning"])["tv"])
