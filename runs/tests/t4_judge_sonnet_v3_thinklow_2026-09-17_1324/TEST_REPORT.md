# TEST_REPORT — t4_judge — 2026-09-17 13:24

Test of pipeline step (4/9), the judge on the two source traces (`scripts/s1_judge.py`, `scripts/derivation.py`), per pipeline v2 Section 9 item 6, with rule R4 in the derivation (decision 20). Git commit `cb372474119b2ee1a5b5caa031c6225a0cefd133`; model `claude-sonnet-5` (sonnet); thinking mode low (request parameters {"thinking": {"type": "adaptive", "display": "summarized"}, "output_config": {"effort": "low"}}, max_tokens 24000); temperature None (not sent: the model rejects sampling parameters); prompt v3 sha256 `e999f7081d5a285c4db1dcb4fb55f9eb5291b1ba536f770d1ad53a815e43f51a`; inventory sha256 `845dba31100f3d3104db3e69279f8a1e2a662c32ecd295fe4f7dec6a669df37b`; sentences `runs/tests/t2_split_2026-09-16_2224/sentences_source.jsonl`; reviewed listing `docs/shared/2026-09-17_source_traces_labeled_v4.md` (pre-R4 comparison: `archive/docs/shared/2026-09-16_source_traces_labeled_v3.md`). Repeats: 1. Run folders: `runs/experiments/judge_source_sonnet_v3_thinklow_2026-09-17_1324`.

## Result: PASS (7/7 checks passed)

## Checks

- PASS — check 1, derivation gate under R4 on the reviewed labels of listing v4 (offline) — e036: 254 sentences; blocks 38 derived vs 38 listed; nodes 147 vs 147; interval differences 0, opener rule/label differences 0, name differences 0; R4 openers at s19, s71, s100, s179 (listing names with a '(1)' count stripped: 98); c004: 375 sentences; blocks 47 derived vs 47 listed; nodes 193 vs 193; interval differences 0, opener rule/label differences 0, name differences 0; R4 openers at s42, s137, s254, s288, s340, s352 (listing names with a '(1)' count stripped: 121)
- PASS — check 2, dry run (requests built, nothing called) — e036: 254 sentences, about 9079 input tokens (characters/4); every index exactly once in the user message: True; c004: 375 sentences, about 11104 input tokens (characters/4); every index exactly once in the user message: True; thinking parameters in the request: {"thinking": {"type": "adaptive", "display": "summarized"}, "output_config": {"effort": "low"}}; requests written to dry_run/requests/
- PASS — check 3, run 1, e036 judged — attempts 1, valid True, model echoed 'claude-sonnet-5', stop reasons ['end_turn'], final end_turn; tokens input 5635, cache read 0, cache write 8584, thinking 7881, output 9544 (thinking included); <think> tag in text blocks per attempt [False]; thinking text chars per attempt [5060]; cost $0.128170; judge nodes 138 / blocks 35 vs reviewed 147 / 38 (R4 on both sides); judge labels changed by R4 enforcement 0; agreement vs reviewed v4 (this trace; judge labels R4-enforced): Level 1 exact 0.878 kappa 0.855, Level 2 exact 0.795 kappa 0.787, Level 3 exact 0.776 kappa 0.769; residue rows 57; as given (before enforcement): Level 1 kappa 0.855, full-path exact 0.776
- PASS — check 4, run 1, c004 judged — attempts 1, valid True, model echoed 'claude-sonnet-5', stop reasons ['end_turn'], final end_turn; tokens input 9403, cache read 8584, cache write 0, thinking 16196, output 18878 (thinking included); <think> tag in text blocks per attempt [False]; thinking text chars per attempt [18804]; cost $0.209303; judge nodes 207 / blocks 43 vs reviewed 193 / 47 (R4 on both sides); judge labels changed by R4 enforcement 0; agreement vs reviewed v4 (this trace; judge labels R4-enforced): Level 1 exact 0.808 kappa 0.761, Level 2 exact 0.667 kappa 0.652, Level 3 exact 0.656 kappa 0.649; residue rows 129; as given (before enforcement): Level 1 kappa 0.761, full-path exact 0.656
- PASS — check 5, run 1, agreement vs reviewed v4 over both traces (judge labels R4-enforced) — 629 sentences; Level 1: exact 0.836, Jaccard 0.844, kappa 0.805; Level 2: exact 0.719, Jaccard 0.724, kappa 0.708; Level 3: exact 0.704, Jaccard 0.711, kappa 0.699; residue rows 186; as given (before enforcement): Level 1 kappa 0.805; Level 2 kappa 0.708; Level 3 kappa 0.699; cost of this run $0.337473
- PASS — check 6, run 1, structural metrics vs reviewed (pooled), after R4 → before R4 in brackets — block openers hits 75 [73] / misses 10 [10] (near 1) / extras 3 [4], F1 0.920 [0.912], rule agrees on 75 of 75 hits; R4 openers reviewed / judge / agree 10 / 10 / 10 (must coincide); next node after the reviewed cuts 77 / 83 (0.928) [75 / 81 (0.926)]; node ends F1 0.893 [0.893], matched nodes Level 1 agree 0.829, reviewed nodes split 25 / merged 52; sentences L1 wrong 103 / L2 wrong 74 / L3 wrong 9 / all right 443 (L1 share of disagreements 0.554); structural_source.csv and structural_source_before_r4.csv written
- PASS — check 7, pytest on scripts/tests — exit code 0; last line: 161 passed in 2.07s

## Run 1: agreement judge (R4-enforced) vs reviewed v4 (both traces)

| level | n | exact-match rate | mean Jaccard | kappa (primary label) | primary agreement |
|---|---|---|---|---|---|
| Level 1 | 629 | 0.8362 | 0.8439 | 0.8048 | 0.8474 |
| Level 1 > Level 2 | 629 | 0.7186 | 0.7244 | 0.7078 | 0.7266 |
| full path | 629 | 0.7043 | 0.7107 | 0.6992 | 0.7138 |

| level | label | n_reviewed | n_judge | tp | precision | recall | F1 |
|---|---|---|---|---|---|---|---|
| 1 | Assumption | 7 | 5 | 4 | 0.800 | 0.571 | 0.667 |
| 1 | Conclusion | 40 | 62 | 36 | 0.581 | 0.900 | 0.706 |
| 1 | Example | 22 | 31 | 21 | 0.677 | 0.955 | 0.792 |
| 1 | Knowledge | 30 | 31 | 24 | 0.774 | 0.800 | 0.787 |
| 1 | Planning | 178 | 168 | 163 | 0.970 | 0.916 | 0.942 |
| 1 | Reasoning | 206 | 188 | 167 | 0.888 | 0.811 | 0.848 |
| 1 | Reflection | 36 | 34 | 26 | 0.765 | 0.722 | 0.743 |
| 1 | Restatement | 123 | 114 | 98 | 0.860 | 0.797 | 0.827 |
| 2 | Assumption > assuming a missing premise by common practice | 1 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Assumption > assuming an uncertain fact | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Assumption > branching (case split) | 5 | 4 | 3 | 0.750 | 0.600 | 0.667 |
| 2 | Conclusion > final answer | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 2 | Conclusion > intermediate conclusion | 37 | 59 | 33 | 0.559 | 0.892 | 0.687 |
| 2 | Example > non-exhaustive listing | 17 | 26 | 16 | 0.615 | 0.941 | 0.744 |
| 2 | Example > rhetorical example | 5 | 5 | 5 | 1.000 | 1.000 | 1.000 |
| 2 | Knowledge > commonsense | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Knowledge > concept or definition | 6 | 5 | 5 | 1.000 | 0.833 | 0.909 |
| 2 | Knowledge > self-knowledge | 5 | 4 | 4 | 1.000 | 0.800 | 0.889 |
| 2 | Knowledge > world knowledge | 16 | 22 | 14 | 0.636 | 0.875 | 0.737 |
| 2 | Planning > announce output | 16 | 18 | 16 | 0.889 | 1.000 | 0.941 |
| 2 | Planning > announce the conclusion | 5 | 3 | 3 | 1.000 | 0.600 | 0.750 |
| 2 | Planning > global plan | 35 | 42 | 32 | 0.762 | 0.914 | 0.831 |
| 2 | Planning > initiate backtracking | 8 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Planning > initiate verification | 43 | 36 | 29 | 0.806 | 0.674 | 0.734 |
| 2 | Planning > local plan | 71 | 68 | 62 | 0.912 | 0.873 | 0.892 |
| 2 | Reasoning > calculation | 35 | 15 | 12 | 0.800 | 0.343 | 0.480 |
| 2 | Reasoning > commonsense reasoning | 12 | 11 | 11 | 1.000 | 0.917 | 0.957 |
| 2 | Reasoning > comparison | 17 | 20 | 12 | 0.600 | 0.706 | 0.649 |
| 2 | Reasoning > defining symbols | 15 | 8 | 6 | 0.750 | 0.400 | 0.522 |
| 2 | Reasoning > hedge word analysis | 13 | 2 | 2 | 1.000 | 0.154 | 0.267 |
| 2 | Reasoning > logical reasoning | 38 | 49 | 25 | 0.510 | 0.658 | 0.575 |
| 2 | Reasoning > option evaluation | 45 | 70 | 36 | 0.514 | 0.800 | 0.626 |
| 2 | Reasoning > speculation | 32 | 13 | 11 | 0.846 | 0.344 | 0.489 |
| 2 | Reflection > emotion or impression | 1 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Reflection > meta-evaluation of a step | 35 | 32 | 25 | 0.781 | 0.714 | 0.746 |
| 2 | Reflection > unspecified | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Restatement > rephrasing an earlier sentence | 70 | 57 | 48 | 0.842 | 0.686 | 0.756 |
| 2 | Restatement > rephrasing the prompt | 53 | 57 | 49 | 0.860 | 0.925 | 0.891 |
| 3 | Assumption > assuming a missing premise by common practice > "$1.00 more" | 1 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > assuming an uncertain fact | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > branching (case split) | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > branching (case split) > algebra | 4 | 4 | 3 | 0.750 | 0.750 | 0.750 |
| 3 | Conclusion > final answer | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 3 | Conclusion > intermediate conclusion | 37 | 59 | 33 | 0.559 | 0.892 | 0.687 |
| 3 | Example > non-exhaustive listing > algebra | 17 | 26 | 16 | 0.615 | 0.941 | 0.744 |
| 3 | Example > rhetorical example | 5 | 5 | 5 | 1.000 | 1.000 | 1.000 |
| 3 | Knowledge > commonsense | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > concept or definition > well-posedness | 6 | 5 | 5 | 1.000 | 0.833 | 0.909 |
| 3 | Knowledge > self-knowledge > evaluation context | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| 3 | Knowledge > self-knowledge > role | 4 | 3 | 3 | 1.000 | 0.750 | 0.857 |
| 3 | Knowledge > world knowledge | 0 | 5 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > world knowledge > famous problem (CRT) | 16 | 17 | 12 | 0.706 | 0.750 | 0.727 |
| 3 | Planning > announce output | 16 | 18 | 16 | 0.889 | 1.000 | 0.941 |
| 3 | Planning > announce the conclusion | 5 | 3 | 3 | 1.000 | 0.600 | 0.750 |
| 3 | Planning > global plan | 35 | 42 | 32 | 0.762 | 0.914 | 0.831 |
| 3 | Planning > initiate backtracking | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Planning > initiate backtracking > Wait (doubt marker) | 3 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Planning > initiate verification | 36 | 27 | 23 | 0.852 | 0.639 | 0.730 |
| 3 | Planning > initiate verification > Wait (doubt marker) | 7 | 9 | 6 | 0.667 | 0.857 | 0.750 |
| 3 | Planning > local plan | 71 | 68 | 62 | 0.912 | 0.873 | 0.892 |
| 3 | Reasoning > calculation > algebra | 35 | 15 | 12 | 0.800 | 0.343 | 0.480 |
| 3 | Reasoning > commonsense reasoning | 12 | 11 | 11 | 1.000 | 0.917 | 0.957 |
| 3 | Reasoning > comparison > option vs option | 8 | 9 | 5 | 0.556 | 0.625 | 0.588 |
| 3 | Reasoning > comparison > prompt vs original text | 9 | 11 | 7 | 0.636 | 0.778 | 0.700 |
| 3 | Reasoning > defining symbols > algebra | 15 | 8 | 6 | 0.750 | 0.400 | 0.522 |
| 3 | Reasoning > hedge word analysis > everyday reading | 4 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > hedge word analysis > mathematical reading | 8 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > hedge word analysis > undecided | 1 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > logical reasoning | 20 | 32 | 17 | 0.531 | 0.850 | 0.654 |
| 3 | Reasoning > logical reasoning > algebra | 18 | 17 | 5 | 0.294 | 0.278 | 0.286 |
| 3 | Reasoning > option evaluation > (A) | 11 | 10 | 7 | 0.700 | 0.636 | 0.667 |
| 3 | Reasoning > option evaluation > (B) | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > option evaluation > (C) | 25 | 40 | 22 | 0.550 | 0.880 | 0.677 |
| 3 | Reasoning > option evaluation > (E) | 9 | 12 | 7 | 0.583 | 0.778 | 0.667 |
| 3 | Reasoning > option evaluation > (F) | 0 | 7 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > speculation | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > speculation > intent of the question writer | 32 | 12 | 11 | 0.917 | 0.344 | 0.500 |
| 3 | Reflection > emotion or impression | 1 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step | 14 | 12 | 12 | 1.000 | 0.857 | 0.923 |
| 3 | Reflection > meta-evaluation of a step > option (A) | 0 | 3 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step > option (B) | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| 3 | Reflection > meta-evaluation of a step > option (C) | 7 | 5 | 3 | 0.600 | 0.429 | 0.500 |
| 3 | Reflection > meta-evaluation of a step > option (D) | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 3 | Reflection > meta-evaluation of a step > option (E) | 5 | 3 | 2 | 0.667 | 0.400 | 0.500 |
| 3 | Reflection > meta-evaluation of a step > option (F) | 3 | 4 | 3 | 0.750 | 1.000 | 0.857 |
| 3 | Reflection > unspecified | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Restatement > rephrasing an earlier sentence | 70 | 57 | 48 | 0.842 | 0.686 | 0.756 |
| 3 | Restatement > rephrasing the prompt > answer-format instruction | 7 | 9 | 7 | 0.778 | 1.000 | 0.875 |
| 3 | Restatement > rephrasing the prompt > option text | 24 | 27 | 20 | 0.741 | 0.833 | 0.784 |
| 3 | Restatement > rephrasing the prompt > question text | 22 | 21 | 20 | 0.952 | 0.909 | 0.930 |

### Twenty most frequent confusion pairs at Level 1 (reference → other, primary label)

| reference | other | count |
|---|---|---|
| Reasoning | Conclusion | 19 |
| Restatement | Example | 10 |
| Planning | Restatement | 8 |
| Reasoning | Restatement | 8 |
| Reflection | Reasoning | 6 |
| Reasoning | Reflection | 5 |
| Knowledge | Reasoning | 5 |
| Restatement | Reasoning | 4 |
| Restatement | Conclusion | 4 |
| Restatement | Knowledge | 4 |
| Conclusion | Reasoning | 3 |
| Planning | Reasoning | 3 |
| Assumption | Planning | 2 |
| Restatement | Reflection | 2 |
| Reasoning | Planning | 2 |
| Reflection | Conclusion | 2 |
| Restatement | Planning | 1 |
| Reasoning | Knowledge | 1 |
| Reasoning | Assumption | 1 |
| Conclusion | Restatement | 1 |

### Twenty most frequent confusion pairs at Level 2 (reference → other, primary label)

| reference | other | count |
|---|---|---|
| Reasoning > calculation | Reasoning > logical reasoning | 15 |
| Reasoning > logical reasoning | Conclusion > intermediate conclusion | 11 |
| Reasoning > hedge word analysis | Reasoning > option evaluation | 10 |
| Reasoning > speculation | Reasoning > option evaluation | 10 |
| Restatement > rephrasing an earlier sentence | Example > non-exhaustive listing | 10 |
| Planning > initiate verification | Planning > global plan | 7 |
| Planning > local plan | Restatement > rephrasing the prompt | 6 |
| Reasoning > defining symbols | Restatement > rephrasing an earlier sentence | 6 |
| Planning > initiate backtracking | Planning > initiate verification | 6 |
| Reasoning > speculation | Reasoning > logical reasoning | 6 |
| Reflection > meta-evaluation of a step | Reasoning > option evaluation | 5 |
| Reasoning > option evaluation | Conclusion > intermediate conclusion | 4 |
| Restatement > rephrasing an earlier sentence | Conclusion > intermediate conclusion | 4 |
| Restatement > rephrasing an earlier sentence | Knowledge > world knowledge | 4 |
| Conclusion > intermediate conclusion | Reasoning > option evaluation | 3 |
| Reasoning > calculation | Conclusion > intermediate conclusion | 3 |
| Reasoning > option evaluation | Reflection > meta-evaluation of a step | 3 |
| Restatement > rephrasing the prompt | Reasoning > option evaluation | 2 |
| Planning > initiate verification | Planning > local plan | 2 |
| Reasoning > speculation | Reasoning > comparison | 2 |

### Residue: 186 sentences whose full-path set differs (first 30)

| trace | s | reference | other | text |
|---|---|---|---|---|
| c004 | 12 | Restatement > rephrasing the prompt > question text | Planning > local plan | ⏎    *   *Goal:* Find cost of Ball. |
| c004 | 17 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | ⏎        *   Does Bat > Ball? |
| c004 | 18 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | \$1.05 > \$0.05. |
| c004 | 20 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | ⏎        *   Is the sum \$1.10? |
| c004 | 22 | Reasoning > logical reasoning > algebra | Conclusion > intermediate conclusion | ⏎        *   *Result:* \$0.05 is a *possible* solution. |
| c004 | 25 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | ⏎        *   Does Bat > Ball? |
| c004 | 26 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | \$1.09 > \$0.01. |
| c004 | 28 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | ⏎        *   Is the sum \$1.10? |
| c004 | 30 | Reasoning > logical reasoning > algebra | Conclusion > intermediate conclusion | ⏎        *   *Result:* \$0.01 is *also* a possible solution. |
| c004 | 33 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | ⏎        *   Does Bat > Ball? |
| c004 | 34 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | \$0.55 is not greater than \$0.55 (it's equal). |
| c004 | 35 | Reasoning > logical reasoning > algebra | Conclusion > intermediate conclusion | ⏎        *   *Result:* \$0.55 is not a solution. |
| c004 | 40 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | Why? |
| c004 | 41 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | Because \$1.00 + \$0.10 = \$1.10. |
| c004 | 42 | Planning > initiate verification > Wait (doubt marker) || Knowledge > world knowledge > famous problem (CRT) | Planning > initiate verification > Wait (doubt marker) || Knowledge > world knowledge | But wait, the problem usually adds the constraint "The bat costs **\$1.00 more than the ball**." |
| c004 | 46 | Reasoning > logical reasoning > algebra | Conclusion > intermediate conclusion | ⏎    *   *Implication:* Without the specific difference constraint (Bat = Ball + 1.00), there are infinite solutions. |
| c004 | 60 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎⏎    *   *(A) It is \$0.05*: |
| c004 | 64 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(B) It is probably \$0.05*: |
| c004 | 65 | Reasoning > hedge word analysis > mathematical reading | Reasoning > hedge word analysis > undecided | "Probably" implies probability. |
| c004 | 66 | Reasoning > hedge word analysis > mathematical reading | Reasoning > hedge word analysis > undecided | Unless there's a distribution of prices given, we can't assign probability. |
| c004 | 67 | Reasoning > hedge word analysis > everyday reading || Reflection > meta-evaluation of a step > option (B) | Reasoning > option evaluation > (B) | However, in the context of riddles, this option acknowledges the likely intent of the user (referring to the famous riddle) while acknowledging the missing constraint. |
| c004 | 68 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(C) There is not enough information, but the answer is most likely \$0.05*: |
| c004 | 69 | Reflection > meta-evaluation of a step > option (C) | Reasoning > option evaluation > (C) | This is logically the most accurate description. |
| c004 | 72 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(D) I am not sure*: |
| c004 | 74 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(E) The question is not well posed*: |
| c004 | 75 | Reasoning > option evaluation > (E) || Knowledge > concept or definition > well-posedness | Reasoning > option evaluation > (E) | Mathematically true (underdetermined), but "not well posed" usually implies no solution or non-unique solution in a way that makes it unsolvable. |
| c004 | 77 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(F) None of the above*: |
| c004 | 92 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | If $b + B = 1.10$ and $B > b$ (where $B$ is bat, $b$ is ball), then $b$ can be any value in $(0, 0.55)$. |
| c004 | 96 | Restatement > rephrasing the prompt > option text | Reasoning > option evaluation > (C) | It then adds "...but the answer is most likely \$0.05". |
| c004 | 97 | Reasoning > hedge word analysis > everyday reading | Reasoning > option evaluation > (C) | This acknowledges the cultural context/intent of the riddle. |
### Run 1: structural metrics judge vs reviewed, after R4 (enforced judge labels vs listing v4, texts on both sides)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | R4 openers reviewed / judge / agree | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| e036 | 38 / 35 | 34 / 4 (0) / 1 | 0.971 / 0.895 / 0.932 | 34 / 34 | 4 / 4 / 4 | 34 / 37 (0.919) | 132 / 15 / 6 | 0.926 | 122 / 147 (0.830) | 6 / 25 | 31 / 21 / 5 / 197 | 0.544 |
| c004 | 47 / 43 | 41 / 6 (1) / 2 | 0.953 / 0.872 / 0.911 | 41 / 41 | 6 / 6 / 6 | 43 / 46 (0.935) | 174 / 19 / 33 | 0.870 | 160 / 193 (0.829) | 19 / 27 | 72 / 53 / 4 / 246 | 0.558 |
| pooled | 85 / 78 | 75 / 10 (1) / 3 | 0.962 / 0.882 / 0.920 | 75 / 75 | 10 / 10 / 10 | 77 / 83 (0.928) | 306 / 34 / 39 | 0.893 | 282 / 340 (0.829) | 25 / 52 | 103 / 74 / 9 / 443 | 0.554 |

Next-node confusions (reviewed → judge, pooled): Planning → Reasoning 2; Planning → Restatement 2; Assumption → Planning 2
e036: missed reviewed openers at s77, s96, s182, s193; extra judge openers at s84
c004: missed reviewed openers at s13, s114, s116, s216, s227, s356; extra judge openers at s12, s111
### Run 1: structural metrics judge vs reviewed, before R4 (labels as given vs listing v3, no texts; comparable with the v2 runs)

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e036 | 37 / 34 | 33 / 4 (0) / 1 | 0.971 / 0.892 / 0.930 | 33 / 33 | 33 / 36 (0.917) | 131 / 15 / 6 | 0.926 | 121 / 146 (0.829) | 6 / 25 | 31 / 21 / 7 / 195 | 0.525 |
| c004 | 46 / 43 | 40 / 6 (1) / 3 | 0.930 / 0.870 / 0.899 | 40 / 40 | 42 / 45 (0.933) | 174 / 19 / 33 | 0.870 | 159 / 193 (0.824) | 19 / 27 | 73 / 53 / 5 / 244 | 0.557 |
| pooled | 83 / 77 | 73 / 10 (1) / 4 | 0.948 / 0.880 / 0.912 | 73 / 73 | 75 / 81 (0.926) | 305 / 34 / 39 | 0.893 | 280 / 339 (0.826) | 25 / 52 | 104 / 74 / 12 / 439 | 0.547 |

Next-node confusions (reviewed → judge, pooled): Planning → Reasoning 2; Planning → Restatement 2; Assumption → Planning 2
e036: missed reviewed openers at s77, s96, s182, s193; extra judge openers at s84
c004: missed reviewed openers at s13, s114, s116, s216, s227, s356; extra judge openers at s12, s42, s111
## pytest output

```
........................................................................ [ 44%]
........................................................................ [ 89%]
.................                                                        [100%]
161 passed in 2.07s
```
