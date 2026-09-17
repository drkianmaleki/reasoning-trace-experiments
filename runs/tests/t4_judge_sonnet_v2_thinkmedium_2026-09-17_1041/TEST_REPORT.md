# TEST_REPORT — t4_judge — 2026-09-17 10:41

Test of pipeline step (4/9), the judge on the two source traces (`scripts/s1_judge.py`, `scripts/derivation.py`), per pipeline v1 Section 9 item 6. Git commit `5eed56dcbf8323af99574d5a82ff350e0a808250`; model `claude-sonnet-5` (sonnet); thinking mode medium (request parameters {"thinking": {"type": "adaptive", "display": "summarized"}, "output_config": {"effort": "medium"}}, max_tokens 24000); temperature None (not sent: the model rejects sampling parameters); prompt v2 sha256 `98ac17659798c184bc75fba6336007fb87e0b771e5272dfa05bdc90781b2a65c`; inventory sha256 `51c5d0d142863a1d6461bcc871b08401f80c02abce45c31445de2cae07798ba2`; sentences `runs/tests/t2_split_2026-09-16_2224/sentences_source.jsonl`. Repeats: 1. Run folders: `runs/experiments/judge_source_sonnet_v2_thinkmedium_2026-09-17_1041`.

## Result: PASS (7/7 checks passed)

## Checks

- PASS — check 1, derivation gate on the reviewed labels (offline) — e036: 254 sentences; blocks 37 derived vs 37 listed; nodes 146 vs 146; interval differences 0, opener rule/label differences 0, name differences 0 (listing names with a '(1)' count stripped: 97); c004: 375 sentences; blocks 46 derived vs 46 listed; nodes 193 vs 193; interval differences 0, opener rule/label differences 0, name differences 0 (listing names with a '(1)' count stripped: 121)
- PASS — check 2, dry run (requests built, nothing called) — e036: 254 sentences, about 8774 input tokens (characters/4); every index exactly once in the user message: True; c004: 375 sentences, about 10799 input tokens (characters/4); every index exactly once in the user message: True; thinking parameters in the request: {"thinking": {"type": "adaptive", "display": "summarized"}, "output_config": {"effort": "medium"}}; requests written to dry_run/requests/
- PASS — check 3, run 1, e036 judged — attempts 1, valid True, model echoed 'claude-sonnet-5', stop reasons ['end_turn'], final end_turn; tokens input 5635, cache read 0, cache write 8109, thinking 9886, output 11533 (thinking included); <think> tag in text blocks per attempt [False]; thinking text chars per attempt [8273]; cost $0.146872; judge nodes 140 / blocks 34 vs reviewed 146 / 37; agreement vs reviewed (this trace): Level 1 exact 0.862 kappa 0.831, Level 2 exact 0.799 kappa 0.791, Level 3 exact 0.772 kappa 0.765; residue rows 58
- PASS — check 4, run 1, c004 judged — attempts 1, valid True, model echoed 'claude-sonnet-5', stop reasons ['end_turn'], final end_turn; tokens input 9403, cache read 8109, cache write 0, thinking 17480, output 20208 (thinking included); <think> tag in text blocks per attempt [False]; thinking text chars per attempt [16625]; cost $0.222508; judge nodes 221 / blocks 48 vs reviewed 193 / 46; agreement vs reviewed (this trace): Level 1 exact 0.808 kappa 0.759, Level 2 exact 0.683 kappa 0.664, Level 3 exact 0.672 kappa 0.658; residue rows 123
- PASS — check 5, run 1, agreement vs reviewed over both traces — 629 sentences; Level 1: exact 0.830, Jaccard 0.835, kappa 0.793; Level 2: exact 0.730, Jaccard 0.733, kappa 0.716; Level 3: exact 0.712, Jaccard 0.716, kappa 0.702; residue rows 181; cost of this run $0.369380
- PASS — check 6, run 1, structural metrics vs reviewed (pooled) — block openers hits 77 / misses 6 (near 2) / extras 5, F1 0.933, rule agrees on 76 of 77 hits; next node after the reviewed cuts 77 / 81 (0.951); node ends F1 0.871, matched nodes Level 1 agree 0.847, reviewed nodes split 31 / merged 49; sentences L1 wrong 107 / L2 wrong 63 / L3 wrong 11 / all right 448 (L1 share of disagreements 0.591); structural_source.csv written
- PASS — check 7, pytest on scripts/tests — exit code 0; last line: 102 passed in 0.33s

## Run 1: agreement judge vs reviewed (both traces)

| level | n | exact-match rate | mean Jaccard | kappa (primary label) | primary agreement |
|---|---|---|---|---|---|
| Level 1 | 629 | 0.8299 | 0.8352 | 0.7934 | 0.8378 |
| Level 1 > Level 2 | 629 | 0.7297 | 0.7332 | 0.7164 | 0.7345 |
| full path | 629 | 0.7122 | 0.7157 | 0.7022 | 0.7170 |

| level | label | n_reviewed | n_judge | tp | precision | recall | F1 |
|---|---|---|---|---|---|---|---|
| 1 | Assumption | 7 | 10 | 5 | 0.500 | 0.714 | 0.588 |
| 1 | Conclusion | 40 | 61 | 36 | 0.590 | 0.900 | 0.713 |
| 1 | Example | 22 | 26 | 21 | 0.808 | 0.955 | 0.875 |
| 1 | Knowledge | 30 | 32 | 27 | 0.844 | 0.900 | 0.871 |
| 1 | Planning | 177 | 175 | 162 | 0.926 | 0.915 | 0.920 |
| 1 | Reasoning | 206 | 177 | 157 | 0.887 | 0.762 | 0.820 |
| 1 | Reflection | 36 | 36 | 27 | 0.750 | 0.750 | 0.750 |
| 1 | Restatement | 123 | 117 | 98 | 0.838 | 0.797 | 0.817 |
| 2 | Assumption > assuming a missing premise by common practice | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Assumption > assuming an uncertain fact | 1 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Assumption > branching (case split) | 5 | 9 | 4 | 0.444 | 0.800 | 0.571 |
| 2 | Conclusion > final answer | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 2 | Conclusion > intermediate conclusion | 37 | 58 | 33 | 0.569 | 0.892 | 0.695 |
| 2 | Example > non-exhaustive listing | 17 | 21 | 16 | 0.762 | 0.941 | 0.842 |
| 2 | Example > rhetorical example | 5 | 5 | 5 | 1.000 | 1.000 | 1.000 |
| 2 | Knowledge > commonsense | 3 | 1 | 1 | 1.000 | 0.333 | 0.500 |
| 2 | Knowledge > concept or definition | 6 | 5 | 5 | 1.000 | 0.833 | 0.909 |
| 2 | Knowledge > self-knowledge | 5 | 5 | 5 | 1.000 | 1.000 | 1.000 |
| 2 | Knowledge > world knowledge | 16 | 21 | 15 | 0.714 | 0.938 | 0.811 |
| 2 | Planning > announce output | 16 | 17 | 16 | 0.941 | 1.000 | 0.970 |
| 2 | Planning > announce the conclusion | 5 | 5 | 4 | 0.800 | 0.800 | 0.800 |
| 2 | Planning > global plan | 35 | 34 | 31 | 0.912 | 0.886 | 0.899 |
| 2 | Planning > initiate backtracking | 8 | 8 | 2 | 0.250 | 0.250 | 0.250 |
| 2 | Planning > initiate verification | 42 | 34 | 30 | 0.882 | 0.714 | 0.789 |
| 2 | Planning > local plan | 71 | 77 | 62 | 0.805 | 0.873 | 0.838 |
| 2 | Reasoning > calculation | 35 | 17 | 14 | 0.824 | 0.400 | 0.538 |
| 2 | Reasoning > commonsense reasoning | 12 | 13 | 11 | 0.846 | 0.917 | 0.880 |
| 2 | Reasoning > comparison | 17 | 15 | 11 | 0.733 | 0.647 | 0.688 |
| 2 | Reasoning > defining symbols | 15 | 8 | 6 | 0.750 | 0.400 | 0.522 |
| 2 | Reasoning > hedge word analysis | 13 | 3 | 3 | 1.000 | 0.231 | 0.375 |
| 2 | Reasoning > logical reasoning | 38 | 52 | 25 | 0.481 | 0.658 | 0.556 |
| 2 | Reasoning > option evaluation | 45 | 57 | 29 | 0.509 | 0.644 | 0.569 |
| 2 | Reasoning > speculation | 32 | 12 | 12 | 1.000 | 0.375 | 0.545 |
| 2 | Reflection > emotion or impression | 1 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Reflection > meta-evaluation of a step | 35 | 34 | 27 | 0.794 | 0.771 | 0.783 |
| 2 | Restatement > rephrasing an earlier sentence | 70 | 55 | 45 | 0.818 | 0.643 | 0.720 |
| 2 | Restatement > rephrasing the prompt | 53 | 62 | 52 | 0.839 | 0.981 | 0.904 |
| 3 | Assumption > assuming a missing premise by common practice > "$1.00 more" | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > assuming an uncertain fact | 1 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > branching (case split) | 1 | 5 | 1 | 0.200 | 1.000 | 0.333 |
| 3 | Assumption > branching (case split) > algebra | 4 | 4 | 3 | 0.750 | 0.750 | 0.750 |
| 3 | Conclusion > final answer | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 3 | Conclusion > intermediate conclusion | 37 | 58 | 33 | 0.569 | 0.892 | 0.695 |
| 3 | Example > non-exhaustive listing > algebra | 17 | 21 | 16 | 0.762 | 0.941 | 0.842 |
| 3 | Example > rhetorical example | 5 | 5 | 5 | 1.000 | 1.000 | 1.000 |
| 3 | Knowledge > commonsense | 3 | 1 | 1 | 1.000 | 0.333 | 0.500 |
| 3 | Knowledge > concept or definition > well-posedness | 6 | 5 | 5 | 1.000 | 0.833 | 0.909 |
| 3 | Knowledge > self-knowledge > evaluation context | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| 3 | Knowledge > self-knowledge > role | 4 | 4 | 4 | 1.000 | 1.000 | 1.000 |
| 3 | Knowledge > world knowledge | 0 | 6 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > world knowledge > famous problem (CRT) | 16 | 15 | 12 | 0.800 | 0.750 | 0.774 |
| 3 | Planning > announce output | 16 | 17 | 16 | 0.941 | 1.000 | 0.970 |
| 3 | Planning > announce the conclusion | 5 | 5 | 4 | 0.800 | 0.800 | 0.800 |
| 3 | Planning > global plan | 35 | 34 | 31 | 0.912 | 0.886 | 0.899 |
| 3 | Planning > initiate backtracking | 8 | 8 | 2 | 0.250 | 0.250 | 0.250 |
| 3 | Planning > initiate verification | 42 | 34 | 30 | 0.882 | 0.714 | 0.789 |
| 3 | Planning > local plan | 71 | 77 | 62 | 0.805 | 0.873 | 0.838 |
| 3 | Reasoning > calculation > algebra | 35 | 17 | 14 | 0.824 | 0.400 | 0.538 |
| 3 | Reasoning > commonsense reasoning | 12 | 13 | 11 | 0.846 | 0.917 | 0.880 |
| 3 | Reasoning > comparison > option vs option | 8 | 10 | 6 | 0.600 | 0.750 | 0.667 |
| 3 | Reasoning > comparison > prompt vs original text | 9 | 5 | 5 | 1.000 | 0.556 | 0.714 |
| 3 | Reasoning > defining symbols > algebra | 15 | 8 | 6 | 0.750 | 0.400 | 0.522 |
| 3 | Reasoning > hedge word analysis > everyday reading | 4 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > hedge word analysis > mathematical reading | 8 | 2 | 2 | 1.000 | 0.250 | 0.400 |
| 3 | Reasoning > hedge word analysis > undecided | 1 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > logical reasoning | 20 | 26 | 14 | 0.538 | 0.700 | 0.609 |
| 3 | Reasoning > logical reasoning > algebra | 18 | 26 | 6 | 0.231 | 0.333 | 0.273 |
| 3 | Reasoning > option evaluation > (A) | 11 | 9 | 6 | 0.667 | 0.545 | 0.600 |
| 3 | Reasoning > option evaluation > (B) | 0 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > option evaluation > (C) | 25 | 26 | 16 | 0.615 | 0.640 | 0.627 |
| 3 | Reasoning > option evaluation > (E) | 9 | 16 | 7 | 0.438 | 0.778 | 0.560 |
| 3 | Reasoning > option evaluation > (F) | 0 | 4 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > speculation > intent of the question writer | 32 | 12 | 12 | 1.000 | 0.375 | 0.545 |
| 3 | Reflection > emotion or impression | 1 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step | 14 | 16 | 14 | 0.875 | 1.000 | 0.933 |
| 3 | Reflection > meta-evaluation of a step > option (A) | 0 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step > option (B) | 3 | 1 | 1 | 1.000 | 0.333 | 0.500 |
| 3 | Reflection > meta-evaluation of a step > option (C) | 7 | 6 | 4 | 0.667 | 0.571 | 0.615 |
| 3 | Reflection > meta-evaluation of a step > option (D) | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 3 | Reflection > meta-evaluation of a step > option (E) | 5 | 3 | 2 | 0.667 | 0.400 | 0.500 |
| 3 | Reflection > meta-evaluation of a step > option (F) | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 3 | Restatement > rephrasing an earlier sentence | 70 | 55 | 45 | 0.818 | 0.643 | 0.720 |
| 3 | Restatement > rephrasing the prompt | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Restatement > rephrasing the prompt > answer-format instruction | 7 | 9 | 7 | 0.778 | 1.000 | 0.875 |
| 3 | Restatement > rephrasing the prompt > option text | 24 | 30 | 22 | 0.733 | 0.917 | 0.815 |
| 3 | Restatement > rephrasing the prompt > question text | 22 | 22 | 21 | 0.955 | 0.955 | 0.955 |

### Twenty most frequent confusion pairs at Level 1 (reference → other, primary label)

| reference | other | count |
|---|---|---|
| Reasoning | Conclusion | 19 |
| Reasoning | Restatement | 11 |
| Planning | Restatement | 8 |
| Restatement | Reasoning | 8 |
| Reflection | Reasoning | 7 |
| Reasoning | Reflection | 6 |
| Reasoning | Planning | 6 |
| Restatement | Example | 5 |
| Reasoning | Assumption | 4 |
| Restatement | Planning | 4 |
| Restatement | Conclusion | 4 |
| Restatement | Knowledge | 2 |
| Restatement | Reflection | 2 |
| Planning | Reasoning | 2 |
| Conclusion | Reasoning | 2 |
| Knowledge | Planning | 1 |
| Assumption | Planning | 1 |
| Example | Reasoning | 1 |
| Planning | Knowledge | 1 |
| Conclusion | Restatement | 1 |

### Twenty most frequent confusion pairs at Level 2 (reference → other, primary label)

| reference | other | count |
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
| Reflection > meta-evaluation of a step | Reasoning > option evaluation | 4 |
| Reasoning > option evaluation | Planning > local plan | 4 |
| Planning > initiate backtracking | Planning > initiate verification | 4 |
| Restatement > rephrasing an earlier sentence | Planning > local plan | 4 |
| Restatement > rephrasing an earlier sentence | Conclusion > intermediate conclusion | 4 |
| Reasoning > speculation | Reasoning > logical reasoning | 4 |
| Reasoning > calculation | Conclusion > intermediate conclusion | 3 |
| Reasoning > calculation | Reasoning > commonsense reasoning | 2 |
| Reflection > meta-evaluation of a step | Reasoning > comparison | 2 |
| Reasoning > option evaluation | Reasoning > logical reasoning | 2 |

### Residue: 181 sentences whose full-path set differs (first 30; the C-trace rows are held out of the prompt work)

| trace | s | reference | other | text |
|---|---|---|---|---|
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
| c004 | 40 | Reasoning > calculation > algebra | Reasoning > commonsense reasoning | Why? |
| c004 | 41 | Reasoning > calculation > algebra | Reasoning > commonsense reasoning | Because \$1.00 + \$0.10 = \$1.10. |
| c004 | 60 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎⏎    *   *(A) It is \$0.05*: |
| c004 | 64 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(B) It is probably \$0.05*: |
| c004 | 65 | Reasoning > hedge word analysis > mathematical reading | Reasoning > hedge word analysis > undecided | "Probably" implies probability. |
| c004 | 67 | Reasoning > hedge word analysis > everyday reading || Reflection > meta-evaluation of a step > option (B) | Reasoning > option evaluation > (B) | However, in the context of riddles, this option acknowledges the likely intent of the user (referring to the famous riddle) while acknowledging the missing constraint. |
| c004 | 68 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(C) There is not enough information, but the answer is most likely \$0.05*: |
| c004 | 69 | Reflection > meta-evaluation of a step > option (C) | Reasoning > option evaluation > (C) | This is logically the most accurate description. |
| c004 | 72 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(D) I am not sure*: |
| c004 | 74 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(E) The question is not well posed*: |
| c004 | 75 | Reasoning > option evaluation > (E) || Knowledge > concept or definition > well-posedness | Reasoning > option evaluation > (E) | Mathematically true (underdetermined), but "not well posed" usually implies no solution or non-unique solution in a way that makes it unsolvable. |
| c004 | 77 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(F) None of the above*: |
| c004 | 82 | Reasoning > speculation > intent of the question writer | Reflection > emotion or impression | ⏎    *   The prompt is a trick. |
| c004 | 92 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | If $b + B = 1.10$ and $B > b$ (where $B$ is bat, $b$ is ball), then $b$ can be any value in $(0, 0.55)$. |
| c004 | 93 | Reasoning > option evaluation > (A) | Conclusion > intermediate conclusion | ⏎    *   Therefore, "It is \$0.05" (A) is logically false based *only* on the provided text. |
| c004 | 94 | Reasoning > option evaluation > (C) | Restatement > rephrasing the prompt > option text | ⏎    *   However, the option (C) explicitly states "There is not enough information". |
| c004 | 97 | Reasoning > hedge word analysis > everyday reading | Reasoning > option evaluation > (C) | This acknowledges the cultural context/intent of the riddle. |
| c004 | 101 | Reasoning > option evaluation > (C) | Planning > local plan | ⏎        1. |
| c004 | 103 | Reasoning > option evaluation > (C) | Planning > local plan | ⏎        2. |
### Run 1: structural metrics judge vs reviewed

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e036 | 37 / 34 | 32 / 5 (2) / 2 | 0.941 / 0.865 / 0.901 | 31 / 32 | 33 / 36 (0.917) | 129 / 17 / 11 | 0.902 | 122 / 146 (0.836) | 9 / 25 | 35 / 16 / 7 / 196 | 0.603 |
| c004 | 46 / 48 | 45 / 1 (0) / 3 | 0.938 / 0.978 / 0.957 | 45 / 45 | 44 / 45 (0.978) | 176 / 17 / 45 | 0.850 | 165 / 193 (0.855) | 22 / 24 | 72 / 47 / 4 / 252 | 0.585 |
| pooled | 83 / 82 | 77 / 6 (2) / 5 | 0.939 / 0.928 / 0.933 | 76 / 77 | 77 / 81 (0.951) | 305 / 34 / 56 | 0.871 | 287 / 339 (0.847) | 31 / 49 | 107 / 63 / 11 / 448 | 0.591 |

Next-node confusions (reviewed → judge, pooled): Planning → Reasoning 1; Planning → Assumption 1; Planning → Restatement 1; Assumption → Planning 1
e036: missed reviewed openers at s19, s77, s96, s117, s193; extra judge openers at s86, s116
c004: missed reviewed openers at s216; extra judge openers at s111, s164, s295
## pytest output

```
........................................................................ [ 70%]
..............................                                           [100%]
102 passed in 0.33s
```
