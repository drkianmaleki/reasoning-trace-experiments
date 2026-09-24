# Judge comparison — prompt v1/v2 x Haiku 4.5/Sonnet 5, thinking modes — 2026-09-24 12:42

Reviewed labels: docs/shared/2026-09-16_source_traces_labeled_v3.md. Exact-match rate on label sets, kappa on the primary label (reviewed as reference). Judge blocks and nodes from the derivation on the judge's labels, against the reviewed 46/193 (c004) and 37/146 (e036).

Runs:

- `judge_source_2026-09-16_2347`: model haiku (echoed claude-haiku-4-5-20251001), prompt v1, thinking off (off)
- `judge_source_haiku_v2_2026-09-17_0012`: model haiku (echoed {'e036': 'claude-haiku-4-5-20251001', 'c004': 'claude-haiku-4-5-20251001'}), prompt v2, thinking off (off)
- `judge_source_sonnet_v1_2026-09-17_0008`: model sonnet (echoed {'e036': 'claude-sonnet-5', 'c004': 'claude-sonnet-5'}), prompt v1, thinking off (leaked)
- `judge_source_sonnet_v2_2026-09-17_0012`: model sonnet (echoed {'e036': 'claude-sonnet-5', 'c004': 'claude-sonnet-5'}), prompt v2, thinking off (leaked)
- `judge_source_sonnet_v2_thinklow_r1_2026-09-17_1017`: model sonnet (echoed {'e036': 'claude-sonnet-5', 'c004': 'claude-sonnet-5'}), prompt v2, thinking low (low r1)
- `judge_source_sonnet_v2_thinklow_r2_2026-09-17_1017`: model sonnet (echoed {'e036': 'claude-sonnet-5', 'c004': 'claude-sonnet-5'}), prompt v2, thinking low (low r2)
- `judge_source_sonnet_v2_thinkmedium_2026-09-17_1041`: model sonnet (echoed {'e036': 'claude-sonnet-5', 'c004': 'claude-sonnet-5'}), prompt v2, thinking medium (medium)
- `judge_source_sonnet_v2_thinknone_2026-09-17_1045`: model sonnet (echoed {'e036': 'claude-sonnet-5', 'c004': 'claude-sonnet-5'}), prompt v2, thinking none (none)
- `judge_source_sonnet_v3_thinklow_2026-09-17_1324`: model sonnet (echoed {'e036': 'claude-sonnet-5', 'c004': 'claude-sonnet-5'}), prompt v3, thinking low (low)
- `judge_source_v3low_2026-09-24_1239`: model sonnet (echoed {'c004': 'claude-sonnet-5', 'e036': 'claude-sonnet-5'}), prompt v3, thinking low (low)

## 2x2, thinking off: C-trace c004 (375 sentences)

| cell | L1 exact | L1 kappa | L2 exact | L2 kappa | L3 exact | L3 kappa | blocks (reviewed) | nodes (reviewed) | attempts | cost |
|---|---|---|---|---|---|---|---|---|---|---|
| haiku × v1 | 0.445 | 0.122 | 0.219 | 0.155 | 0.189 | 0.147 | 14 (46) | 45 (193) | 1 | $0.0121 |
| haiku × v2 | 0.507 | 0.192 | 0.251 | 0.188 | 0.184 | 0.144 | 5 (46) | 41 (193) | 1 | $0.0119 |
| sonnet × v1 | 0.744 | 0.658 | 0.576 | 0.553 | 0.563 | 0.549 | 40 (46) | 202 (193) | 2 | $0.1722 |
| sonnet × v2 | 0.808 | 0.760 | 0.645 | 0.629 | 0.629 | 0.619 | 46 (46) | 195 (193) | 2 | $0.1637 |

## 2x2, thinking off: E-trace e036 (254 sentences)

| cell | L1 exact | L1 kappa | L2 exact | L2 kappa | L3 exact | L3 kappa | blocks (reviewed) | nodes (reviewed) | attempts | cost |
|---|---|---|---|---|---|---|---|---|---|---|
| haiku × v1 | 0.539 | 0.433 | 0.346 | 0.317 | 0.327 | 0.306 | 20 (37) | 80 (146) | 1 | $0.0163 |
| haiku × v2 | 0.535 | 0.422 | 0.362 | 0.328 | 0.319 | 0.290 | 15 (37) | 49 (146) | 1 | $0.0149 |
| sonnet × v1 | 0.791 | 0.746 | 0.661 | 0.641 | 0.626 | 0.609 | 37 (37) | 152 (146) | 2 | $0.1563 |
| sonnet × v2 | 0.858 | 0.830 | 0.807 | 0.800 | 0.780 | 0.773 | 33 (37) | 157 (146) | 2 | $0.1607 |

## 2x2, thinking off: Pooled (629 sentences)

| cell | L1 exact | L1 kappa | L2 exact | L2 kappa | L3 exact | L3 kappa | blocks (reviewed) | nodes (reviewed) | attempts | cost |
|---|---|---|---|---|---|---|---|---|---|---|
| haiku × v1 | 0.483 | 0.288 | 0.270 | 0.228 | 0.245 | 0.217 | 34 (83) | 125 (339) | 1+1 | $0.0283 |
| haiku × v2 | 0.518 | 0.336 | 0.296 | 0.254 | 0.238 | 0.210 | 20 (83) | 90 (339) | 1+1 | $0.0269 |
| sonnet × v1 | 0.763 | 0.705 | 0.610 | 0.591 | 0.588 | 0.575 | 77 (83) | 354 (339) | 2+2 | $0.3285 |
| sonnet × v2 | 0.828 | 0.794 | 0.711 | 0.699 | 0.690 | 0.682 | 79 (83) | 352 (339) | 2+2 | $0.3243 |

## Confusion classes per 2x2 cell (pooled over both traces; reviewed → judge on the Level 2 primary label; option evaluation as n_judge vs n_reviewed of the Level 2 label set)

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

## Structural metrics (scripts/structural_agreement.py), every run

### judge_source_2026-09-16_2347 (haiku × v1, thinking off)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e036 | 37 / 20 | 11 / 26 (7) / 9 | 0.550 / 0.297 / 0.386 | 11 / 11 | 17 / 36 (0.472) | 66 / 80 / 14 | 0.584 | 70 / 146 (0.479) | 13 / 104 | 117 / 49 / 5 / 83 | 0.684 |
| c004 | 47 / 14 | 14 / 33 (0) / 0 | 1.000 / 0.298 / 0.459 | 14 / 14 | 26 / 46 (0.565) | 38 / 155 / 7 | 0.319 | 70 / 193 (0.363) | 7 / 178 | 208 / 85 / 11 / 71 | 0.684 |
| pooled | 84 / 34 | 25 / 59 (7) / 9 | 0.735 / 0.298 / 0.424 | 25 / 25 | 43 / 82 (0.524) | 104 / 235 / 21 | 0.448 | 140 / 339 (0.413) | 20 / 282 | 325 / 134 / 16 / 154 | 0.684 |

Next-node confusions (reviewed → judge, pooled): Planning → Reasoning 21; Planning → Reflection 10; Assumption → Reasoning 5; Planning → Restatement 2; Planning → Assumption 1
e036: missed reviewed openers at s12, s19, s20, s42, s71, s75, s77, s93, s96, s105, s144, s152, s154, s166, s168, s174, s177, s182, s187, s193, s204, s207, s213, s215, s220, s251; extra judge openers at s145, s164, s169, s178, s188, s208, s216, s222, s252
c004: missed reviewed openers at s8, s13, s15, s23, s31, s36, s42, s43, s58, s98, s114, s116, s132, s144, s148, s166, s171, s190, s199, s202, s209, s216, s227, s229, s254, s263, s266, s277, s302, s330, s342, s344, s356; extra judge openers at s-

### judge_source_haiku_v2_2026-09-17_0012 (haiku × v2, thinking off)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e036 | 37 / 15 | 13 / 24 (2) / 2 | 0.867 / 0.351 / 0.500 | 13 / 13 | 15 / 36 (0.417) | 35 / 111 / 14 | 0.359 | 62 / 146 (0.425) | 14 / 126 | 118 / 44 / 11 / 81 | 0.682 |
| c004 | 47 / 5 | 5 / 42 (0) / 0 | 1.000 / 0.106 / 0.192 | 5 / 5 | 15 / 46 (0.326) | 34 / 159 / 7 | 0.291 | 74 / 193 (0.383) | 7 / 174 | 185 / 96 / 25 / 69 | 0.605 |
| pooled | 84 / 20 | 18 / 66 (2) / 2 | 0.900 / 0.214 / 0.346 | 18 / 18 | 30 / 82 (0.366) | 69 / 270 / 21 | 0.322 | 136 / 339 (0.401) | 21 / 300 | 303 / 140 / 36 / 150 | 0.633 |

Next-node confusions (reviewed → judge, pooled): Planning → Reasoning 33; Planning → Reflection 7; Assumption → Reasoning 5; Planning → Restatement 3; Planning → Conclusion 3; Planning → Assumption 1
e036: missed reviewed openers at s16, s19, s20, s53, s71, s75, s77, s93, s96, s100, s117, s144, s152, s166, s168, s174, s182, s187, s193, s204, s213, s220, s247, s251; extra judge openers at s188, s252
c004: missed reviewed openers at s15, s23, s31, s36, s42, s43, s79, s98, s107, s114, s116, s120, s132, s137, s144, s148, s160, s166, s171, s187, s190, s193, s199, s202, s209, s216, s227, s229, s254, s263, s266, s277, s288, s302, s325, s330, s340, s342, s344, s352, s356, s362; extra judge openers at s-

### judge_source_sonnet_v1_2026-09-17_0008 (sonnet × v1, thinking leaked)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e036 | 37 / 37 | 28 / 9 (2) / 9 | 0.757 / 0.757 / 0.757 | 27 / 28 | 32 / 36 (0.889) | 126 / 20 / 26 | 0.846 | 118 / 146 (0.808) | 12 / 31 | 53 / 33 / 9 / 159 | 0.558 |
| c004 | 47 / 40 | 37 / 10 (1) / 3 | 0.925 / 0.787 / 0.851 | 36 / 37 | 41 / 46 (0.891) | 167 / 26 / 35 | 0.846 | 141 / 193 (0.731) | 17 / 37 | 96 / 63 / 5 / 211 | 0.585 |
| pooled | 84 / 77 | 65 / 19 (3) / 12 | 0.844 / 0.774 / 0.807 | 63 / 65 | 73 / 82 (0.890) | 293 / 46 / 61 | 0.846 | 259 / 339 (0.764) | 29 / 68 | 149 / 96 / 14 / 370 | 0.575 |

Next-node confusions (reviewed → judge, pooled): Planning → Reasoning 4; Assumption → Planning 2; Planning → Restatement 1; Conclusion → Planning 1; Planning → Knowledge 1
e036: missed reviewed openers at s12, s19, s77, s96, s117, s182, s187, s193, s204; extra judge openers at s142, s153, s164, s165, s176, s186, s214, s218, s246
c004: missed reviewed openers at s8, s13, s36, s42, s58, s79, s216, s325, s340, s342; extra judge openers at s111, s161, s291

### judge_source_sonnet_v2_2026-09-17_0012 (sonnet × v2, thinking leaked)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e036 | 37 / 33 | 33 / 4 (1) / 0 | 1.000 / 0.892 / 0.943 | 33 / 33 | 34 / 36 (0.944) | 136 / 10 / 21 | 0.898 | 125 / 146 (0.856) | 13 / 17 | 36 / 13 / 7 / 198 | 0.643 |
| c004 | 47 / 46 | 46 / 1 (1) / 0 | 1.000 / 0.979 / 0.989 | 44 / 46 | 43 / 46 (0.935) | 170 / 23 / 25 | 0.876 | 159 / 193 (0.824) | 17 / 34 | 72 / 61 / 6 / 236 | 0.518 |
| pooled | 84 / 79 | 79 / 5 (2) / 0 | 1.000 / 0.940 / 0.969 | 77 / 79 | 77 / 82 (0.939) | 306 / 33 / 46 | 0.886 | 284 / 339 (0.838) | 30 / 51 | 108 / 74 / 13 / 434 | 0.554 |

Next-node confusions (reviewed → judge, pooled): Planning → Reasoning 2; Assumption → Planning 2; Planning → Knowledge 1
e036: missed reviewed openers at s19, s77, s117, s182; extra judge openers at s-
c004: missed reviewed openers at s42; extra judge openers at s-

### judge_source_sonnet_v2_thinklow_r1_2026-09-17_1017 (sonnet × v2, thinking low r1)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e036 | 37 / 34 | 33 / 4 (1) / 1 | 0.971 / 0.892 / 0.930 | 33 / 33 | 33 / 36 (0.917) | 120 / 26 / 17 | 0.848 | 113 / 146 (0.774) | 7 / 39 | 46 / 22 / 1 / 185 | 0.667 |
| c004 | 47 / 43 | 41 / 6 (0) / 2 | 0.953 / 0.872 / 0.911 | 40 / 41 | 40 / 46 (0.870) | 165 / 28 / 41 | 0.827 | 143 / 193 (0.741) | 21 / 43 | 95 / 51 / 8 / 221 | 0.617 |
| pooled | 84 / 77 | 74 / 10 (1) / 3 | 0.961 / 0.881 / 0.919 | 73 / 74 | 73 / 82 (0.890) | 285 / 54 / 58 | 0.836 | 256 / 339 (0.755) | 28 / 82 | 141 / 73 / 9 / 406 | 0.632 |

Next-node confusions (reviewed → judge, pooled): Planning → Restatement 5; Assumption → Planning 2; Planning → Reasoning 1; Planning → Knowledge 1
e036: missed reviewed openers at s19, s77, s96, s193; extra judge openers at s130
c004: missed reviewed openers at s42, s43, s114, s116, s216, s227; extra judge openers at s291, s328

### judge_source_sonnet_v2_thinklow_r2_2026-09-17_1017 (sonnet × v2, thinking low r2)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e036 | 37 / 33 | 30 / 7 (0) / 3 | 0.909 / 0.811 / 0.857 | 30 / 30 | 33 / 36 (0.917) | 125 / 21 / 17 | 0.868 | 113 / 146 (0.774) | 13 / 34 | 46 / 21 / 6 / 181 | 0.630 |
| c004 | 47 / 43 | 42 / 5 (2) / 1 | 0.977 / 0.894 / 0.933 | 41 / 42 | 41 / 46 (0.891) | 170 / 23 / 40 | 0.844 | 147 / 193 (0.762) | 17 / 35 | 86 / 62 / 4 / 223 | 0.566 |
| pooled | 84 / 76 | 72 / 12 (2) / 4 | 0.947 / 0.857 / 0.900 | 71 / 72 | 74 / 82 (0.902) | 295 / 44 / 57 | 0.854 | 260 / 339 (0.767) | 30 / 69 | 132 / 83 / 10 / 404 | 0.587 |

Next-node confusions (reviewed → judge, pooled): Planning → Restatement 4; Assumption → Planning 2; Planning → Reasoning 1; Planning → Knowledge 1
e036: missed reviewed openers at s19, s20, s77, s96, s117, s152, s193; extra judge openers at s84, s91, s130
c004: missed reviewed openers at s13, s42, s114, s216, s227; extra judge openers at s12

### judge_source_sonnet_v2_thinkmedium_2026-09-17_1041 (sonnet × v2, thinking medium)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e036 | 37 / 34 | 32 / 5 (2) / 2 | 0.941 / 0.865 / 0.901 | 31 / 32 | 33 / 36 (0.917) | 129 / 17 / 11 | 0.902 | 122 / 146 (0.836) | 9 / 25 | 35 / 16 / 9 / 194 | 0.583 |
| c004 | 47 / 48 | 45 / 2 (1) / 3 | 0.938 / 0.957 / 0.947 | 45 / 45 | 44 / 46 (0.957) | 176 / 17 / 45 | 0.850 | 164 / 193 (0.850) | 22 / 24 | 73 / 47 / 5 / 250 | 0.584 |
| pooled | 84 / 82 | 77 / 7 (3) / 5 | 0.939 / 0.917 / 0.928 | 76 / 77 | 77 / 82 (0.939) | 305 / 34 / 56 | 0.871 | 286 / 339 (0.844) | 31 / 49 | 108 / 63 / 14 / 444 | 0.584 |

Next-node confusions (reviewed → judge, pooled): Planning → Reasoning 1; Planning → Assumption 1; Planning → Restatement 1; Planning → Knowledge 1; Assumption → Planning 1
e036: missed reviewed openers at s19, s77, s96, s117, s193; extra judge openers at s86, s116
c004: missed reviewed openers at s42, s216; extra judge openers at s111, s164, s295

### judge_source_sonnet_v2_thinknone_2026-09-17_1045 (sonnet × v2, thinking none)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e036 | 37 / 33 | 28 / 9 (3) / 5 | 0.848 / 0.757 / 0.800 | 28 / 28 | 29 / 36 (0.806) | 117 / 29 / 13 | 0.848 | 112 / 146 (0.767) | 12 / 46 | 44 / 22 / 7 / 181 | 0.603 |
| c004 | 47 / 48 | 41 / 6 (3) / 7 | 0.854 / 0.872 / 0.863 | 39 / 41 | 40 / 46 (0.870) | 167 / 26 / 65 | 0.786 | 141 / 193 (0.731) | 29 / 34 | 110 / 49 / 7 / 209 | 0.663 |
| pooled | 84 / 81 | 69 / 15 (6) / 12 | 0.852 / 0.821 / 0.836 | 67 / 69 | 69 / 82 (0.841) | 284 / 55 / 78 | 0.810 | 253 / 339 (0.746) | 41 / 80 | 154 / 71 / 14 / 390 | 0.644 |

Next-node confusions (reviewed → judge, pooled): Planning → Restatement 4; Planning → Reasoning 3; Planning → Reflection 2; Assumption → Planning 2; Planning → Conclusion 1; Planning → Knowledge 1
e036: missed reviewed openers at s19, s77, s96, s117, s144, s182, s193, s213, s245; extra judge openers at s91, s113, s145, s164, s244
c004: missed reviewed openers at s13, s42, s114, s216, s227, s288; extra judge openers at s1, s12, s40, s289, s291, s328, s366

### judge_source_sonnet_v3_thinklow_2026-09-17_1324 (sonnet × v3, thinking low)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e036 | 37 / 34 | 33 / 4 (0) / 1 | 0.971 / 0.892 / 0.930 | 33 / 33 | 33 / 36 (0.917) | 131 / 15 / 6 | 0.926 | 121 / 146 (0.829) | 6 / 25 | 31 / 21 / 5 / 197 | 0.544 |
| c004 | 47 / 43 | 41 / 6 (1) / 2 | 0.953 / 0.872 / 0.911 | 41 / 41 | 43 / 46 (0.935) | 174 / 19 / 33 | 0.870 | 160 / 193 (0.829) | 19 / 27 | 72 / 53 / 4 / 246 | 0.558 |
| pooled | 84 / 77 | 74 / 10 (1) / 3 | 0.961 / 0.881 / 0.919 | 74 / 74 | 76 / 82 (0.927) | 305 / 34 / 39 | 0.893 | 281 / 339 (0.829) | 25 / 52 | 103 / 74 / 9 / 443 | 0.554 |

Next-node confusions (reviewed → judge, pooled): Planning → Reasoning 2; Planning → Restatement 2; Assumption → Planning 2
e036: missed reviewed openers at s77, s96, s182, s193; extra judge openers at s84
c004: missed reviewed openers at s13, s114, s116, s216, s227, s356; extra judge openers at s12, s111

### judge_source_v3low_2026-09-24_1239 (sonnet × v3, thinking low)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| c004 | 47 / 43 | 42 / 5 (2) / 1 | 0.977 / 0.894 / 0.933 | 41 / 42 | 42 / 46 (0.913) | 168 / 25 / 24 | 0.873 | 147 / 193 (0.762) | 16 / 36 | 87 / 48 / 2 / 238 | 0.635 |
| e036 | 37 / 34 | 33 / 4 (0) / 1 | 0.971 / 0.892 / 0.930 | 33 / 33 | 33 / 36 (0.917) | 128 / 18 / 8 | 0.908 | 117 / 146 (0.801) | 6 / 32 | 38 / 19 / 5 / 192 | 0.613 |
| pooled | 84 / 77 | 75 / 9 (2) / 2 | 0.974 / 0.893 / 0.932 | 74 / 75 | 75 / 82 (0.915) | 296 / 43 / 32 | 0.888 | 264 / 339 (0.779) | 22 / 68 | 125 / 67 / 7 / 430 | 0.628 |

Next-node confusions (reviewed → judge, pooled): Planning → Restatement 4; Assumption → Planning 2; Planning → Reasoning 1
c004: missed reviewed openers at s13, s43, s114, s116, s216; extra judge openers at s12
e036: missed reviewed openers at s77, s96, s182, s193; extra judge openers at s84

## Reasoning curve, Sonnet 5 × prompt v2

Thinking tokens per sentence from usage.output_tokens_details (0 where thinking was disabled; the leaked cell's reasoning sits in its output tokens instead); structural metrics pooled over both traces; projected judge-side cost per collection at Sonnet batch prices ($1/$5 per million input/output, cache read $0.10, cache write $1.25): input = collection text tokens × (the cell's uncached input ÷ one clean pass of 15,038 tokens) + prefix tokens (archived500: 424k × 1.6; new continuations: 720 × 1,908 × 1.6), output = the cell's output tokens per judged sentence × collection sentences (sweep44 15,295; archived500 240,620; new continuations 5.9M ÷ 23.91 = 246,781), one cached system prompt read per document.

| cell | run | thinking tokens / sentence | attempts | L1 exact / kappa | L2 exact / kappa | full exact / kappa | block F1 | next-node agreement | node F1 | L1 share of disagreements | cost e036 / c004 | output tokens / sentence | input factor | projected sweep44 | projected archived500 | projected new continuations | projected total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | `judge_source_sonnet_v2_thinknone_2026-09-17_1045` | 0.00 | 2+1 | 0.755 / 0.699 | 0.642 / 0.627 | 0.620 / 0.609 | 0.836 | 0.841 | 0.810 | 0.644 | $0.0863 / $0.0552 | 11.51 | 1.51 | $1.21 | $20.32 | $25.93 | $47.46 |
| leaked | `judge_source_sonnet_v2_2026-09-17_0012` | 0.00 | 2+2 | 0.828 / 0.794 | 0.711 / 0.699 | 0.690 / 0.682 | 0.969 | 0.939 | 0.886 | 0.554 | $0.1607 / $0.1637 | 32.86 | 3.08 | $3.13 | $51.54 | $61.48 | $116.15 |
| low r1 | `judge_source_sonnet_v2_thinklow_r1_2026-09-17_1017` | 19.79 | 1+1 | 0.776 / 0.724 | 0.660 / 0.644 | 0.645 / 0.634 | 0.919 | 0.890 | 0.836 | 0.632 | $0.1076 / $0.1142 | 27.00 | 1.00 | $2.30 | $37.12 | $42.00 | $81.42 |
| low r2 | `judge_source_sonnet_v2_thinklow_r2_2026-09-17_1017` | 26.49 | 1+1 | 0.790 / 0.741 | 0.658 / 0.642 | 0.642 / 0.631 | 0.900 | 0.902 | 0.854 | 0.587 | $0.1114 / $0.1320 | 33.41 | 1.00 | $2.79 | $44.84 | $49.91 | $97.53 |
| medium | `judge_source_sonnet_v2_thinkmedium_2026-09-17_1041` | 43.51 | 1+1 | 0.828 / 0.791 | 0.728 / 0.715 | 0.706 / 0.696 | 0.928 | 0.939 | 0.871 | 0.584 | $0.1469 / $0.2225 | 50.46 | 1.00 | $4.09 | $65.36 | $70.95 | $140.40 |

### Ten most frequent Level 2 confusions, none (`judge_source_sonnet_v2_thinknone_2026-09-17_1045`, reviewed → judge, pooled)

| reviewed | judge | count |
|---|---|---|
| Reasoning > speculation | Reasoning > option evaluation | 16 |
| Reasoning > hedge word analysis | Reasoning > option evaluation | 10 |
| Restatement > rephrasing an earlier sentence | Example > non-exhaustive listing | 10 |
| Reasoning > calculation | Reasoning > logical reasoning | 9 |
| Reasoning > logical reasoning | Conclusion > intermediate conclusion | 8 |
| Reflection > meta-evaluation of a step | Reasoning > option evaluation | 7 |
| Planning > local plan | Restatement > rephrasing the prompt | 6 |
| Restatement > rephrasing an earlier sentence | Conclusion > intermediate conclusion | 6 |
| Restatement > rephrasing an earlier sentence | Reasoning > option evaluation | 6 |
| Reasoning > calculation | Planning > local plan | 5 |

### Ten most frequent Level 2 confusions, leaked (`judge_source_sonnet_v2_2026-09-17_0012`, reviewed → judge, pooled)

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

### Ten most frequent Level 2 confusions, low r1 (`judge_source_sonnet_v2_thinklow_r1_2026-09-17_1017`, reviewed → judge, pooled)

| reviewed | judge | count |
|---|---|---|
| Reasoning > calculation | Reasoning > logical reasoning | 13 |
| Restatement > rephrasing an earlier sentence | Example > non-exhaustive listing | 11 |
| Reasoning > speculation | Reasoning > option evaluation | 10 |
| Restatement > rephrasing an earlier sentence | Conclusion > intermediate conclusion | 10 |
| Reasoning > hedge word analysis | Reasoning > option evaluation | 9 |
| Reasoning > logical reasoning | Conclusion > intermediate conclusion | 8 |
| Reasoning > speculation | Reasoning > logical reasoning | 7 |
| Planning > initiate backtracking | Planning > initiate verification | 7 |
| Planning > local plan | Restatement > rephrasing the prompt | 6 |
| Reflection > meta-evaluation of a step | Reasoning > option evaluation | 6 |

### Ten most frequent Level 2 confusions, low r2 (`judge_source_sonnet_v2_thinklow_r2_2026-09-17_1017`, reviewed → judge, pooled)

| reviewed | judge | count |
|---|---|---|
| Reasoning > calculation | Reasoning > logical reasoning | 17 |
| Reasoning > hedge word analysis | Reasoning > option evaluation | 10 |
| Restatement > rephrasing an earlier sentence | Conclusion > intermediate conclusion | 9 |
| Reasoning > speculation | Reasoning > option evaluation | 8 |
| Restatement > rephrasing an earlier sentence | Reasoning > logical reasoning | 8 |
| Restatement > rephrasing an earlier sentence | Example > non-exhaustive listing | 8 |
| Reasoning > speculation | Reasoning > logical reasoning | 7 |
| Planning > initiate backtracking | Planning > initiate verification | 7 |
| Reasoning > logical reasoning | Conclusion > intermediate conclusion | 6 |
| Planning > local plan | Restatement > rephrasing the prompt | 6 |

### Ten most frequent Level 2 confusions, medium (`judge_source_sonnet_v2_thinkmedium_2026-09-17_1041`, reviewed → judge, pooled)

| reviewed | judge | count |
|---|---|---|
| Reasoning > calculation | Reasoning > logical reasoning | 13 |
| Reasoning > speculation | Reasoning > option evaluation | 9 |
| Reasoning > logical reasoning | Conclusion > intermediate conclusion | 8 |
| Reasoning > hedge word analysis | Reasoning > option evaluation | 7 |
| Planning > local plan | Restatement > rephrasing the prompt | 6 |
| Reasoning > option evaluation | Conclusion > intermediate conclusion | 6 |
| Planning > initiate verification | Planning > initiate backtracking | 6 |
| Reasoning > defining symbols | Restatement > rephrasing an earlier sentence | 6 |
| Restatement > rephrasing an earlier sentence | Example > non-exhaustive listing | 5 |
| Restatement > rephrasing an earlier sentence | Reasoning > logical reasoning | 5 |

