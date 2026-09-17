# TEST_REPORT — t4d_r4 — 2026-09-17 13:24

Gate of rule R4 in the derivation (`scripts/derivation.py`, `scripts/structural_agreement.py`), pipeline v2 step (4d/9) and decision 20; labeling scheme v6 Section 6b. Git commit `cb372474119b2ee1a5b5caa031c6225a0cefd133`. Listing `docs/shared/2026-09-17_source_traces_labeled_v4.md`; pre-R4 listing `archive/docs/shared/2026-09-16_source_traces_labeled_v3.md` (archive, read only); texts `runs/tests/t2_split_2026-09-16_2224/sentences_source.jsonl`. R4 regex `^[\s\u23ce*_#>\d.)(-]*(?:but\s+|and\s+|oh,?\s+|okay,?\s+)?wait\b` (case-insensitive). Offline; API cost $0.

## Result: PASS (5/5 checks passed)

## Checks

- PASS — check 1, derivation gate under R4 on the reviewed labels of listing v4 (texts from sentences_source.jsonl) — c004: 375 sentences; blocks 47 derived vs 47 listed (expected 47); nodes 193 vs 193 (expected 193); interval differences 0, opener rule/label differences 0, name differences 0; R4 openers at s42, s137, s254, s288, s340, s352; listing rows with a fragment after the node name: none; e036: 254 sentences; blocks 38 derived vs 38 listed (expected 38); nodes 147 vs 147 (expected 147); interval differences 0, opener rule/label differences 0, name differences 0; R4 openers at s19, s71, s100, s179; listing rows with a fragment after the node name: s19 ('|\\| Reasoning > comparison > prompt vs original text')
- PASS — check 2, regression: the derivation without texts reproduces the archived listing v3 — c004: blocks 46 (expected 46), nodes 193 (expected 193), differences 0; e036: blocks 37 (expected 37), nodes 146 (expected 146), differences 0
- PASS — check 3, R4 label enforcement on the reviewed labels changes nothing — c004: R4 sentences 6, labels changed 0; e036: R4 sentences 4, labels changed 0
- PASS — check 4, structural metrics of `runs/experiments/judge_source_sonnet_v2_thinklow_r1_2026-09-17_1017` before R4 (judge labels as given vs listing v3) and after R4 (enforced vs listing v4, texts on both sides) — c004: block F1 0.921 → 0.923, next node 0.889 → 0.891, R4 openers agree 6 of 6; e036: block F1 0.930 → 0.946, next node 0.917 → 0.946, R4 openers agree 4 of 4; pooled: block F1 0.925 → 0.933, next node 0.901 → 0.916, R4 openers agree 10 of 10; judge labels changed by enforcement: 10 of 10 R4 sentences
- PASS — check 5, pytest on scripts/tests — exit code 0; last line: 161 passed in 1.87s

## Check 4: before and after R4

| scope | block F1 before → after | block hits / misses / extras before → after | next node after cut before → after | R4 openers reviewed / judge / agree (after) | node F1 before → after |
|---|---|---|---|---|---|
| c004 | 0.921 → 0.923 | 41 / 5 / 2 → 42 / 5 / 2 | 40 / 45 (0.889) → 41 / 46 (0.891) | 6 / 6 / 6 | 0.827 → 0.827 |
| e036 | 0.930 → 0.946 | 33 / 4 / 1 → 35 / 3 / 1 | 33 / 36 (0.917) → 35 / 37 (0.946) | 4 / 4 / 4 | 0.848 → 0.853 |
| pooled | 0.925 → 0.933 | 74 / 9 / 3 → 77 / 8 / 3 | 73 / 81 (0.901) → 76 / 83 (0.916) | 10 / 10 / 10 | 0.836 → 0.838 |
### Before R4 (judge labels as given; reviewed = listing v3; no texts)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| c004 | 46 / 43 | 41 / 5 (0) / 2 | 0.953 / 0.891 / 0.921 | 40 / 41 | 40 / 45 (0.889) | 165 / 28 / 41 | 0.827 | 144 / 193 (0.746) | 21 / 43 | 94 / 51 / 6 / 224 | 0.623 |
| e036 | 37 / 34 | 33 / 4 (1) / 1 | 0.971 / 0.892 / 0.930 | 33 / 33 | 33 / 36 (0.917) | 120 / 26 / 17 | 0.848 | 113 / 146 (0.774) | 7 / 39 | 46 / 22 / 0 / 186 | 0.676 |
| pooled | 83 / 77 | 74 / 9 (1) / 3 | 0.961 / 0.892 / 0.925 | 73 / 74 | 73 / 81 (0.901) | 285 / 54 / 58 | 0.836 | 257 / 339 (0.758) | 28 / 82 | 140 / 73 / 6 / 410 | 0.639 |

Next-node confusions (reviewed → judge, pooled): Planning → Restatement 5; Assumption → Planning 2; Planning → Reasoning 1
c004: missed reviewed openers at s43, s114, s116, s216, s227; extra judge openers at s291, s328
e036: missed reviewed openers at s19, s77, s96, s193; extra judge openers at s130
### After R4 (judge labels R4-enforced; reviewed = listing v4; texts on both sides)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | R4 openers reviewed / judge / agree | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c004 | 47 / 44 | 42 / 5 (1) / 2 | 0.955 / 0.894 / 0.923 | 41 / 42 | 6 / 6 / 6 | 41 / 46 (0.891) | 165 / 28 / 41 | 0.827 | 144 / 193 (0.746) | 21 / 43 | 94 / 51 / 6 / 224 | 0.623 |
| e036 | 38 / 36 | 35 / 3 (0) / 1 | 0.972 / 0.921 / 0.946 | 35 / 35 | 4 / 4 / 4 | 35 / 37 (0.946) | 122 / 25 / 17 | 0.853 | 115 / 147 (0.782) | 7 / 38 | 45 / 22 / 0 / 187 | 0.672 |
| pooled | 85 / 80 | 77 / 8 (1) / 3 | 0.963 / 0.906 / 0.933 | 76 / 77 | 10 / 10 / 10 | 76 / 83 (0.916) | 287 / 53 / 58 | 0.838 | 259 / 340 (0.762) | 28 / 81 | 139 / 73 / 6 / 411 | 0.638 |

Next-node confusions (reviewed → judge, pooled): Planning → Restatement 5; Assumption → Planning 2
c004: missed reviewed openers at s43, s114, s116, s216, s227; extra judge openers at s291, s328
e036: missed reviewed openers at s77, s96, s193; extra judge openers at s130
## R4 enforcement on the judge labels of the chosen run

| trace | s | action | changed | judge label before | after | text |
|---|---|---|---|---|---|---|
| c004 | 42 | prepended | True | Knowledge > world knowledge > famous problem (CRT) | Planning > initiate verification > Wait (doubt marker) \|\| Knowledge > world knowledge > famous problem (CRT) | But wait, the problem usually adds the constraint "The bat costs **\$1.00 more t |
| c004 | 137 | set_level3 | True | Planning > initiate verification | Planning > initiate verification > Wait (doubt marker) | ⏎⏎    **Wait, let's look at Option (F) "None of the above".** |
| c004 | 254 | set_level3 | True | Planning > initiate verification | Planning > initiate verification > Wait (doubt marker) | ⏎⏎    Wait, is there an argument for (E)? |
| c004 | 288 | set_level3 | True | Planning > initiate backtracking | Planning > initiate backtracking > Wait (doubt marker) | ⏎⏎    **Wait, hold on.** |
| c004 | 340 | set_level3 | True | Planning > initiate verification | Planning > initiate verification > Wait (doubt marker) | ⏎⏎    Wait, I should check if there's any weird interpretation of "A bat" (vampi |
| c004 | 352 | set_level3 | True | Planning > initiate verification | Planning > initiate verification > Wait (doubt marker) | ⏎⏎    **Wait, looking at the options again.** |
| e036 | 19 | prepended | True | Reasoning > comparison > prompt vs original text | Planning > initiate verification > Wait (doubt marker) \|\| Reasoning > comparison > prompt vs original text | (Wait, the classic problem says "The bat costs $1.00 *more* than the ball." But  |
| e036 | 71 | set_level3 | True | Planning > initiate backtracking | Planning > initiate backtracking > Wait (doubt marker) | ⏎   Wait, let's think about how these questions are typically framed in tests. |
| e036 | 100 | set_level3 | True | Planning > initiate verification | Planning > initiate verification > Wait (doubt marker) | ⏎⏎   Wait, let's double check option (C): |
| e036 | 179 | set_level3 | True | Planning > initiate verification | Planning > initiate verification > Wait (doubt marker) | ⏎   Wait, let's consider if the question might be from a specific source where ( |
## pytest output

```
........................................................................ [ 44%]
........................................................................ [ 89%]
.................                                                        [100%]
161 passed in 1.87s
```
