# Judge comparison 2x2 — prompt v1/v2 x Haiku 4.5/Sonnet 5 — 2026-09-17 00:15

Reviewed labels: docs/shared/2026-09-16_source_traces_labeled_v3.md. Exact-match rate on label sets, kappa on the primary label (reviewed as reference). Judge blocks and nodes from the derivation on the judge's labels, against the reviewed 46/193 (c004) and 37/146 (e036).

Cells:

- haiku × v1: `runs/experiments/judge_source_2026-09-16_2347` (model echoed claude-haiku-4-5-20251001, prompt judge_prompt_v1.md)
- haiku × v2: `runs/experiments/judge_source_haiku_v2_2026-09-17_0012` (model echoed {'e036': 'claude-haiku-4-5-20251001', 'c004': 'claude-haiku-4-5-20251001'}, prompt judge_prompt_v2.md)
- sonnet × v1: `runs/experiments/judge_source_sonnet_v1_2026-09-17_0008` (model echoed {'e036': 'claude-sonnet-5', 'c004': 'claude-sonnet-5'}, prompt judge_prompt_v1.md)
- sonnet × v2: `runs/experiments/judge_source_sonnet_v2_2026-09-17_0012` (model echoed {'e036': 'claude-sonnet-5', 'c004': 'claude-sonnet-5'}, prompt judge_prompt_v2.md)

## C-trace c004 (375 sentences)

| cell | L1 exact | L1 kappa | L2 exact | L2 kappa | L3 exact | L3 kappa | blocks (reviewed) | nodes (reviewed) | attempts | cost |
|---|---|---|---|---|---|---|---|---|---|---|
| haiku × v1 | 0.445 | 0.122 | 0.219 | 0.155 | 0.197 | 0.155 | 14 (46) | 45 (193) | 1 | $0.0121 |
| haiku × v2 | 0.507 | 0.192 | 0.251 | 0.188 | 0.184 | 0.144 | 5 (46) | 41 (193) | 1 | $0.0119 |
| sonnet × v1 | 0.747 | 0.662 | 0.579 | 0.556 | 0.571 | 0.557 | 40 (46) | 202 (193) | 2 | $0.1722 |
| sonnet × v2 | 0.811 | 0.764 | 0.648 | 0.632 | 0.635 | 0.624 | 46 (46) | 195 (193) | 2 | $0.1637 |

## E-trace e036 (254 sentences)

| cell | L1 exact | L1 kappa | L2 exact | L2 kappa | L3 exact | L3 kappa | blocks (reviewed) | nodes (reviewed) | attempts | cost |
|---|---|---|---|---|---|---|---|---|---|---|
| haiku × v1 | 0.539 | 0.433 | 0.346 | 0.317 | 0.331 | 0.309 | 20 (37) | 80 (146) | 1 | $0.0163 |
| haiku × v2 | 0.535 | 0.422 | 0.362 | 0.328 | 0.319 | 0.289 | 15 (37) | 49 (146) | 1 | $0.0149 |
| sonnet × v1 | 0.791 | 0.746 | 0.661 | 0.641 | 0.634 | 0.617 | 37 (37) | 152 (146) | 2 | $0.1563 |
| sonnet × v2 | 0.858 | 0.830 | 0.807 | 0.800 | 0.787 | 0.782 | 33 (37) | 157 (146) | 2 | $0.1607 |

## Pooled (629 sentences)

| cell | L1 exact | L1 kappa | L2 exact | L2 kappa | L3 exact | L3 kappa | blocks (reviewed) | nodes (reviewed) | attempts | cost |
|---|---|---|---|---|---|---|---|---|---|---|
| haiku × v1 | 0.483 | 0.288 | 0.270 | 0.228 | 0.251 | 0.223 | 34 (83) | 125 (339) | 1+1 | $0.0283 |
| haiku × v2 | 0.518 | 0.336 | 0.296 | 0.254 | 0.238 | 0.210 | 20 (83) | 90 (339) | 1+1 | $0.0269 |
| sonnet × v1 | 0.765 | 0.707 | 0.612 | 0.593 | 0.596 | 0.583 | 77 (83) | 354 (339) | 2+2 | $0.3285 |
| sonnet × v2 | 0.830 | 0.796 | 0.712 | 0.701 | 0.696 | 0.689 | 79 (83) | 352 (339) | 2+2 | $0.3243 |

## Confusion classes per cell (pooled over both traces; reviewed → judge on the Level 2 primary label; option evaluation as n_judge vs n_reviewed of the Level 2 label set)

| class | haiku × v1 | haiku × v2 | sonnet × v1 | sonnet × v2 |
|---|---|---|---|---|
| global plan -> local plan | 26 | 12 | 21 | 0 |
| rephrasing an earlier sentence -> anything else | 70 | 54 | 63 | 25 |
| branching -> anything else | 5 | 5 | 2 | 2 |
| option evaluation n_judge vs n_reviewed | 213 vs 45 | 108 vs 45 | 89 vs 45 | 69 vs 45 |
| meta-evaluation -> emotion or impression | 12 | 0 | 0 | 1 |
| announce output -> emotion or impression | 9 | 0 | 0 | 0 |

## Ten most frequent Level 2 confusions, haiku × v1 (reviewed → judge, primary label, pooled)

| reviewed | judge | count |
|---|---|---|
| Restatement > rephrasing an earlier sentence | Reasoning > option evaluation | 39 |
| Planning > local plan | Reasoning > option evaluation | 38 |
| Planning > global plan | Planning > local plan | 26 |
| Restatement > rephrasing an earlier sentence | Reasoning > logical reasoning | 22 |
| Reasoning > speculation | Reasoning > option evaluation | 19 |
| Reflection > meta-evaluation of a step | Reasoning > option evaluation | 16 |
| Conclusion > intermediate conclusion | Reasoning > option evaluation | 13 |
| Reflection > meta-evaluation of a step | Reflection > emotion or impression | 12 |
| Reasoning > logical reasoning | Reasoning > calculation | 10 |
| Example > non-exhaustive listing | Reasoning > logical reasoning | 10 |

## Ten most frequent Level 2 confusions, haiku × v2 (reviewed → judge, primary label, pooled)

| reviewed | judge | count |
|---|---|---|
| Restatement > rephrasing an earlier sentence | Reasoning > logical reasoning | 40 |
| Reasoning > speculation | Reasoning > logical reasoning | 23 |
| Planning > local plan | Reasoning > logical reasoning | 19 |
| Planning > local plan | Planning > global plan | 19 |
| Planning > local plan | Reasoning > calculation | 17 |
| Reflection > meta-evaluation of a step | Reasoning > option evaluation | 14 |
| Planning > global plan | Planning > local plan | 12 |
| Reasoning > logical reasoning | Reasoning > calculation | 12 |
| Reasoning > hedge word analysis | Reasoning > option evaluation | 11 |
| Planning > initiate verification | Reasoning > logical reasoning | 11 |

## Ten most frequent Level 2 confusions, sonnet × v1 (reviewed → judge, primary label, pooled)

| reviewed | judge | count |
|---|---|---|
| Planning > global plan | Planning > local plan | 21 |
| Reflection > meta-evaluation of a step | Reasoning > option evaluation | 13 |
| Reasoning > calculation | Reasoning > logical reasoning | 12 |
| Restatement > rephrasing an earlier sentence | Example > non-exhaustive listing | 12 |
| Reasoning > speculation | Reasoning > option evaluation | 11 |
| Restatement > rephrasing an earlier sentence | Knowledge > world knowledge | 10 |
| Reasoning > hedge word analysis | Reasoning > option evaluation | 9 |
| Restatement > rephrasing an earlier sentence | Reasoning > defining symbols | 9 |
| Restatement > rephrasing an earlier sentence | Reasoning > logical reasoning | 9 |
| Planning > local plan | Restatement > rephrasing the prompt | 6 |

## Ten most frequent Level 2 confusions, sonnet × v2 (reviewed → judge, primary label, pooled)

| reviewed | judge | count |
|---|---|---|
| Reasoning > calculation | Reasoning > logical reasoning | 15 |
| Restatement > rephrasing an earlier sentence | Example > non-exhaustive listing | 12 |
| Reasoning > logical reasoning | Conclusion > intermediate conclusion | 11 |
| Reasoning > speculation | Reasoning > option evaluation | 11 |
| Reasoning > hedge word analysis | Reasoning > option evaluation | 8 |
| Reasoning > option evaluation | Conclusion > intermediate conclusion | 7 |
| Planning > local plan | Restatement > rephrasing the prompt | 6 |
| Planning > initiate backtracking | Planning > initiate verification | 6 |
| Reasoning > defining symbols | Restatement > rephrasing an earlier sentence | 6 |
| Restatement > rephrasing an earlier sentence | Conclusion > intermediate conclusion | 6 |

