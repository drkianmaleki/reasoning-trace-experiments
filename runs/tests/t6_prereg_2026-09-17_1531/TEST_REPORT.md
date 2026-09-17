# TEST_REPORT — t6_prereg — 2026-09-17 15:31

Test of pipeline step (6/9), the pre-registration `docs/shared/2026-09-17_preregistration_stage1_v1.md` (sha256 `4e0dd25876ed6d6c4deab69e0cb32e712842662547bbc81dc419b5e59c341fc5`), per pipeline v2 Section 9 item 8. Git commit `b5f4a5a9b0526a7bfe2f5b7da65ace8db0066d11`. Offline; API cost $0.

## Result: PASS (4/4 checks passed)

## Checks

- PASS — check 1, the registration file is in docs/shared and committed — exists True; commits 1; registration timestamp (earliest commit): b5f4a5a9b0526a7bfe2f5b7da65ace8db0066d11 2026-09-17 14:52:14 -0500 pre-registration of stage one (n=25, 84 prefixes under R4, stopping rule, judge Sonnet 5 x v3 x low, ceilings) â€” registration timestamp; STATE_2026-09-17_2
- PASS — check 2, the cut list of Section 3 items 3-4 equals the block ends derived from listing v4 under R4 and the pinned lists — text C 46 / E 37 indices; derived C 46 / E 37; equal True; C first/last s[7]…s[373], E s[11]…s[250]
- PASS — check 3, n, n_0, the ceilings and the stopping rule are stated — n = 25: present; n_0 = 100: present; DeepInfra ceiling $45: present; Claude ceiling $80: present; stopping rule: present; denominator: present
- PASS — check 4, pytest on scripts/tests — exit code 0; last line: 194 passed in 6.02s

## git log of the registration file

```
b5f4a5a9b0526a7bfe2f5b7da65ace8db0066d11 2026-09-17 14:52:14 -0500 pre-registration of stage one (n=25, 84 prefixes under R4, stopping rule, judge Sonnet 5 x v3 x low, ceilings) â€” registration timestamp; STATE_2026-09-17_2
```

## pytest output

```
........................................................................ [ 37%]
........................................................................ [ 74%]
..................................................                       [100%]
194 passed in 6.02s
```
