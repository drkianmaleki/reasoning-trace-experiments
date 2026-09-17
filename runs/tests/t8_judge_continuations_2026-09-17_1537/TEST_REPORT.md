# TEST_REPORT — t8_judge_continuations — 2026-09-17 15:37

Test of pipeline step (8/9) (`scripts/s3_judge_continuations.py` over `scripts/s1_judge.py` batch mode), per pipeline v2 Section 9 item 10. Git commit `b5f4a5a9b0526a7bfe2f5b7da65ace8db0066d11`. Smoke folder `runs/tests/t7_resample_2026-09-17_1532/smoke`; judge Sonnet 5 × prompt v3 × thinking low, batch prices. API cost $0.6755.

## Result: PASS (4/4 checks passed)

## Checks

- PASS — check 1, s3 dry run on the smoke folder: documents built, cost projected — collections ['rb_c004']; documents 3, sentences 2204, prefix sentences shown 24; projected cost $0.510 at batch prices (rates 34 thinking + 7 label tokens per sentence, 23.9 text tokens per sentence)
- PASS — check 2, one real batch of three continuation requests: submitted, polled, parsed — valid 3 of 3, failed 0, retry None; cost $0.6755; stopped None
- PASS — check 3, derivation with R1-R4: first new node and block sequence per continuation, pnext written — rb_c004_B00_001: Pl₁¹(3) (Planning, opens True), 77 blocks from the cut; rb_c004_B00_000: Pl₁¹(2) (Planning, opens True), 71 blocks from the cut; rb_c004_B00_002: Pl₁¹(2) (Planning, opens True), 135 blocks from the cut; pnext file pnext_smoke.csv
- PASS — check 4, pytest on scripts/tests — exit code 0; last line: 194 passed in 5.82s

## The three continuations (cut(C-B00), prefix s0-s7 labeled)

| continuation | continuation sentences | first new node | L1 | opens block (rule) | first sentence is Wait | block sequence from the cut |
|---|---|---|---|---|---|---|
| rb_c004_B00_001 | 564 | Pl₁¹(3) | Planning | True (R1) | False | B1 (R1): Pl₁¹(3) Re₁¹ Pl₁² Re₁² Pl₁³ As₁ \| B2 (R1): Pl₂¹(3) Re₂¹ Pl₂² Re₂²(3) Co₂ \| B3 (R1): Pl₃(2) Kn₃(2) Re₃ \| B4 (R4): Pl₄ Rs₄ Kn₄ Re₄ \| B5 (R1): Pl₅¹(3) Rs₅¹(2) Pl₅² Rs₅²(2) Pl₅³ Ex₅¹(2) Re₅¹(3) Pl₅⁴ Ex₅²(2) Re₅²(3) Pl₅⁵ Ex₅³(2) Re₅³(3) Pl₅⁶ Ex₅⁴(2) Re₅⁴(3) \| B6 (R1): Pl₆(2) Rs₆¹ Re₆¹(2) Rs₆² Re₆²(2) Rs₆³ Re₆³ Rs₆⁴ Re₆⁴ Rs₆⁵ Re₆⁵ Rs₆⁶ \| B7 (R1): Pl₇¹(2) Rs₇¹ Re₇¹ Kn₇(2) As₇ Pl₇² Rs₇² Pl₇³ Co₇ Re₇² \| B8 (R1): Pl₈(3) Re₈ \| B9 (R2): As₉ Co₉ \| B10 (R2): As₁₀ Co₁₀ \| B11 (R1): Pl₁₁ Rf₁₁(6) \| B12 (R1): Pl₁₂ Kn₁₂ Re₁₂ \| B13 (R1): Pl₁₃ As₁₃ Kn₁₃ \| B14 (R2): As₁₄ Re₁₄¹(2) Pl₁₄ Ex₁₄(2) R |
| rb_c004_B00_000 | 620 | Pl₁¹(2) | Planning | True (R1) | False | B1 (R1): Pl₁¹(2) Re₁¹(2) Pl₁² Re₁² Pl₁³ Re₁³ Pl₁⁴ Rs₁ \| B2 (R1): Pl₂(2) Kn₂(2) Re₂(2) \| B3 (R1): Pl₃ Rs₃(2) Re₃(2) \| B4 (R1): Pl₄(2) Rs₄(2) Co₄(2) \| B5 (R1): Pl₅¹(4) Rs₅¹ Pl₅² Rs₅² Re₅¹ Pl₅³ Re₅² As₅ Re₅³ Pl₅⁴ \| B6 (R2): As₆ Re₆(3) \| B7 (R2): As₇ Re₇(3) \| B8 (R2): As₈ Re₈(3) \| B9 (R2): As₉ Re₉(3) \| B10 (R1): Pl₁₀(2) Co₁₀ Re₁₀(11) \| B11 (R1): Pl₁₁¹(2) Rs₁₁ Pl₁₁² Kn₁₁ Re₁₁(2) \| B12 (R1): Pl₁₂ Re₁₂(5) \| B13 (R1): Pl₁₃ Re₁₃ \| B14 (R2): As₁₄ Re₁₄ \| B15 (R2): As₁₅ Re₁₅¹(2) Pl₁₅ Re₁₅²(2) Rf₁₅(2) Re₁₅³(2) \| B16 (R1): Pl₁₆¹(2) Kn₁₆(3) Re₁₆¹ Co₁₆ Pl₁₆² Re₁₆²(3) Pl₁₆³ Re₁₆³(4) \| B17 (R1): |
| rb_c004_B00_002 | 1020 | Pl₁¹(2) | Planning | True (R1) | False | B1 (R1): Pl₁¹(2) Re₁¹(2) Pl₁² Re₁² Pl₁³ Re₁³ Pl₁⁴ Rs₁ \| B2 (R1): Pl₂(2) Re₂(2) [Re+Ex]₂ \| B3 (R1): Pl₃¹(2) Kn₃¹(2) Pl₃² Kn₃²(2) Pl₃³(2) Kn₃³ Pl₃⁴ Kn₃⁴ Pl₃⁵ Re₃¹(2) Pl₃⁶ Re₃² \| B4 (R1): Pl₄(2) Rs₄ Re₄(2) Co₄ \| B5 (R1): Pl₅(2) Rf₅(6) \| B6 (R1): Pl₆¹(2) Re₆¹(2) Pl₆² Co₆ Re₆²(4) \| B7 (R1): Pl₇(2) \| B8 (R2): As₈ Re₈¹(2) Rs₈ Re₈²(2) \| B9 (R1): Pl₉ Re₉(2) \| B10 (R1): Pl₁₀¹ Rs₁₀(6) Pl₁₀² Re₁₀¹ Co₁₀ Re₁₀² \| B11 (R1): Pl₁₁¹(2) Kn₁₁¹ Pl₁₁² Rs₁₁ Pl₁₁³ Re₁₁¹ Kn₁₁² Re₁₁² Ex₁₁¹ Re₁₁³ Ex₁₁² Co₁₁ Re₁₁⁴(3) \| B12 (R1): Pl₁₂ Re₁₂(5) \| B13 (R1): Pl₁₃ Re₁₃(3) \| B14 (R1): Pl₁₄ Re₁₄¹ Rs₁₄¹ Re₁₄² Rs₁₄²(2) |

## pytest output

```
........................................................................ [ 37%]
........................................................................ [ 74%]
..................................................                       [100%]
194 passed in 5.82s
```
