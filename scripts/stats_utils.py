#!/usr/bin/env python3
"""stats_utils.py -- the interval, distance and resampling arithmetic of pre-registration stage
one, Sections 5 and 6 (pipeline v2, step 9/9).  numpy for the resampling loops; every function
is deterministic given its seed.

- wilson(k, n): the Wilson score interval of a proportion (95% by default).
- newcombe(k1, n1, k2, n2): the Newcombe (1998, method 10) hybrid-score interval for p1 - p2.
- tv(p, q): the total-variation distance 0.5 * sum |p - q| over the union of keys.
- distribution(labels, keys): the empirical distribution over `keys`.
- bootstrap_gap(...): the gap between the two largest Delta_m with a percentile bootstrap that
  resamples continuations within each cut (Section 5.3).
- permutation_test(...): the type-only null of Section 6.2 -- S = mean over cuts of
  TV(p_hat_m, p_hat_X) with continuations reassigned at random among the cuts sharing X.
- bootstrap_tv(...): a percentile bootstrap interval of TV(p_hat, reference) resampling one cut's
  continuations (Sections 6.2 and 6.3).
"""
from __future__ import annotations

import math
from collections import Counter

import numpy as np

Z95 = 1.959964


def wilson(k: int, n: int, z: float = Z95) -> tuple[float, float]:
    if n <= 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def newcombe(k1: int, n1: int, k2: int, n2: int, z: float = Z95) -> tuple[float, float]:
    """Interval for p1 - p2 (Newcombe 1998, method 10: hybrid of the two Wilson intervals)."""
    if n1 <= 0 or n2 <= 0:
        return (float("nan"), float("nan"))
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson(k1, n1, z)
    l2, u2 = wilson(k2, n2, z)
    d = p1 - p2
    return (d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2))


def distribution(labels: list[str], keys: list[str]) -> dict[str, float]:
    c = Counter(labels)
    n = len(labels)
    return {k: (c.get(k, 0) / n if n else float("nan")) for k in keys}


def tv(p: dict[str, float], q: dict[str, float]) -> float:
    keys = set(p) | set(q)
    return 0.5 * sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys)


def _phat(answers: np.ndarray, target: int) -> float:
    return float(np.mean(answers == target)) if answers.size else float("nan")


def gap_of(deltas: list[float]) -> float:
    """Delta_(1) - Delta_(2), the two largest signed shifts; nan with fewer than two cuts."""
    if len(deltas) < 2:
        return float("nan")
    s = sorted(deltas, reverse=True)
    return s[0] - s[1]


def bootstrap_gap(cut0_answers: list[str], cuts_answers: list[list[str]], a_t: str, draws: int = 10000, seed: int = 0) -> dict:
    """Section 5.3: the gap with a percentile bootstrap interval, resampling continuations
    within cut-0 and within each cut (draws x all cuts).  Answers are strings; a_t the trace's
    own answer.  Returns observed gap, top block index, interval and the draws' mean."""
    rng = np.random.default_rng(seed)
    enc = lambda a: np.array([1 if x == a_t else 0 for x in a], dtype=np.int8)
    base = enc(cut0_answers)
    cuts = [enc(a) for a in cuts_answers]

    def deltas_from(base_s, cuts_s):
        prev = _phat(base_s, 1)
        out = []
        for c in cuts_s:
            p = _phat(c, 1)
            out.append(p - prev)
            prev = p
        return out

    obs = deltas_from(base, cuts)
    gap_obs = gap_of(obs)
    top = int(np.argmax(obs)) if obs else None
    gaps = np.empty(draws)
    for i in range(draws):
        b = rng.choice(base, size=base.size, replace=True) if base.size else base
        cs = [rng.choice(c, size=c.size, replace=True) if c.size else c for c in cuts]
        gaps[i] = gap_of(deltas_from(b, cs))
    finite = gaps[np.isfinite(gaps)]
    lo, hi = (float(np.percentile(finite, 2.5)), float(np.percentile(finite, 97.5))) if finite.size else (float("nan"), float("nan"))
    return {"gap": gap_obs, "top": top, "deltas": obs, "ci_low": lo, "ci_high": hi, "draws": draws, "seed": seed,
            "mean_draw": float(finite.mean()) if finite.size else float("nan")}


def permutation_test(groups: dict[str, list[list[str]]], keys: list[str], n_perm: int = 10000, seed: int = 0) -> dict:
    """Section 6.2.  groups: {X: [labels of cut 1, labels of cut 2, ...]} (cuts sharing the
    last-node label X; groups with a single cut are excluded and listed).  S = mean over the
    included cuts of TV(p_hat_m, p_hat_X); the null reassigns continuations at random among the
    cuts of each group, keeping every cut's n.  p = (#{S_perm >= S_obs} + 1) / (n_perm + 1)."""
    rng = np.random.default_rng(seed)
    key_index = {k: i for i, k in enumerate(keys)}
    included = {x: cuts for x, cuts in groups.items() if len(cuts) >= 2}
    singletons = sorted(x for x, cuts in groups.items() if len(cuts) < 2)
    if not included:
        return {"S_obs": float("nan"), "p": float("nan"), "n_perm": n_perm, "seed": seed, "cuts": 0, "groups": 0,
                "singletons": singletons, "per_cut_tv": {}, "S_perm_mean": float("nan")}
    arrays = {x: [np.array([key_index[l] for l in cut], dtype=np.int16) for cut in cuts] for x, cuts in included.items()}
    K = len(keys)

    def dist(a: np.ndarray) -> np.ndarray:
        return np.bincount(a, minlength=K) / a.size if a.size else np.full(K, np.nan)

    def stat(arrs: dict[str, list[np.ndarray]]) -> tuple[float, dict]:
        tvs = {}
        for x, cuts in arrs.items():
            pooled = dist(np.concatenate(cuts))
            for i, c in enumerate(cuts):
                tvs[(x, i)] = 0.5 * float(np.abs(dist(c) - pooled).sum())
        return float(np.mean(list(tvs.values()))), tvs

    s_obs, per_cut = stat(arrays)
    count = 0
    s_perm = np.empty(n_perm)
    for k in range(n_perm):
        permuted = {}
        for x, cuts in arrays.items():
            pool = np.concatenate(cuts)
            rng.shuffle(pool)
            sizes = np.cumsum([c.size for c in cuts])[:-1]
            permuted[x] = np.split(pool, sizes)
        s, _ = stat(permuted)
        s_perm[k] = s
        if s >= s_obs - 1e-12:
            count += 1
    return {"S_obs": s_obs, "p": (count + 1) / (n_perm + 1), "n_perm": n_perm, "seed": seed,
            "cuts": sum(len(c) for c in included.values()), "groups": len(included), "singletons": singletons,
            "per_cut_tv": per_cut, "S_perm_mean": float(s_perm.mean())}


def bootstrap_tv(labels: list[str], reference: dict[str, float], keys: list[str], draws: int = 2000, seed: int = 0) -> dict:
    """TV(p_hat(labels), reference) with a percentile bootstrap interval over the labels."""
    rng = np.random.default_rng(seed)
    key_index = {k: i for i, k in enumerate(keys)}
    a = np.array([key_index[l] for l in labels], dtype=np.int16)
    ref = np.array([reference.get(k, 0.0) for k in keys])
    K = len(keys)

    def tv_of(arr):
        if not arr.size:
            return float("nan")
        return 0.5 * float(np.abs(np.bincount(arr, minlength=K) / arr.size - ref).sum())

    obs = tv_of(a)
    if not a.size:
        return {"tv": obs, "ci_low": float("nan"), "ci_high": float("nan"), "n": 0}
    vals = np.array([tv_of(rng.choice(a, size=a.size, replace=True)) for _ in range(draws)])
    return {"tv": obs, "ci_low": float(np.percentile(vals, 2.5)), "ci_high": float(np.percentile(vals, 97.5)), "n": int(a.size)}
