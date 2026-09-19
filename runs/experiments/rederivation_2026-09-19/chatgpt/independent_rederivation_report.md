# Independent re-derivation and scoring audit

**Input:** `continuations.jsonl` (625 original JSONL records); analysis instructions: `Pasted markdown.md`.
**Output generated:** 2026-09-19; independent script: `independent_rederivation.py`.

## What is and is not verified

The raw JSONL contains 625 distinct IDs across 22 expected groups (no-think: 100; cut-0: 25; C: 12 × 25; E: 8 × 25). Each group has all sequence indices from zero through n−1 without repetition, a single identical prompt, and a single identical prompt-token count. The `think_closed` flag agrees with the `</think>` delimiter for cut continuations; no-think records have completed replies without that delimiter. No `answer` or `chosen` fields were used. All category counts in each row sum to its original denominator.

**Unavailable original files:** `pcut.csv`, `stage1_summary.md`, the full preregistration, the original analysis script, and the mediation tables were not supplied. Thus this audit does *not* claim agreement with those files or validate preregistered choices beyond the supplied markdown.

## Scoring rules specified before looking at discrepancies

- **Pass A:** singleton letter A–F in original `letters` counts as the answer; empty/multiple values are `?`. Unresolved values remain in the denominator.
- **Pass B:** use only the explicit answer in the last nonblank line of a **completed** (`finish="stop"`) reply. Accept `Answer: X`, `Answer: (X)`, or `Therefore, Answer: X.` (case-insensitive; tolerates simple bold formatting). For no-think, the full text is the reply; for other conditions, use the text after the first `</think>`. A continuation with `finish="length"` is `?` regardless of any provisional thought-stage answer. Never infer a final letter from ordinary discussion of the options. All 25 (or 100) records remain in each denominator.

The Pass B rule measures completed final answers, not the last provisional answer in truncated reasoning. This is a substantive estimand change relative to Pass A. Pre-registration deviation must be disclosed if Pass B is used in the paper.

## All 22 answer-count rows

The vector order is **[A, B, C, D, E, F, ?]**; every row has n=25 except no-think (n=100).

| Group | Original `letters` (Pass A) | Completed answers (Pass B) |
|:--|:--|:--|
| no-think | 32, 0, 49, 0, 19, 0, 0 | 32, 0, 49, 0, 19, 0, 0 |
| cut-0 | 0, 2, 4, 0, 18, 0, 1 | 0, 0, 3, 0, 18, 0, 4 |
| C-B00 | 1, 1, 16, 0, 2, 0, 5 | 0, 0, 12, 0, 1, 0, 12 |
| C-B01 | 1, 0, 9, 0, 8, 0, 7 | 0, 0, 7, 0, 8, 0, 10 |
| C-B02 | 0, 0, 14, 0, 6, 0, 5 | 0, 0, 13, 0, 6, 0, 6 |
| C-B03 | 0, 1, 11, 0, 8, 0, 5 | 0, 0, 6, 0, 8, 0, 11 |
| C-B04 | 0, 0, 7, 0, 11, 0, 7 | 0, 0, 4, 0, 11, 0, 10 |
| C-B05 | 1, 0, 7, 0, 8, 0, 9 | 0, 0, 6, 0, 8, 0, 11 |
| C-B06 | 0, 0, 17, 1, 2, 0, 5 | 0, 0, 15, 0, 2, 0, 8 |
| C-B07 | 0, 1, 12, 0, 3, 0, 9 | 0, 0, 10, 0, 3, 0, 12 |
| C-B08 | 0, 0, 10, 0, 8, 1, 6 | 0, 0, 10, 0, 8, 0, 7 |
| C-B09 | 0, 0, 24, 0, 0, 0, 1 | 0, 0, 25, 0, 0, 0, 0 |
| C-B10 | 0, 0, 24, 0, 0, 0, 1 | 0, 0, 25, 0, 0, 0, 0 |
| C-B11 | 0, 0, 25, 0, 0, 0, 0 | 0, 0, 25, 0, 0, 0, 0 |
| E-B00 | 0, 0, 1, 0, 24, 0, 0 | 0, 0, 1, 0, 24, 0, 0 |
| E-B01 | 0, 0, 5, 0, 20, 0, 0 | 0, 0, 5, 0, 20, 0, 0 |
| E-B02 | 1, 0, 10, 0, 14, 0, 0 | 1, 0, 10, 0, 14, 0, 0 |
| E-B03 | 0, 0, 5, 0, 20, 0, 0 | 0, 0, 5, 0, 20, 0, 0 |
| E-B04 | 0, 0, 1, 0, 24, 0, 0 | 0, 0, 1, 0, 24, 0, 0 |
| E-B05 | 0, 0, 6, 0, 19, 0, 0 | 0, 0, 6, 0, 19, 0, 0 |
| E-B06 | 0, 0, 0, 0, 24, 1, 0 | 0, 0, 0, 0, 24, 1, 0 |
| E-B07 | 0, 0, 0, 0, 25, 0, 0 | 0, 0, 0, 0, 25, 0, 0 |

## Baseline proportions and Wilson 95% intervals

| Pass | Baseline | Letter | k/n | p̂ | Wilson 95% |
|:--|:--|:--|:--|--:|:--|
| A | no-think | C | 49/100 | 0.4900 | [0.3942, 0.5865] |
| A | no-think | E | 19/100 | 0.1900 | [0.1251, 0.2778] |
| A | no-think | A | 32/100 | 0.3200 | [0.2367, 0.4166] |
| A | cut-0 | C | 4/25 | 0.1600 | [0.0640, 0.3465] |
| A | cut-0 | E | 18/25 | 0.7200 | [0.5242, 0.8572] |
| A | cut-0 | A | 0/25 | 0.0000 | [0.0000, 0.1332] |
| B | no-think | C | 49/100 | 0.4900 | [0.3942, 0.5865] |
| B | no-think | E | 19/100 | 0.1900 | [0.1251, 0.2778] |
| B | no-think | A | 32/100 | 0.3200 | [0.2367, 0.4166] |
| B | cut-0 | C | 3/25 | 0.1200 | [0.0417, 0.2996] |
| B | cut-0 | E | 18/25 | 0.7200 | [0.5242, 0.8572] |
| B | cut-0 | A | 0/25 | 0.0000 | [0.0000, 0.1332] |

## Every per-cut estimate and successive difference

For each trace the success letter is C or E respectively. At block 0, the previous group is shared cut-0; later, it is the preceding block. The p̂ interval is Wilson and the Δ interval is independent-sample Newcombe method 10. These are *pointwise*, not simultaneous, intervals.

| Pass | Block | k/25 | p̂ (Wilson 95%) | Δ (Newcombe 95%) |
|:--|:--|--:|:--|:--|
| A | C-B00 | 16/25 | 0.6400 [0.4452, 0.7975] | +0.48 [0.2103, 0.6645] |
| A | C-B01 | 9/25 | 0.3600 [0.2025, 0.5548] | -0.28 [-0.5028, -0.0045] |
| A | C-B02 | 14/25 | 0.5600 [0.3707, 0.7333] | +0.20 [-0.0717, 0.4342] |
| A | C-B03 | 11/25 | 0.4400 [0.2667, 0.6293] | -0.12 [-0.3651, 0.1477] |
| A | C-B04 | 7/25 | 0.2800 [0.1428, 0.4758] | -0.16 [-0.3938, 0.1015] |
| A | C-B05 | 7/25 | 0.2800 [0.1428, 0.4758] | +0.00 [-0.2390, 0.2390] |
| A | C-B06 | 17/25 | 0.6800 [0.4841, 0.8279] | +0.40 [0.1231, 0.6017] |
| A | C-B07 | 12/25 | 0.4800 [0.3003, 0.6650] | -0.20 [-0.4328, 0.0695] |
| A | C-B08 | 10/25 | 0.4000 [0.2340, 0.5926] | -0.08 [-0.3285, 0.1834] |
| A | C-B09 | 24/25 | 0.9600 [0.8046, 0.9929] | +0.56 [0.3125, 0.7292] |
| A | C-B10 | 24/25 | 0.9600 [0.8046, 0.9929] | +0.00 [-0.1589, 0.1589] |
| A | C-B11 | 25/25 | 1.0000 [0.8668, 1.0000] | +0.04 [-0.0972, 0.1954] |
| A | E-B00 | 24/25 | 0.9600 [0.8046, 0.9929] | +0.24 [0.0327, 0.4385] |
| A | E-B01 | 20/25 | 0.8000 [0.6087, 0.9114] | -0.16 [-0.3541, 0.0312] |
| A | E-B02 | 14/25 | 0.5600 [0.3707, 0.7333] | -0.24 [-0.4597, 0.0182] |
| A | E-B03 | 20/25 | 0.8000 [0.6087, 0.9114] | +0.24 [-0.0182, 0.4597] |
| A | E-B04 | 24/25 | 0.9600 [0.8046, 0.9929] | +0.16 [-0.0312, 0.3541] |
| A | E-B05 | 19/25 | 0.7600 [0.5657, 0.8850] | -0.20 [-0.3971, -0.0005] |
| A | E-B06 | 24/25 | 0.9600 [0.8046, 0.9929] | +0.20 [0.0005, 0.3971] |
| A | E-B07 | 25/25 | 1.0000 [0.8668, 1.0000] | +0.04 [-0.0972, 0.1954] |
| B | C-B00 | 12/25 | 0.4800 [0.3003, 0.6650] | +0.36 [0.1060, 0.5609] |
| B | C-B01 | 7/25 | 0.2800 [0.1428, 0.4758] | -0.20 [-0.4303, 0.0657] |
| B | C-B02 | 13/25 | 0.5200 [0.3350, 0.6997] | +0.24 [-0.0294, 0.4661] |
| B | C-B03 | 6/25 | 0.2400 [0.1150, 0.4343] | -0.28 [-0.4989, -0.0117] |
| B | C-B04 | 4/25 | 0.1600 [0.0640, 0.3465] | -0.08 [-0.2967, 0.1446] |
| B | C-B05 | 6/25 | 0.2400 [0.1150, 0.4343] | +0.08 [-0.1446, 0.2967] |
| B | C-B06 | 15/25 | 0.6000 [0.4074, 0.7660] | +0.36 [0.0864, 0.5678] |
| B | C-B07 | 10/25 | 0.4000 [0.2340, 0.5926] | -0.20 [-0.4347, 0.0724] |
| B | C-B08 | 10/25 | 0.4000 [0.2340, 0.5926] | +0.00 [-0.2542, 0.2542] |
| B | C-B09 | 25/25 | 1.0000 [0.8668, 1.0000] | +0.60 [0.3658, 0.7660] |
| B | C-B10 | 25/25 | 1.0000 [0.8668, 1.0000] | +0.00 [-0.1332, 0.1332] |
| B | C-B11 | 25/25 | 1.0000 [0.8668, 1.0000] | +0.00 [-0.1332, 0.1332] |
| B | E-B00 | 24/25 | 0.9600 [0.8046, 0.9929] | +0.24 [0.0327, 0.4385] |
| B | E-B01 | 20/25 | 0.8000 [0.6087, 0.9114] | -0.16 [-0.3541, 0.0312] |
| B | E-B02 | 14/25 | 0.5600 [0.3707, 0.7333] | -0.24 [-0.4597, 0.0182] |
| B | E-B03 | 20/25 | 0.8000 [0.6087, 0.9114] | +0.24 [-0.0182, 0.4597] |
| B | E-B04 | 24/25 | 0.9600 [0.8046, 0.9929] | +0.16 [-0.0312, 0.3541] |
| B | E-B05 | 19/25 | 0.7600 [0.5657, 0.8850] | -0.20 [-0.3971, -0.0005] |
| B | E-B06 | 24/25 | 0.9600 [0.8046, 0.9929] | +0.20 [0.0005, 0.3971] |
| B | E-B07 | 25/25 | 1.0000 [0.8668, 1.0000] | +0.04 [-0.0972, 0.1954] |

## Largest shifts, first all-target cut, and bootstrap gaps

| Pass / trace | First all-target cut M | First / second / third shifts | Ranked gap (95% percentile bootstrap) | Signed, named-block contrast (95% percentile bootstrap) |
|:--|:--|:--|:--|:--|
| A / c004 | B11 | B09 +0.56, B00 +0.48, B06 +0.40 | 0.0800 [0.0000, 0.3200] | B09 − B00: +0.08 [-0.2400, 0.4000] |
| A / e036 | B07 | B00 +0.24, B03 +0.24, B06 +0.20 | 0.0000 [0.0000, 0.2800] | B00 − B03: +0.00 [-0.3200, 0.3200] |
| B / c004 | B09 | B09 +0.60, B00 +0.36, B06 +0.36 | 0.2400 [0.0000, 0.4000] | B09 − B00: +0.24 [-0.0800, 0.5200] |
| B / e036 | B07 | B00 +0.24, B03 +0.24, B06 +0.20 | 0.0000 [0.0000, 0.2800] | B00 − B03: +0.00 [-0.3200, 0.3200] |

Each bootstrap replicate separately resamples all 25 categorical answers of cut-0 and all 25 answers at every sampled cut, then recomputes every difference and re-ranks all shifts before computing largest minus second-largest. 10,000 replicates, NumPy `default_rng(0)`, percentile 2.5 and 97.5, preserving `?`. The named-block contrast is exploratory; it *does not* re-rank in each resample. In E, the named contrast is B00 − B03; in C it is B09 − B00.

**Monte Carlo stability:** Alternate seeds 1 and 20260919 and a 100,000-replicate seed-0 run give the same displayed gap interval endpoints in all four trace/pass combinations except corrected C with seed 20260919: upper endpoint 0.44 instead of 0.40. Therefore the corrected C upper endpoint has at least one 0.04-grid-step of Monte Carlo variation at 10,000 draws.

### Descriptive movement

| Pass / trace | Cut-0 → final target p̂ | Total change | Trivial shifts | Sum of top 1 / 2 / 3 shifts ÷ total movement |
|:--|:--|--:|--:|:--|
| A / c004 | 4/25 → 25/25 | +0.84 | 2 | 0.667 / 1.238 / 1.714 |
| A / e036 | 18/25 → 25/25 | +0.28 | 0 | 0.857 / 1.714 / 2.429 |
| B / c004 | 3/25 → 25/25 | +0.88 | 3 | 0.682 / 1.091 / 1.500 |
| B / e036 | 18/25 → 25/25 | +0.28 | 0 | 0.857 / 1.714 / 2.429 |

## Every disagreement with original `letters`

There are **36 disagreements**: 33 length-limited continuations with a single original letter changed to unresolved, plus 3 completed C replies previously scored unresolved because the final answer is parenthesized. The additional 9 length-limited records with `["D", "E"]` already count as unresolved in both passes and are **not** disagreements. Seven length-limited replies that closed thinking but never finished their reply are also unresolved in both passes.

| Record ID | Group | Original → independent | Evidence for independent reading |
|:--|:--|:--|:--|
| `rb_c004_B00_003` | C-B00 | A → ? | Length limit; no completed final reply |
| `rb_c004_B00_004` | C-B00 | C → ? | Length limit; no completed final reply |
| `rb_c004_B00_015` | C-B00 | C → ? | Length limit; no completed final reply |
| `rb_c004_B00_016` | C-B00 | C → ? | Length limit; no completed final reply |
| `rb_c004_B00_018` | C-B00 | E → ? | Length limit; no completed final reply |
| `rb_c004_B00_021` | C-B00 | B → ? | Length limit; no completed final reply |
| `rb_c004_B00_022` | C-B00 | C → ? | Length limit; no completed final reply |
| `rb_c004_B01_002` | C-B01 | C → ? | Length limit; no completed final reply |
| `rb_c004_B01_008` | C-B01 | A → ? | Length limit; no completed final reply |
| `rb_c004_B01_020` | C-B01 | C → ? | Length limit; no completed final reply |
| `rb_c004_B02_008` | C-B02 | C → ? | Length limit; no completed final reply |
| `rb_c004_B02_015` | C-B02 | C → ? | Length limit; no completed final reply |
| `rb_c004_B02_023` | C-B02 | ? → C | Completed reply ends `Answer: (C)` |
| `rb_c004_B03_003` | C-B03 | C → ? | Length limit; no completed final reply |
| `rb_c004_B03_006` | C-B03 | C → ? | Length limit; no completed final reply |
| `rb_c004_B03_010` | C-B03 | C → ? | Length limit; no completed final reply |
| `rb_c004_B03_011` | C-B03 | B → ? | Length limit; no completed final reply |
| `rb_c004_B03_015` | C-B03 | C → ? | Length limit; no completed final reply |
| `rb_c004_B03_020` | C-B03 | C → ? | Length limit; no completed final reply |
| `rb_c004_B04_001` | C-B04 | C → ? | Length limit; no completed final reply |
| `rb_c004_B04_012` | C-B04 | C → ? | Length limit; no completed final reply |
| `rb_c004_B04_022` | C-B04 | C → ? | Length limit; no completed final reply |
| `rb_c004_B05_000` | C-B05 | A → ? | Length limit; no completed final reply |
| `rb_c004_B05_023` | C-B05 | C → ? | Length limit; no completed final reply |
| `rb_c004_B06_018` | C-B06 | D → ? | Length limit; no completed final reply |
| `rb_c004_B06_019` | C-B06 | C → ? | Length limit; no completed final reply |
| `rb_c004_B06_023` | C-B06 | C → ? | Length limit; no completed final reply |
| `rb_c004_B07_014` | C-B07 | C → ? | Length limit; no completed final reply |
| `rb_c004_B07_016` | C-B07 | B → ? | Length limit; no completed final reply |
| `rb_c004_B07_020` | C-B07 | C → ? | Length limit; no completed final reply |
| `rb_c004_B08_015` | C-B08 | F → ? | Length limit; no completed final reply |
| `rb_c004_B09_017` | C-B09 | ? → C | Completed reply ends `Answer: (C)` |
| `rb_c004_B10_012` | C-B10 | ? → C | Completed reply ends `Answer: (C)` |
| `rb_cut0_017` | cut-0 | B → ? | Length limit; no completed final reply |
| `rb_cut0_020` | cut-0 | B → ? | Length limit; no completed final reply |
| `rb_cut0_021` | cut-0 | C → ? | Length limit; no completed final reply |

## Precision, validity, and interpretation

1. **Arithmetic.** Use z = 1.959964 for Wilson score intervals; construct Newcombe method 10 for p₁ − p₂ from the two Wilson intervals. The code independently matched `statsmodels` 0.14.6 for **40 Wilson and 40 Newcombe intervals**, with maximum absolute numerical discrepancies 1.82×10⁻⁹ and 2.23×10⁻⁹, respectively (the tiny difference follows z rounding). Example: C-B00 original p̂ = 16/25 = 0.64, Wilson [0.445185, 0.797521]; its shift relative to C=4/25 at cut-0 is +0.48, Newcombe [0.210280, 0.664451].
2. **Stopping rule change.** Original C first reaches all 25 C at B11 (B09 and B10 each score 24/25). Corrected C already reaches all 25 at **B09** and remains at 25/25 at B10 and B11. The corrected *first all-C cut* is B09, but the observed dataset has two subsequent cuts: it was collected under original scoring. The E first all-E cut is B07 in both passes.
3. **Selection and uncertainty.** The ranked gap is mathematically nonnegative under all resamples and is not a signed test statistic. A percentile interval touching zero cannot independently establish either uniqueness or lack of uniqueness of a named top block; the signed B09−B00 C contrast crosses zero under both scoring rules. The pointwise Wilson/Newcombe intervals do not correct for multiple examined cuts or the sequential, data-dependent stopping rule.
4. **Sampling independence is an assumption.** Newcombe assumes independently sampled proportions; unique sequence indices and separate records do not prove random draws were independent. The JSONL does not by itself establish distinct sampler random seeds or full experimental provenance.
5. **No causal block attribution from these summaries alone.** These conditional continuation frequencies and adjacent differences describe associations across successively longer prefixes. A claim that a block *caused* a shift requires the research design and assumptions separately. No judge, mediation outcomes, or external scores were included here.
6. **Recommendation on scoring as an analysis convention (not a retroactive preregistration claim):** If the response variable is the letter in the completed user-facing answer, use Pass B and separately report the original Pass A as preregistered/scorer-implemented sensitivity. An unfinished internal draft is not a completed answer. Accept parenthesized final letters or explicitly declare that the instrument is strictly format-compliance-scored; avoid silently treating `Answer: (C)` as missing while treating a truncated thought-stage `Answer: C` as final. State how this change affects the stopping rule, and pre-specify the corrected rule before any future independent replication.

## Bibliographic and implementation cross-check

- Wilson, E. B. (1927), *Probable Inference, the Law of Succession, and Statistical Inference*, *Journal of the American Statistical Association* 22(158):209–212. https://doi.org/10.1080/01621459.1927.10502953
- Newcombe, R. G. (1998), *Interval estimation for the difference between independent proportions: comparison of eleven methods*, *Statistics in Medicine* 17(8):873–890. https://pubmed.ncbi.nlm.nih.gov/9595617/
- Statsmodels independent-sample confidence-interval API: https://www.statsmodels.org/dev/generated/statsmodels.stats.proportion.confint_proportions_2indep.html

## Reproduce

Put `independent_rederivation.py` next to the original `continuations.jsonl`; run `python independent_rederivation.py` in an environment with NumPy. It recreates `counts_side_by_side.csv`, `baseline_statistics.csv`, `per_cut_statistics.csv`, `trace_summaries.csv`, and `scoring_disagreements.csv`. No internet access, original result tables, or scorer-generated summary fields are required.
