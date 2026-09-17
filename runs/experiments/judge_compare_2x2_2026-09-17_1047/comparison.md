# Judge comparison — prompt v1/v2 x Haiku 4.5/Sonnet 5, thinking modes — 2026-09-17 10:47

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

## 2x2, thinking off: C-trace c004 (375 sentences)

| cell | L1 exact | L1 kappa | L2 exact | L2 kappa | L3 exact | L3 kappa | blocks (reviewed) | nodes (reviewed) | attempts | cost |
|---|---|---|---|---|---|---|---|---|---|---|
| haiku × v1 | 0.445 | 0.122 | 0.219 | 0.155 | 0.197 | 0.155 | 14 (46) | 45 (193) | 1 | $0.0121 |
| haiku × v2 | 0.507 | 0.192 | 0.251 | 0.188 | 0.184 | 0.144 | 5 (46) | 41 (193) | 1 | $0.0119 |
| sonnet × v1 | 0.747 | 0.662 | 0.579 | 0.556 | 0.571 | 0.557 | 40 (46) | 202 (193) | 2 | $0.1722 |
| sonnet × v2 | 0.811 | 0.764 | 0.648 | 0.632 | 0.635 | 0.624 | 46 (46) | 195 (193) | 2 | $0.1637 |

## 2x2, thinking off: E-trace e036 (254 sentences)

| cell | L1 exact | L1 kappa | L2 exact | L2 kappa | L3 exact | L3 kappa | blocks (reviewed) | nodes (reviewed) | attempts | cost |
|---|---|---|---|---|---|---|---|---|---|---|
| haiku × v1 | 0.539 | 0.433 | 0.346 | 0.317 | 0.331 | 0.309 | 20 (37) | 80 (146) | 1 | $0.0163 |
| haiku × v2 | 0.535 | 0.422 | 0.362 | 0.328 | 0.319 | 0.289 | 15 (37) | 49 (146) | 1 | $0.0149 |
| sonnet × v1 | 0.791 | 0.746 | 0.661 | 0.641 | 0.634 | 0.617 | 37 (37) | 152 (146) | 2 | $0.1563 |
| sonnet × v2 | 0.858 | 0.830 | 0.807 | 0.800 | 0.787 | 0.782 | 33 (37) | 157 (146) | 2 | $0.1607 |

## 2x2, thinking off: Pooled (629 sentences)

| cell | L1 exact | L1 kappa | L2 exact | L2 kappa | L3 exact | L3 kappa | blocks (reviewed) | nodes (reviewed) | attempts | cost |
|---|---|---|---|---|---|---|---|---|---|---|
| haiku × v1 | 0.483 | 0.288 | 0.270 | 0.228 | 0.251 | 0.223 | 34 (83) | 125 (339) | 1+1 | $0.0283 |
| haiku × v2 | 0.518 | 0.336 | 0.296 | 0.254 | 0.238 | 0.210 | 20 (83) | 90 (339) | 1+1 | $0.0269 |
| sonnet × v1 | 0.765 | 0.707 | 0.612 | 0.593 | 0.596 | 0.583 | 77 (83) | 354 (339) | 2+2 | $0.3285 |
| sonnet × v2 | 0.830 | 0.796 | 0.712 | 0.701 | 0.696 | 0.689 | 79 (83) | 352 (339) | 2+2 | $0.3243 |

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
| e036 | 37 / 20 | 11 / 26 (7) / 9 | 0.550 / 0.297 / 0.386 | 11 / 11 | 17 / 36 (0.472) | 66 / 80 / 14 | 0.584 | 70 / 146 (0.479) | 13 / 104 | 117 / 49 / 4 / 84 | 0.688 |
| c004 | 46 / 14 | 14 / 32 (0) / 0 | 1.000 / 0.304 / 0.467 | 14 / 14 | 26 / 45 (0.578) | 38 / 155 / 7 | 0.319 | 70 / 193 (0.363) | 7 / 178 | 208 / 85 / 8 / 74 | 0.691 |
| pooled | 83 / 34 | 25 / 58 (7) / 9 | 0.735 / 0.301 / 0.427 | 25 / 25 | 43 / 81 (0.531) | 104 / 235 / 21 | 0.448 | 140 / 339 (0.413) | 20 / 282 | 325 / 134 / 12 / 158 | 0.690 |

Next-node confusions (reviewed → judge, pooled): Planning → Reasoning 20; Planning → Reflection 10; Assumption → Reasoning 5; Planning → Restatement 2; Planning → Assumption 1
e036: missed reviewed openers at s12, s19, s20, s42, s71, s75, s77, s93, s96, s105, s144, s152, s154, s166, s168, s174, s177, s182, s187, s193, s204, s207, s213, s215, s220, s251; extra judge openers at s145, s164, s169, s178, s188, s208, s216, s222, s252
c004: missed reviewed openers at s8, s13, s15, s23, s31, s36, s43, s58, s98, s114, s116, s132, s144, s148, s166, s171, s190, s199, s202, s209, s216, s227, s229, s254, s263, s266, s277, s302, s330, s342, s344, s356; extra judge openers at s-

### judge_source_haiku_v2_2026-09-17_0012 (haiku × v2, thinking off)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e036 | 37 / 15 | 13 / 24 (2) / 2 | 0.867 / 0.351 / 0.500 | 13 / 13 | 15 / 36 (0.417) | 35 / 111 / 14 | 0.359 | 62 / 146 (0.425) | 14 / 126 | 118 / 44 / 11 / 81 | 0.682 |
| c004 | 46 / 5 | 5 / 41 (0) / 0 | 1.000 / 0.109 / 0.196 | 5 / 5 | 15 / 45 (0.333) | 34 / 159 / 7 | 0.291 | 74 / 193 (0.383) | 7 / 174 | 185 / 96 / 25 / 69 | 0.605 |
| pooled | 83 / 20 | 18 / 65 (2) / 2 | 0.900 / 0.217 / 0.350 | 18 / 18 | 30 / 81 (0.370) | 69 / 270 / 21 | 0.322 | 136 / 339 (0.401) | 21 / 300 | 303 / 140 / 36 / 150 | 0.633 |

Next-node confusions (reviewed → judge, pooled): Planning → Reasoning 32; Planning → Reflection 7; Assumption → Reasoning 5; Planning → Restatement 3; Planning → Conclusion 3; Planning → Assumption 1
e036: missed reviewed openers at s16, s19, s20, s53, s71, s75, s77, s93, s96, s100, s117, s144, s152, s166, s168, s174, s182, s187, s193, s204, s213, s220, s247, s251; extra judge openers at s188, s252
c004: missed reviewed openers at s15, s23, s31, s36, s43, s79, s98, s107, s114, s116, s120, s132, s137, s144, s148, s160, s166, s171, s187, s190, s193, s199, s202, s209, s216, s227, s229, s254, s263, s266, s277, s288, s302, s325, s330, s340, s342, s344, s352, s356, s362; extra judge openers at s-

### judge_source_sonnet_v1_2026-09-17_0008 (sonnet × v1, thinking leaked)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e036 | 37 / 37 | 28 / 9 (2) / 9 | 0.757 / 0.757 / 0.757 | 27 / 28 | 32 / 36 (0.889) | 126 / 20 / 26 | 0.846 | 118 / 146 (0.808) | 12 / 31 | 53 / 33 / 7 / 161 | 0.570 |
| c004 | 46 / 40 | 37 / 9 (0) / 3 | 0.925 / 0.804 / 0.860 | 36 / 37 | 41 / 45 (0.911) | 167 / 26 / 35 | 0.846 | 142 / 193 (0.736) | 17 / 37 | 95 / 63 / 3 / 214 | 0.590 |
| pooled | 83 / 77 | 65 / 18 (2) / 12 | 0.844 / 0.783 / 0.812 | 63 / 65 | 73 / 81 (0.901) | 293 / 46 / 61 | 0.846 | 260 / 339 (0.767) | 29 / 68 | 148 / 96 / 10 / 375 | 0.583 |

Next-node confusions (reviewed → judge, pooled): Planning → Reasoning 4; Assumption → Planning 2; Planning → Restatement 1; Conclusion → Planning 1
e036: missed reviewed openers at s12, s19, s77, s96, s117, s182, s187, s193, s204; extra judge openers at s142, s153, s164, s165, s176, s186, s214, s218, s246
c004: missed reviewed openers at s8, s13, s36, s58, s79, s216, s325, s340, s342; extra judge openers at s111, s161, s291

### judge_source_sonnet_v2_2026-09-17_0012 (sonnet × v2, thinking leaked)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e036 | 37 / 33 | 33 / 4 (1) / 0 | 1.000 / 0.892 / 0.943 | 33 / 33 | 34 / 36 (0.944) | 136 / 10 / 21 | 0.898 | 125 / 146 (0.856) | 13 / 17 | 36 / 13 / 5 / 200 | 0.667 |
| c004 | 46 / 46 | 46 / 0 (0) / 0 | 1.000 / 1.000 / 1.000 | 44 / 46 | 43 / 45 (0.956) | 170 / 23 / 25 | 0.876 | 160 / 193 (0.829) | 17 / 34 | 71 / 61 / 5 / 238 | 0.518 |
| pooled | 83 / 79 | 79 / 4 (1) / 0 | 1.000 / 0.952 / 0.975 | 77 / 79 | 77 / 81 (0.951) | 306 / 33 / 46 | 0.886 | 285 / 339 (0.841) | 30 / 51 | 107 / 74 / 10 / 438 | 0.560 |

Next-node confusions (reviewed → judge, pooled): Planning → Reasoning 2; Assumption → Planning 2
e036: missed reviewed openers at s19, s77, s117, s182; extra judge openers at s-

### judge_source_sonnet_v2_thinklow_r1_2026-09-17_1017 (sonnet × v2, thinking low r1)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e036 | 37 / 34 | 33 / 4 (1) / 1 | 0.971 / 0.892 / 0.930 | 33 / 33 | 33 / 36 (0.917) | 120 / 26 / 17 | 0.848 | 113 / 146 (0.774) | 7 / 39 | 46 / 22 / 0 / 186 | 0.676 |
| c004 | 46 / 43 | 41 / 5 (0) / 2 | 0.953 / 0.891 / 0.921 | 40 / 41 | 40 / 45 (0.889) | 165 / 28 / 41 | 0.827 | 144 / 193 (0.746) | 21 / 43 | 94 / 51 / 6 / 224 | 0.623 |
| pooled | 83 / 77 | 74 / 9 (1) / 3 | 0.961 / 0.892 / 0.925 | 73 / 74 | 73 / 81 (0.901) | 285 / 54 / 58 | 0.836 | 257 / 339 (0.758) | 28 / 82 | 140 / 73 / 6 / 410 | 0.639 |

Next-node confusions (reviewed → judge, pooled): Planning → Restatement 5; Assumption → Planning 2; Planning → Reasoning 1
e036: missed reviewed openers at s19, s77, s96, s193; extra judge openers at s130
c004: missed reviewed openers at s43, s114, s116, s216, s227; extra judge openers at s291, s328

### judge_source_sonnet_v2_thinklow_r2_2026-09-17_1017 (sonnet × v2, thinking low r2)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e036 | 37 / 33 | 30 / 7 (0) / 3 | 0.909 / 0.811 / 0.857 | 30 / 30 | 33 / 36 (0.917) | 125 / 21 / 17 | 0.868 | 113 / 146 (0.774) | 13 / 34 | 46 / 21 / 4 / 183 | 0.648 |
| c004 | 46 / 43 | 42 / 4 (1) / 1 | 0.977 / 0.913 / 0.944 | 41 / 42 | 41 / 45 (0.911) | 170 / 23 / 40 | 0.844 | 148 / 193 (0.767) | 17 / 35 | 85 / 62 / 3 / 225 | 0.567 |
| pooled | 83 / 76 | 72 / 11 (1) / 4 | 0.947 / 0.867 / 0.906 | 71 / 72 | 74 / 81 (0.914) | 295 / 44 / 57 | 0.854 | 261 / 339 (0.770) | 30 / 69 | 131 / 83 / 7 / 408 | 0.593 |

Next-node confusions (reviewed → judge, pooled): Planning → Restatement 4; Assumption → Planning 2; Planning → Reasoning 1
e036: missed reviewed openers at s19, s20, s77, s96, s117, s152, s193; extra judge openers at s84, s91, s130
c004: missed reviewed openers at s13, s114, s216, s227; extra judge openers at s12

### judge_source_sonnet_v2_thinkmedium_2026-09-17_1041 (sonnet × v2, thinking medium)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e036 | 37 / 34 | 32 / 5 (2) / 2 | 0.941 / 0.865 / 0.901 | 31 / 32 | 33 / 36 (0.917) | 129 / 17 / 11 | 0.902 | 122 / 146 (0.836) | 9 / 25 | 35 / 16 / 7 / 196 | 0.603 |
| c004 | 46 / 48 | 45 / 1 (0) / 3 | 0.938 / 0.978 / 0.957 | 45 / 45 | 44 / 45 (0.978) | 176 / 17 / 45 | 0.850 | 165 / 193 (0.855) | 22 / 24 | 72 / 47 / 4 / 252 | 0.585 |
| pooled | 83 / 82 | 77 / 6 (2) / 5 | 0.939 / 0.928 / 0.933 | 76 / 77 | 77 / 81 (0.951) | 305 / 34 / 56 | 0.871 | 287 / 339 (0.847) | 31 / 49 | 107 / 63 / 11 / 448 | 0.591 |

Next-node confusions (reviewed → judge, pooled): Planning → Reasoning 1; Planning → Assumption 1; Planning → Restatement 1; Assumption → Planning 1
e036: missed reviewed openers at s19, s77, s96, s117, s193; extra judge openers at s86, s116
c004: missed reviewed openers at s216; extra judge openers at s111, s164, s295

### judge_source_sonnet_v2_thinknone_2026-09-17_1045 (sonnet × v2, thinking none)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e036 | 37 / 33 | 28 / 9 (3) / 5 | 0.848 / 0.757 / 0.800 | 28 / 28 | 29 / 36 (0.806) | 117 / 29 / 13 | 0.848 | 112 / 146 (0.767) | 12 / 46 | 44 / 22 / 5 / 183 | 0.620 |
| c004 | 46 / 48 | 41 / 5 (2) / 7 | 0.854 / 0.891 / 0.872 | 39 / 41 | 40 / 45 (0.889) | 167 / 26 / 65 | 0.786 | 142 / 193 (0.736) | 29 / 34 | 109 / 49 / 6 / 211 | 0.665 |
| pooled | 83 / 81 | 69 / 14 (5) / 12 | 0.852 / 0.831 / 0.841 | 67 / 69 | 69 / 81 (0.852) | 284 / 55 / 78 | 0.810 | 254 / 339 (0.749) | 41 / 80 | 153 / 71 / 11 / 394 | 0.651 |

Next-node confusions (reviewed → judge, pooled): Planning → Restatement 4; Planning → Reasoning 3; Planning → Reflection 2; Assumption → Planning 2; Planning → Conclusion 1
e036: missed reviewed openers at s19, s77, s96, s117, s144, s182, s193, s213, s245; extra judge openers at s91, s113, s145, s164, s244
c004: missed reviewed openers at s13, s114, s216, s227, s288; extra judge openers at s1, s12, s40, s289, s291, s328, s366

## Reasoning curve, Sonnet 5 × prompt v2

Thinking tokens per sentence from usage.output_tokens_details (0 where thinking was disabled; the leaked cell's reasoning sits in its output tokens instead); structural metrics pooled over both traces; projected judge-side cost per collection at Sonnet batch prices ($1/$5 per million input/output, cache read $0.10, cache write $1.25): input = collection text tokens × (the cell's uncached input ÷ one clean pass of 15,038 tokens) + prefix tokens (archived500: 424k × 1.6; new continuations: 720 × 1,908 × 1.6), output = the cell's output tokens per judged sentence × collection sentences (sweep44 15,295; archived500 240,620; new continuations 5.9M ÷ 23.91 = 246,781), one cached system prompt read per document.

| cell | run | thinking tokens / sentence | attempts | L1 exact / kappa | L2 exact / kappa | full exact / kappa | block F1 | next-node agreement | node F1 | L1 share of disagreements | cost e036 / c004 | output tokens / sentence | input factor | projected sweep44 | projected archived500 | projected new continuations | projected total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | `judge_source_sonnet_v2_thinknone_2026-09-17_1045` | 0.00 | 2+1 | 0.757 / 0.701 | 0.644 / 0.628 | 0.626 / 0.616 | 0.841 | 0.852 | 0.810 | 0.651 | $0.0863 / $0.0552 | 11.51 | 1.51 | $1.21 | $20.32 | $25.93 | $47.46 |
| leaked | `judge_source_sonnet_v2_2026-09-17_0012` | 0.00 | 2+2 | 0.830 / 0.796 | 0.712 / 0.701 | 0.696 / 0.689 | 0.975 | 0.951 | 0.886 | 0.560 | $0.1607 / $0.1637 | 32.86 | 3.08 | $3.13 | $51.54 | $61.48 | $116.15 |
| low r1 | `judge_source_sonnet_v2_thinklow_r1_2026-09-17_1017` | 19.79 | 1+1 | 0.777 / 0.726 | 0.661 / 0.645 | 0.652 / 0.641 | 0.925 | 0.901 | 0.836 | 0.639 | $0.1076 / $0.1142 | 27.00 | 1.00 | $2.30 | $37.12 | $42.00 | $81.42 |
| low r2 | `judge_source_sonnet_v2_thinklow_r2_2026-09-17_1017` | 26.49 | 1+1 | 0.792 / 0.744 | 0.660 / 0.644 | 0.649 / 0.637 | 0.906 | 0.914 | 0.854 | 0.593 | $0.1114 / $0.1320 | 33.41 | 1.00 | $2.79 | $44.84 | $49.91 | $97.53 |
| medium | `judge_source_sonnet_v2_thinkmedium_2026-09-17_1041` | 43.51 | 1+1 | 0.830 / 0.793 | 0.730 / 0.716 | 0.712 / 0.702 | 0.933 | 0.951 | 0.871 | 0.591 | $0.1469 / $0.2225 | 50.46 | 1.00 | $4.09 | $65.36 | $70.95 | $140.40 |

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

