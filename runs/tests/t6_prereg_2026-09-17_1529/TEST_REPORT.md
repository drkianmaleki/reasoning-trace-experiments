# TEST_REPORT — t6_prereg — 2026-09-17 15:29

Test of pipeline step (6/9), the pre-registration `docs/shared/2026-09-17_preregistration_stage1_v1.md` (sha256 `4e0dd25876ed6d6c4deab69e0cb32e712842662547bbc81dc419b5e59c341fc5`), per pipeline v2 Section 9 item 8. Git commit `b5f4a5a9b0526a7bfe2f5b7da65ace8db0066d11`. Offline; API cost $0.

## Result: FAIL (3/4 checks passed)

## Checks

- PASS — check 1, the registration file is in docs/shared and committed — exists True; commits 1; registration timestamp (earliest commit): b5f4a5a9b0526a7bfe2f5b7da65ace8db0066d11 2026-09-17 14:52:14 -0500 pre-registration of stage one (n=25, 84 prefixes under R4, stopping rule, judge Sonnet 5 x v3 x low, ceilings) â€” registration timestamp; STATE_2026-09-17_2
- PASS — check 2, the cut list of Section 3 items 3-4 equals the block ends derived from listing v4 under R4 and the pinned lists — text C 46 / E 37 indices; derived C 46 / E 37; equal True; C first/last s[7]…s[373], E s[11]…s[250]
- PASS — check 3, n, n_0, the ceilings and the stopping rule are stated — n = 25: present; n_0 = 100: present; DeepInfra ceiling $45: present; Claude ceiling $80: present; stopping rule: present; denominator: present
- FAIL — check 4, pytest on scripts/tests — exit code 1; last line: 3 failed, 191 passed, 2 warnings in 6.63s

## git log of the registration file

```
b5f4a5a9b0526a7bfe2f5b7da65ace8db0066d11 2026-09-17 14:52:14 -0500 pre-registration of stage one (n=25, 84 prefixes under R4, stopping rule, judge Sonnet 5 x v3 x low, ceilings) â€” registration timestamp; STATE_2026-09-17_2
```

## pytest output

```
........................................................................ [ 37%]
........................................................................ [ 74%]
...............FF..............F..................                       [100%]
================================== FAILURES ===================================
____________________ test_collections_split_and_projection ____________________

tmp_path = WindowsPath('C:/Users/kianu/AppData/Local/Temp/pytest-of-kianu/pytest-51/test_collections_split_and_pro0')

    def test_collections_split_and_projection(tmp_path):
        run = write_run(tmp_path / "run")
        recs, pcut = S3.load_run(run)
        assert len(recs) == 4 and len(pcut) == 3  # the no-think record is not a continuation to label
        colls = S3.collections_of(recs)
        assert set(colls) == {"rb_cut0", "rb_c004"} and len(colls["rb_c004"]) == 3
        path, meta, n_sent = S3.split_collection("rb_c004", colls["rb_c004"], tmp_path)
        rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]
>       assert n_sent == 2 + 2 + 3 and all("think_end" in r for r in rows)
E       assert (9 == ((2 + 2) + 3))

scripts\tests\test_s3_judge_continuations.py:52: AssertionError
_______________________ test_run_dry_and_real_with_stub _______________________

tmp_path = WindowsPath('C:/Users/kianu/AppData/Local/Temp/pytest-of-kianu/pytest-51/test_run_dry_and_real_with_stu0')

    def test_run_dry_and_real_with_stub(tmp_path):
        run = write_run(tmp_path / "run")
        d = S3.run(run, tmp_path / "dry", dry_run=True, log=lambda s: None)
        assert d["dry_run"] and set(d["collections"]) == {"rb_cut0", "rb_c004"} and d["projection"]["total_cost_est_usd"] >= 0
        req = json.loads((tmp_path / "dry" / "rb_c004" / "requests" / "rb_c004_B00_000.json").read_text(encoding="utf-8"))
        msg = req["messages"][0]["content"]
        assert "a prefix of 8 sentences" in msg.split("\n")[0] and msg.split("\n")[2].startswith("s0: Here's a thinking process") and "\nc0: Wait, re-read.\n" in msg
        client = stub_client(lambda cid, attempt: ("succeeded", REPLIES[cid]))
        s = S3.run(run, tmp_path / "judge", client=client, log=lambda s: None, noise_cuts={"c004": 0}, sleep=lambda x: None)
>       assert s["collections"]["rb_c004"]["valid"] == 3 and s["collections"]["rb_cut0"]["valid"] == 1 and s.get("stopped") is None
E       assert (2 == 3)

scripts\tests\test_s3_judge_continuations.py:69: AssertionError
___________________________ test_wilson_hand_values ___________________________

    def test_wilson_hand_values():
        # k = 21, n = 25, z = 1.959964: p = 0.84; centre = (0.84 + 0.076830)/1.153664 = 0.79471;
        # half = 1.959964 * sqrt(0.84*0.16/25 + z^2/(4*625)) / 1.153664 = 1.959964 * sqrt(0.005376 + 0.0015366)/1.153664 = 0.14126
        lo, hi = ST.wilson(21, 25)
        assert lo == pytest.approx(0.6535, abs=2e-4) and hi == pytest.approx(0.9360, abs=2e-4)
        # P_hat = 1 at n = 25: centre = (1 + z^2/50)/(1 + z^2/25) = 1.076830/1.153664 = 0.93340, half = (z^2/50)/1.153664 = 0.06660 -> 0.8668
        assert ST.wilson(25, 25) == pytest.approx((0.8668, 1.0), abs=2e-4)
        assert ST.wilson(0, 25)[0] == 0.0 and ST.wilson(0, 25)[1] == pytest.approx(0.1332, abs=2e-4)  # 1 - 0.8668, by symmetry
        assert all(math.isnan(x) for x in ST.wilson(0, 0))
        lo1, _ = ST.wilson(25, 25, z=1.644854)  # one-sided 95% lower bound: 0.887 (registration 3.6)
>       assert lo1 == pytest.approx(0.887, abs=2e-3)
E       assert 0.9023464540243974 == 0.887 ± 0.002
E         
E         comparison failed
E         Obtained: 0.9023464540243974
E         Expected: 0.887 ± 0.002

scripts\tests\test_stats_utils.py:25: AssertionError
============================== warnings summary ===============================
scripts/tests/test_s4_analyze.py::test_mediation_hand_values
  C:\Users\kianu\Dropbox\Projects\Ongoing\reasoning-trace-experiments\scripts\s4_analyze.py:479: RuntimeWarning: Mean of empty slice
    mean_py = float(np.nanmean([r["p_Y_source"] for r in ps]))

scripts/tests/test_s4_analyze.py::test_mediation_hand_values
  C:\Users\kianu\Dropbox\Projects\Ongoing\reasoning-trace-experiments\scripts\s4_analyze.py:480: RuntimeWarning: Mean of empty slice
    mean_open = float(np.nanmean([r["opens_where_source_did"] for r in ps if r["source_opens"]])) if any(r["source_opens"] for r in ps) else float("nan")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED scripts/tests/test_s3_judge_continuations.py::test_collections_split_and_projection
FAILED scripts/tests/test_s3_judge_continuations.py::test_run_dry_and_real_with_stub
FAILED scripts/tests/test_stats_utils.py::test_wilson_hand_values - assert 0....
3 failed, 191 passed, 2 warnings in 6.63s
```
