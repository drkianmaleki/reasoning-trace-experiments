# TEST_REPORT — t6_prereg — 2026-09-17 17:55

Test of pipeline step (6/9), the pre-registration `docs/shared/2026-09-17_preregistration_stage1_v2.md` (sha256 `53115b04214347b55c992a7e249e7e2b3a991bbe6a4c0de8a3999c76b42f10a5`), per pipeline v2 Section 9 item 8. Git commit `64ae55b4af25527d8c61619c5db8a902ed8bb4ba`. Offline; API cost $0.

## Result: FAIL (3/4 checks passed)

## Checks

- PASS — check 1, the registration file is in docs/shared and committed — exists True; commits 2; registration timestamp (earliest commit): b5f4a5a9b0526a7bfe2f5b7da65ace8db0066d11 2026-09-17 14:52:14 -0500 pre-registration of stage one (n=25, 84 prefixes under R4, stopping rule, judge Sonnet 5 x v3 x low, ceilings) â€” registration timestamp; STATE_2026-09-17_2
- PASS — check 2, the cut list of Section 3 items 3-4 equals the block ends derived from listing v4 under R4 and the pinned lists — text C 46 / E 37 indices; derived C 46 / E 37; equal True; C first/last s[7]…s[373], E s[11]…s[250]
- PASS — check 3, n, n_0, the ceilings and the stopping rule are stated — n = 25: present; n_0 = 100: present; DeepInfra ceiling $45: present; Claude ceiling $80: present; stopping rule: present; denominator: present
- FAIL — check 4, pytest on scripts/tests — exit code 1; last line: 1 failed, 193 passed in 6.82s

## git log of the registration file

```
64ae55b4af25527d8c61619c5db8a902ed8bb4ba 2026-09-17 17:51:58 -0500 run scripts s2/s3/s4 with tests t6-t9 (PASS), smoke tests; pre-registration v2 (pre-run amendments: stop sequence, no-think cap 8000, judge ceiling order)
b5f4a5a9b0526a7bfe2f5b7da65ace8db0066d11 2026-09-17 14:52:14 -0500 pre-registration of stage one (n=25, 84 prefixes under R4, stopping rule, judge Sonnet 5 x v3 x low, ceilings) â€” registration timestamp; STATE_2026-09-17_2
```

## pytest output

```
........................................................................ [ 37%]
........................................................................ [ 74%]
.................F................................                       [100%]
================================== FAILURES ===================================
_________________________ test_mediation_hand_values __________________________

tmp_path = WindowsPath('C:/Users/kianu/AppData/Local/Temp/pytest-of-kianu/pytest-61/test_mediation_hand_values0')

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
>           p.unlink()  # the toy's figures do not stay in figures/
            ^^^^^^^^^^

scripts\tests\test_s4_analyze.py:85: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = WindowsPath('C:/Users/kianu/Dropbox/Projects/Ongoing/reasoning-trace-experiments/figures/toy_c004_phat.png')
missing_ok = False

    def unlink(self, missing_ok=False):
        """
        Remove this file or link.
        If the path is a directory, use rmdir() instead.
        """
        try:
>           os.unlink(self)
E           PermissionError: [WinError 32] The process cannot access the file because it is being used by another process: 'C:\\Users\\kianu\\Dropbox\\Projects\\Ongoing\\reasoning-trace-experiments\\figures\\toy_c004_phat.png'

..\..\..\..\AppData\Local\Programs\Python\Python312\Lib\pathlib.py:1342: PermissionError
=========================== short test summary info ===========================
FAILED scripts/tests/test_s4_analyze.py::test_mediation_hand_values - Permiss...
1 failed, 193 passed in 6.82s
```
