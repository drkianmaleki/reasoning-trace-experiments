# TEST_REPORT — t4_judge — 2026-09-17 10:17

Test of pipeline step (4/9), the judge on the two source traces (`scripts/s1_judge.py`, `scripts/derivation.py`), per pipeline v1 Section 9 item 6. Git commit `4b3841ea31ee7c952ae7a6aa7ccb52fb5fea765e`; model `claude-sonnet-5` (sonnet); thinking mode low (request parameters {"thinking": {"type": "adaptive", "display": "summarized"}, "output_config": {"effort": "low"}}, max_tokens 24000); temperature None (not sent: the model rejects sampling parameters); prompt v2 sha256 `98ac17659798c184bc75fba6336007fb87e0b771e5272dfa05bdc90781b2a65c`; inventory sha256 `51c5d0d142863a1d6461bcc871b08401f80c02abce45c31445de2cae07798ba2`; sentences `runs/tests/t2_split_2026-09-16_2224/sentences_source.jsonl`. Repeats: 2. Run folders: `runs/experiments/judge_source_sonnet_v2_thinklow_r1_2026-09-17_1017`, `runs/experiments/judge_source_sonnet_v2_thinklow_r2_2026-09-17_1017`.

## Result: PASS (10/10 checks passed)

## Checks

- PASS — check 1, derivation gate on the reviewed labels (offline) — e036: 254 sentences; blocks 37 derived vs 37 listed; nodes 146 vs 146; interval differences 0, opener rule/label differences 0, name differences 0 (listing names with a '(1)' count stripped: 97); c004: 375 sentences; blocks 46 derived vs 46 listed; nodes 193 vs 193; interval differences 0, opener rule/label differences 0, name differences 0 (listing names with a '(1)' count stripped: 121)
- PASS — check 2, dry run (requests built, nothing called) — e036: 254 sentences, about 8774 input tokens (characters/4); every index exactly once in the user message: True; c004: 375 sentences, about 10799 input tokens (characters/4); every index exactly once in the user message: True; thinking parameters in the request: {"thinking": {"type": "adaptive", "display": "summarized"}, "output_config": {"effort": "low"}}; requests written to dry_run/requests/
- PASS — check 3, run 1, e036 judged — attempts 1, valid True, model echoed 'claude-sonnet-5', stop reasons ['end_turn'], final end_turn; tokens input 5635, cache read 0, cache write 8109, thinking 5647, output 7606 (thinking included); <think> tag in text blocks per attempt [False]; thinking text chars per attempt [4589]; cost $0.107603; judge nodes 137 / blocks 34 vs reviewed 146 / 37; agreement vs reviewed (this trace): Level 1 exact 0.819 kappa 0.780, Level 2 exact 0.732 kappa 0.715, Level 3 exact 0.732 kappa 0.719; residue rows 68
- PASS — check 4, run 1, c004 judged — attempts 1, valid True, model echoed 'claude-sonnet-5', stop reasons ['end_turn'], final end_turn; tokens input 9403, cache read 8109, cache write 0, thinking 6804, output 9374 (thinking included); <think> tag in text blocks per attempt [False]; thinking text chars per attempt [4027]; cost $0.114168; judge nodes 206 / blocks 43 vs reviewed 193 / 46; agreement vs reviewed (this trace): Level 1 exact 0.749 kappa 0.676, Level 2 exact 0.613 kappa 0.595, Level 3 exact 0.597 kappa 0.585; residue rows 151
- PASS — check 5, run 1, agreement vs reviewed over both traces — 629 sentences; Level 1: exact 0.777, Jaccard 0.788, kappa 0.726; Level 2: exact 0.661, Jaccard 0.670, kappa 0.645; Level 3: exact 0.652, Jaccard 0.660, kappa 0.641; residue rows 219; cost of this run $0.221770
- PASS — check 6, run 2, e036 judged — attempts 1, valid True, model echoed 'claude-sonnet-5', stop reasons ['end_turn'], final end_turn; tokens input 5635, cache read 8109, cache write 0, thinking 8195, output 9855 (thinking included); <think> tag in text blocks per attempt [False]; thinking text chars per attempt [5534]; cost $0.111442; judge nodes 142 / blocks 33 vs reviewed 146 / 37; agreement vs reviewed (this trace): Level 1 exact 0.819 kappa 0.780, Level 2 exact 0.736 kappa 0.719, Level 3 exact 0.720 kappa 0.706; residue rows 71
- PASS — check 7, run 2, c004 judged — attempts 1, valid True, model echoed 'claude-sonnet-5', stop reasons ['end_turn'], final end_turn; tokens input 9403, cache read 8109, cache write 0, thinking 8469, output 11158 (thinking included); <think> tag in text blocks per attempt [False]; thinking text chars per attempt [3853]; cost $0.132008; judge nodes 210 / blocks 43 vs reviewed 193 / 46; agreement vs reviewed (this trace): Level 1 exact 0.773 kappa 0.704, Level 2 exact 0.608 kappa 0.590, Level 3 exact 0.600 kappa 0.589; residue rows 150
- PASS — check 8, run 2, agreement vs reviewed over both traces — 629 sentences; Level 1: exact 0.792, Jaccard 0.800, kappa 0.744; Level 2: exact 0.660, Jaccard 0.666, kappa 0.644; Level 3: exact 0.649, Jaccard 0.655, kappa 0.637; residue rows 221; cost of this run $0.243450
- PASS — check 9, test-retest run 2 vs run 1 — e036: L1 exact 0.913 kappa 0.890, L2 exact 0.850 kappa 0.838, full exact 0.831 kappa 0.819; differing sentences 43; c004: L1 exact 0.923 kappa 0.902, L2 exact 0.867 kappa 0.858, full exact 0.840 kappa 0.833; differing sentences 60; pooled: L1 exact 0.919 kappa 0.900, L2 exact 0.860 kappa 0.851, full exact 0.836 kappa 0.829; differing sentences 103
- PASS — check 10, pytest on scripts/tests — exit code 0; last line: 91 passed in 0.29s

## Run 1: agreement judge vs reviewed (both traces)

| level | n | exact-match rate | mean Jaccard | kappa (primary label) | primary agreement |
|---|---|---|---|---|---|
| Level 1 | 629 | 0.7774 | 0.7878 | 0.7261 | 0.7870 |
| Level 1 > Level 2 | 629 | 0.6614 | 0.6701 | 0.6454 | 0.6677 |
| full path | 629 | 0.6518 | 0.6598 | 0.6405 | 0.6582 |

| level | label | n_reviewed | n_judge | tp | precision | recall | F1 |
|---|---|---|---|---|---|---|---|
| 1 | Assumption | 7 | 3 | 3 | 1.000 | 0.429 | 0.600 |
| 1 | Conclusion | 40 | 66 | 36 | 0.545 | 0.900 | 0.679 |
| 1 | Example | 22 | 34 | 22 | 0.647 | 1.000 | 0.786 |
| 1 | Knowledge | 30 | 27 | 19 | 0.704 | 0.633 | 0.667 |
| 1 | Planning | 177 | 178 | 158 | 0.888 | 0.893 | 0.890 |
| 1 | Reasoning | 206 | 205 | 167 | 0.815 | 0.811 | 0.813 |
| 1 | Reflection | 36 | 31 | 24 | 0.774 | 0.667 | 0.716 |
| 1 | Restatement | 123 | 88 | 74 | 0.841 | 0.602 | 0.701 |
| 2 | Assumption > assuming a missing premise by common practice | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Assumption > assuming an uncertain fact | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Assumption > branching (case split) | 5 | 3 | 3 | 1.000 | 0.600 | 0.750 |
| 2 | Conclusion > final answer | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 2 | Conclusion > intermediate conclusion | 37 | 63 | 33 | 0.524 | 0.892 | 0.660 |
| 2 | Example > non-exhaustive listing | 17 | 34 | 17 | 0.500 | 1.000 | 0.667 |
| 2 | Example > rhetorical example | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Knowledge > commonsense | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Knowledge > concept or definition | 6 | 5 | 4 | 0.800 | 0.667 | 0.727 |
| 2 | Knowledge > self-knowledge | 5 | 2 | 2 | 1.000 | 0.400 | 0.571 |
| 2 | Knowledge > world knowledge | 16 | 20 | 13 | 0.650 | 0.812 | 0.722 |
| 2 | Planning > announce output | 16 | 17 | 16 | 0.941 | 1.000 | 0.970 |
| 2 | Planning > announce the conclusion | 5 | 4 | 4 | 1.000 | 0.800 | 0.889 |
| 2 | Planning > global plan | 35 | 38 | 32 | 0.842 | 0.914 | 0.877 |
| 2 | Planning > initiate backtracking | 8 | 3 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Planning > initiate verification | 42 | 40 | 27 | 0.675 | 0.643 | 0.659 |
| 2 | Planning > local plan | 71 | 75 | 60 | 0.800 | 0.845 | 0.822 |
| 2 | Planning > unspecified | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Reasoning > calculation | 35 | 21 | 17 | 0.810 | 0.486 | 0.607 |
| 2 | Reasoning > commonsense reasoning | 12 | 13 | 12 | 0.923 | 1.000 | 0.960 |
| 2 | Reasoning > comparison | 17 | 12 | 9 | 0.750 | 0.529 | 0.621 |
| 2 | Reasoning > defining symbols | 15 | 11 | 6 | 0.545 | 0.400 | 0.462 |
| 2 | Reasoning > hedge word analysis | 13 | 3 | 3 | 1.000 | 0.231 | 0.375 |
| 2 | Reasoning > logical reasoning | 38 | 55 | 23 | 0.418 | 0.605 | 0.495 |
| 2 | Reasoning > option evaluation | 45 | 72 | 34 | 0.472 | 0.756 | 0.581 |
| 2 | Reasoning > speculation | 32 | 18 | 13 | 0.722 | 0.406 | 0.520 |
| 2 | Reflection > emotion or impression | 1 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Reflection > meta-evaluation of a step | 35 | 30 | 24 | 0.800 | 0.686 | 0.738 |
| 2 | Restatement > rephrasing an earlier sentence | 70 | 33 | 25 | 0.758 | 0.357 | 0.485 |
| 2 | Restatement > rephrasing the prompt | 53 | 55 | 48 | 0.873 | 0.906 | 0.889 |
| 3 | Assumption > assuming a missing premise by common practice > "$1.00 more" | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > assuming an uncertain fact | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > branching (case split) | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > branching (case split) > algebra | 4 | 3 | 3 | 1.000 | 0.750 | 0.857 |
| 3 | Conclusion > final answer | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 3 | Conclusion > intermediate conclusion | 37 | 63 | 33 | 0.524 | 0.892 | 0.660 |
| 3 | Example > non-exhaustive listing > algebra | 17 | 34 | 17 | 0.500 | 1.000 | 0.667 |
| 3 | Example > rhetorical example | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > commonsense | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > concept or definition > well-posedness | 6 | 5 | 4 | 0.800 | 0.667 | 0.727 |
| 3 | Knowledge > self-knowledge > evaluation context | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| 3 | Knowledge > self-knowledge > role | 4 | 1 | 1 | 1.000 | 0.250 | 0.400 |
| 3 | Knowledge > world knowledge > famous problem (CRT) | 16 | 20 | 13 | 0.650 | 0.812 | 0.722 |
| 3 | Planning > announce output | 16 | 17 | 16 | 0.941 | 1.000 | 0.970 |
| 3 | Planning > announce the conclusion | 5 | 4 | 4 | 1.000 | 0.800 | 0.889 |
| 3 | Planning > global plan | 35 | 38 | 32 | 0.842 | 0.914 | 0.877 |
| 3 | Planning > initiate backtracking | 8 | 3 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Planning > initiate verification | 42 | 40 | 27 | 0.675 | 0.643 | 0.659 |
| 3 | Planning > local plan | 71 | 75 | 60 | 0.800 | 0.845 | 0.822 |
| 3 | Planning > unspecified | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > calculation | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > calculation > algebra | 35 | 20 | 16 | 0.800 | 0.457 | 0.582 |
| 3 | Reasoning > commonsense reasoning | 12 | 13 | 12 | 0.923 | 1.000 | 0.960 |
| 3 | Reasoning > comparison > option vs option | 8 | 6 | 4 | 0.667 | 0.500 | 0.571 |
| 3 | Reasoning > comparison > prompt vs original text | 9 | 6 | 5 | 0.833 | 0.556 | 0.667 |
| 3 | Reasoning > defining symbols > algebra | 15 | 11 | 6 | 0.545 | 0.400 | 0.462 |
| 3 | Reasoning > hedge word analysis > everyday reading | 4 | 1 | 1 | 1.000 | 0.250 | 0.400 |
| 3 | Reasoning > hedge word analysis > mathematical reading | 8 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > hedge word analysis > undecided | 1 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > logical reasoning | 20 | 27 | 13 | 0.481 | 0.650 | 0.553 |
| 3 | Reasoning > logical reasoning > algebra | 18 | 28 | 7 | 0.250 | 0.389 | 0.304 |
| 3 | Reasoning > option evaluation > (A) | 11 | 11 | 6 | 0.545 | 0.545 | 0.545 |
| 3 | Reasoning > option evaluation > (B) | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > option evaluation > (C) | 25 | 41 | 20 | 0.488 | 0.800 | 0.606 |
| 3 | Reasoning > option evaluation > (E) | 9 | 15 | 8 | 0.533 | 0.889 | 0.667 |
| 3 | Reasoning > option evaluation > (F) | 0 | 4 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > speculation | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > speculation > intent of the question writer | 32 | 17 | 13 | 0.765 | 0.406 | 0.531 |
| 3 | Reflection > emotion or impression | 1 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step | 14 | 13 | 12 | 0.923 | 0.857 | 0.889 |
| 3 | Reflection > meta-evaluation of a step > option (A) | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step > option (B) | 3 | 1 | 1 | 1.000 | 0.333 | 0.500 |
| 3 | Reflection > meta-evaluation of a step > option (C) | 7 | 6 | 4 | 0.667 | 0.571 | 0.615 |
| 3 | Reflection > meta-evaluation of a step > option (D) | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 3 | Reflection > meta-evaluation of a step > option (E) | 5 | 3 | 2 | 0.667 | 0.400 | 0.500 |
| 3 | Reflection > meta-evaluation of a step > option (F) | 3 | 3 | 2 | 0.667 | 0.667 | 0.667 |
| 3 | Restatement > rephrasing an earlier sentence | 70 | 33 | 25 | 0.758 | 0.357 | 0.485 |
| 3 | Restatement > rephrasing the prompt > answer-format instruction | 7 | 6 | 6 | 1.000 | 0.857 | 0.923 |
| 3 | Restatement > rephrasing the prompt > option text | 24 | 28 | 22 | 0.786 | 0.917 | 0.846 |
| 3 | Restatement > rephrasing the prompt > question text | 22 | 21 | 19 | 0.905 | 0.864 | 0.884 |

### Twenty most frequent confusion pairs at Level 1 (reference → other, primary label)

| reference | other | count |
|---|---|---|
| Reasoning | Conclusion | 17 |
| Restatement | Reasoning | 15 |
| Planning | Restatement | 12 |
| Reasoning | Planning | 11 |
| Restatement | Example | 11 |
| Restatement | Conclusion | 10 |
| Knowledge | Reasoning | 9 |
| Reflection | Reasoning | 8 |
| Restatement | Knowledge | 7 |
| Restatement | Planning | 6 |
| Reasoning | Reflection | 6 |
| Reasoning | Restatement | 5 |
| Conclusion | Reasoning | 4 |
| Assumption | Planning | 2 |
| Planning | Reasoning | 2 |
| Reflection | Conclusion | 2 |
| Assumption | Reasoning | 1 |
| Knowledge | Planning | 1 |
| Planning | Example | 1 |
| Planning | Knowledge | 1 |

### Twenty most frequent confusion pairs at Level 2 (reference → other, primary label)

| reference | other | count |
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
| Restatement > rephrasing an earlier sentence | Planning > local plan | 6 |
| Restatement > rephrasing an earlier sentence | Knowledge > world knowledge | 6 |
| Reasoning > option evaluation | Conclusion > intermediate conclusion | 5 |
| Restatement > rephrasing an earlier sentence | Reasoning > logical reasoning | 5 |
| Example > rhetorical example | Example > non-exhaustive listing | 5 |
| Planning > initiate verification | Restatement > rephrasing the prompt | 4 |
| Reasoning > option evaluation | Planning > local plan | 4 |
| Reasoning > defining symbols | Reasoning > calculation | 4 |
| Restatement > rephrasing an earlier sentence | Reasoning > option evaluation | 4 |
| Reasoning > defining symbols | Restatement > rephrasing an earlier sentence | 4 |

### Residue: 219 sentences whose full-path set differs (first 30; the C-trace rows are held out of the prompt work)

| trace | s | reference | other | text |
|---|---|---|---|---|
| c004 | 12 | Restatement > rephrasing the prompt > question text | Reasoning > defining symbols > algebra | ⏎    *   *Goal:* Find cost of Ball. |
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
| c004 | 40 | Reasoning > calculation > algebra | Reasoning > logical reasoning | Why? |
| c004 | 41 | Reasoning > calculation > algebra | Reasoning > logical reasoning | Because \$1.00 + \$0.10 = \$1.10. |
| c004 | 43 | Planning > initiate verification || Restatement > rephrasing the prompt > question text | Restatement > rephrasing the prompt > question text | ⏎    *   *Check the text provided in the prompt again carefully:* "A bat and a ball cost \$1.10 in total. |
| c004 | 47 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | Any price for the ball ($x$) where $0 < x < 0.55$ works. |
| c004 | 60 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎⏎    *   *(A) It is \$0.05*: |
| c004 | 64 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(B) It is probably \$0.05*: |
| c004 | 65 | Reasoning > hedge word analysis > mathematical reading | Reasoning > hedge word analysis > undecided | "Probably" implies probability. |
| c004 | 66 | Reasoning > hedge word analysis > mathematical reading | Reasoning > hedge word analysis > undecided | Unless there's a distribution of prices given, we can't assign probability. |
| c004 | 67 | Reasoning > hedge word analysis > everyday reading || Reflection > meta-evaluation of a step > option (B) | Reasoning > hedge word analysis > everyday reading | However, in the context of riddles, this option acknowledges the likely intent of the user (referring to the famous riddle) while acknowledging the missing constraint. |
| c004 | 68 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(C) There is not enough information, but the answer is most likely \$0.05*: |
| c004 | 69 | Reflection > meta-evaluation of a step > option (C) | Reasoning > option evaluation > (C) | This is logically the most accurate description. |
| c004 | 72 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(D) I am not sure*: |
| c004 | 74 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(E) The question is not well posed*: |
| c004 | 75 | Reasoning > option evaluation > (E) || Knowledge > concept or definition > well-posedness | Reasoning > option evaluation > (E) | Mathematically true (underdetermined), but "not well posed" usually implies no solution or non-unique solution in a way that makes it unsolvable. |
| c004 | 77 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(F) None of the above*: |
| c004 | 82 | Reasoning > speculation > intent of the question writer | Reasoning > logical reasoning | ⏎    *   The prompt is a trick. |
| c004 | 93 | Reasoning > option evaluation > (A) | Conclusion > intermediate conclusion | ⏎    *   Therefore, "It is \$0.05" (A) is logically false based *only* on the provided text. |
| c004 | 96 | Restatement > rephrasing the prompt > option text | Reasoning > option evaluation > (C) | It then adds "...but the answer is most likely \$0.05". |
## Run 2: agreement judge vs reviewed (both traces)

| level | n | exact-match rate | mean Jaccard | kappa (primary label) | primary agreement |
|---|---|---|---|---|---|
| Level 1 | 629 | 0.7917 | 0.8005 | 0.7435 | 0.8013 |
| Level 1 > Level 2 | 629 | 0.6598 | 0.6661 | 0.6438 | 0.6661 |
| full path | 629 | 0.6486 | 0.6550 | 0.6375 | 0.6550 |

| level | label | n_reviewed | n_judge | tp | precision | recall | F1 |
|---|---|---|---|---|---|---|---|
| 1 | Assumption | 7 | 4 | 3 | 0.750 | 0.429 | 0.545 |
| 1 | Conclusion | 40 | 61 | 35 | 0.574 | 0.875 | 0.693 |
| 1 | Example | 22 | 29 | 21 | 0.724 | 0.955 | 0.824 |
| 1 | Knowledge | 30 | 29 | 22 | 0.759 | 0.733 | 0.746 |
| 1 | Planning | 177 | 179 | 160 | 0.894 | 0.904 | 0.899 |
| 1 | Reasoning | 206 | 208 | 170 | 0.817 | 0.825 | 0.821 |
| 1 | Reflection | 36 | 30 | 23 | 0.767 | 0.639 | 0.697 |
| 1 | Restatement | 123 | 90 | 76 | 0.844 | 0.618 | 0.714 |
| 2 | Assumption > assuming a missing premise by common practice | 1 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Assumption > assuming an uncertain fact | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Assumption > branching (case split) | 5 | 3 | 3 | 1.000 | 0.600 | 0.750 |
| 2 | Conclusion > final answer | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 2 | Conclusion > intermediate conclusion | 37 | 58 | 32 | 0.552 | 0.865 | 0.674 |
| 2 | Example > non-exhaustive listing | 17 | 29 | 17 | 0.586 | 1.000 | 0.739 |
| 2 | Example > rhetorical example | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Knowledge > commonsense | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Knowledge > concept or definition | 6 | 5 | 5 | 1.000 | 0.833 | 0.909 |
| 2 | Knowledge > self-knowledge | 5 | 4 | 4 | 1.000 | 0.800 | 0.889 |
| 2 | Knowledge > world knowledge | 16 | 20 | 13 | 0.650 | 0.812 | 0.722 |
| 2 | Planning > announce output | 16 | 19 | 16 | 0.842 | 1.000 | 0.914 |
| 2 | Planning > announce the conclusion | 5 | 2 | 2 | 1.000 | 0.400 | 0.571 |
| 2 | Planning > global plan | 35 | 38 | 31 | 0.816 | 0.886 | 0.849 |
| 2 | Planning > initiate backtracking | 8 | 4 | 1 | 0.250 | 0.125 | 0.167 |
| 2 | Planning > initiate verification | 42 | 38 | 27 | 0.711 | 0.643 | 0.675 |
| 2 | Planning > local plan | 71 | 78 | 61 | 0.782 | 0.859 | 0.819 |
| 2 | Reasoning > calculation | 35 | 14 | 9 | 0.643 | 0.257 | 0.367 |
| 2 | Reasoning > commonsense reasoning | 12 | 14 | 10 | 0.714 | 0.833 | 0.769 |
| 2 | Reasoning > comparison | 17 | 16 | 11 | 0.688 | 0.647 | 0.667 |
| 2 | Reasoning > defining symbols | 15 | 17 | 10 | 0.588 | 0.667 | 0.625 |
| 2 | Reasoning > hedge word analysis | 13 | 2 | 2 | 1.000 | 0.154 | 0.267 |
| 2 | Reasoning > logical reasoning | 38 | 66 | 27 | 0.409 | 0.711 | 0.519 |
| 2 | Reasoning > option evaluation | 45 | 67 | 33 | 0.493 | 0.733 | 0.589 |
| 2 | Reasoning > speculation | 32 | 12 | 9 | 0.750 | 0.281 | 0.409 |
| 2 | Reflection > emotion or impression | 1 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Reflection > meta-evaluation of a step | 35 | 28 | 23 | 0.821 | 0.657 | 0.730 |
| 2 | Reflection > unspecified | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Restatement > rephrasing an earlier sentence | 70 | 33 | 25 | 0.758 | 0.357 | 0.485 |
| 2 | Restatement > rephrasing the prompt | 53 | 57 | 50 | 0.877 | 0.943 | 0.909 |
| 3 | Assumption > assuming a missing premise by common practice > "$1.00 more" | 1 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > assuming an uncertain fact | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > branching (case split) | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > branching (case split) > algebra | 4 | 3 | 3 | 1.000 | 0.750 | 0.857 |
| 3 | Conclusion > final answer | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 3 | Conclusion > intermediate conclusion | 37 | 58 | 32 | 0.552 | 0.865 | 0.674 |
| 3 | Example > non-exhaustive listing | 0 | 4 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Example > non-exhaustive listing > algebra | 17 | 25 | 17 | 0.680 | 1.000 | 0.810 |
| 3 | Example > rhetorical example | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > commonsense | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > concept or definition > well-posedness | 6 | 5 | 5 | 1.000 | 0.833 | 0.909 |
| 3 | Knowledge > self-knowledge > evaluation context | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| 3 | Knowledge > self-knowledge > role | 4 | 3 | 3 | 1.000 | 0.750 | 0.857 |
| 3 | Knowledge > world knowledge | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > world knowledge > famous problem (CRT) | 16 | 19 | 12 | 0.632 | 0.750 | 0.686 |
| 3 | Planning > announce output | 16 | 19 | 16 | 0.842 | 1.000 | 0.914 |
| 3 | Planning > announce the conclusion | 5 | 2 | 2 | 1.000 | 0.400 | 0.571 |
| 3 | Planning > global plan | 35 | 38 | 31 | 0.816 | 0.886 | 0.849 |
| 3 | Planning > initiate backtracking | 8 | 4 | 1 | 0.250 | 0.125 | 0.167 |
| 3 | Planning > initiate verification | 42 | 38 | 27 | 0.711 | 0.643 | 0.675 |
| 3 | Planning > local plan | 71 | 78 | 61 | 0.782 | 0.859 | 0.819 |
| 3 | Reasoning > calculation > algebra | 35 | 14 | 9 | 0.643 | 0.257 | 0.367 |
| 3 | Reasoning > commonsense reasoning | 12 | 14 | 10 | 0.714 | 0.833 | 0.769 |
| 3 | Reasoning > comparison > option vs option | 8 | 8 | 4 | 0.500 | 0.500 | 0.500 |
| 3 | Reasoning > comparison > prompt vs original text | 9 | 8 | 7 | 0.875 | 0.778 | 0.824 |
| 3 | Reasoning > defining symbols > algebra | 15 | 17 | 10 | 0.588 | 0.667 | 0.625 |
| 3 | Reasoning > hedge word analysis | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > hedge word analysis > everyday reading | 4 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > hedge word analysis > mathematical reading | 8 | 1 | 1 | 1.000 | 0.125 | 0.222 |
| 3 | Reasoning > hedge word analysis > undecided | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > logical reasoning | 20 | 36 | 18 | 0.500 | 0.900 | 0.643 |
| 3 | Reasoning > logical reasoning > algebra | 18 | 30 | 7 | 0.233 | 0.389 | 0.292 |
| 3 | Reasoning > option evaluation > (A) | 11 | 10 | 5 | 0.500 | 0.455 | 0.476 |
| 3 | Reasoning > option evaluation > (B) | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > option evaluation > (C) | 25 | 42 | 20 | 0.476 | 0.800 | 0.597 |
| 3 | Reasoning > option evaluation > (E) | 9 | 11 | 8 | 0.727 | 0.889 | 0.800 |
| 3 | Reasoning > option evaluation > (F) | 0 | 3 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > speculation | 0 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > speculation > intent of the question writer | 32 | 10 | 9 | 0.900 | 0.281 | 0.429 |
| 3 | Reflection > emotion or impression | 1 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step | 14 | 12 | 12 | 1.000 | 0.857 | 0.923 |
| 3 | Reflection > meta-evaluation of a step > option (A) | 0 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step > option (B) | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| 3 | Reflection > meta-evaluation of a step > option (C) | 7 | 3 | 2 | 0.667 | 0.286 | 0.400 |
| 3 | Reflection > meta-evaluation of a step > option (D) | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 3 | Reflection > meta-evaluation of a step > option (E) | 5 | 3 | 2 | 0.667 | 0.400 | 0.500 |
| 3 | Reflection > meta-evaluation of a step > option (F) | 3 | 3 | 2 | 0.667 | 0.667 | 0.667 |
| 3 | Reflection > unspecified | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Restatement > rephrasing an earlier sentence | 70 | 33 | 25 | 0.758 | 0.357 | 0.485 |
| 3 | Restatement > rephrasing the prompt > answer-format instruction | 7 | 9 | 7 | 0.778 | 1.000 | 0.875 |
| 3 | Restatement > rephrasing the prompt > option text | 24 | 29 | 22 | 0.759 | 0.917 | 0.830 |
| 3 | Restatement > rephrasing the prompt > question text | 22 | 19 | 18 | 0.947 | 0.818 | 0.878 |

### Twenty most frequent confusion pairs at Level 1 (reference → other, primary label)

| reference | other | count |
|---|---|---|
| Restatement | Reasoning | 19 |
| Reasoning | Conclusion | 14 |
| Planning | Restatement | 11 |
| Reasoning | Planning | 10 |
| Reflection | Reasoning | 9 |
| Restatement | Conclusion | 9 |
| Restatement | Example | 8 |
| Restatement | Knowledge | 6 |
| Knowledge | Reasoning | 6 |
| Restatement | Planning | 5 |
| Reasoning | Reflection | 5 |
| Reasoning | Restatement | 4 |
| Conclusion | Reasoning | 2 |
| Assumption | Planning | 2 |
| Planning | Reasoning | 2 |
| Reflection | Conclusion | 2 |
| Assumption | Reasoning | 1 |
| Knowledge | Planning | 1 |
| Reasoning | Assumption | 1 |
| Example | Reasoning | 1 |

### Twenty most frequent confusion pairs at Level 2 (reference → other, primary label)

| reference | other | count |
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
| Reflection > meta-evaluation of a step | Reasoning > option evaluation | 6 |
| Restatement > rephrasing an earlier sentence | Knowledge > world knowledge | 6 |
| Reasoning > option evaluation | Conclusion > intermediate conclusion | 4 |
| Reasoning > option evaluation | Planning > local plan | 4 |
| Restatement > rephrasing an earlier sentence | Planning > local plan | 4 |
| Restatement > rephrasing an earlier sentence | Reasoning > option evaluation | 4 |
| Example > rhetorical example | Example > non-exhaustive listing | 4 |
| Planning > initiate verification | Restatement > rephrasing the prompt | 3 |
| Reasoning > speculation | Reasoning > comparison | 3 |
| Restatement > rephrasing an earlier sentence | Reasoning > defining symbols | 3 |

### Residue: 221 sentences whose full-path set differs (first 30; the C-trace rows are held out of the prompt work)

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
| c004 | 40 | Reasoning > calculation > algebra | Reasoning > logical reasoning | Why? |
| c004 | 41 | Reasoning > calculation > algebra | Reasoning > logical reasoning | Because \$1.00 + \$0.10 = \$1.10. |
| c004 | 47 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | Any price for the ball ($x$) where $0 < x < 0.55$ works. |
| c004 | 60 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎⏎    *   *(A) It is \$0.05*: |
| c004 | 64 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(B) It is probably \$0.05*: |
| c004 | 65 | Reasoning > hedge word analysis > mathematical reading | Reasoning > hedge word analysis | "Probably" implies probability. |
| c004 | 67 | Reasoning > hedge word analysis > everyday reading || Reflection > meta-evaluation of a step > option (B) | Reasoning > option evaluation > (B) | However, in the context of riddles, this option acknowledges the likely intent of the user (referring to the famous riddle) while acknowledging the missing constraint. |
| c004 | 68 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(C) There is not enough information, but the answer is most likely \$0.05*: |
| c004 | 69 | Reflection > meta-evaluation of a step > option (C) | Reasoning > option evaluation > (C) | This is logically the most accurate description. |
| c004 | 72 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(D) I am not sure*: |
| c004 | 74 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(E) The question is not well posed*: |
| c004 | 75 | Reasoning > option evaluation > (E) || Knowledge > concept or definition > well-posedness | Reasoning > option evaluation > (E) | Mathematically true (underdetermined), but "not well posed" usually implies no solution or non-unique solution in a way that makes it unsolvable. |
| c004 | 77 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(F) None of the above*: |
| c004 | 82 | Reasoning > speculation > intent of the question writer | Reasoning > logical reasoning | ⏎    *   The prompt is a trick. |
| c004 | 92 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | If $b + B = 1.10$ and $B > b$ (where $B$ is bat, $b$ is ball), then $b$ can be any value in $(0, 0.55)$. |
| c004 | 93 | Reasoning > option evaluation > (A) | Conclusion > intermediate conclusion | ⏎    *   Therefore, "It is \$0.05" (A) is logically false based *only* on the provided text. |
| c004 | 97 | Reasoning > hedge word analysis > everyday reading | Reasoning > option evaluation > (C) | This acknowledges the cultural context/intent of the riddle. |
| c004 | 101 | Reasoning > option evaluation > (C) | Planning > local plan | ⏎        1. |
## Test-retest: run 2 against run 1 (run 1 as reference; same functions as reviewed-vs-judge)

| scope | L1 exact | L1 kappa | L2 exact | L2 kappa | full exact | full kappa | run 1 blocks / nodes | run 2 blocks / nodes | reviewed |
|---|---|---|---|---|---|---|---|---|---|
| e036 | 0.913 | 0.890 | 0.850 | 0.838 | 0.831 | 0.819 | 34 / 137 | 33 / 142 | 37 / 146 |
| c004 | 0.923 | 0.902 | 0.867 | 0.858 | 0.840 | 0.833 | 43 / 206 | 43 / 210 | 46 / 193 |
| pooled | 0.919 | 0.900 | 0.860 | 0.851 | 0.836 | 0.829 | 77 / 343 | 76 / 352 | 83 / 339 |

### Ten most frequent Level 2 disagreements between the runs (run 1 → run 2)

| run 1 | run 2 | count |
|---|---|---|
| Reasoning > calculation | Reasoning > logical reasoning | 6 |
| Conclusion > intermediate conclusion | Restatement > rephrasing an earlier sentence | 4 |
| Example > non-exhaustive listing | Reasoning > logical reasoning | 4 |
| Restatement > rephrasing an earlier sentence | Reasoning > defining symbols | 4 |
| Reasoning > logical reasoning | Reasoning > comparison | 3 |
| Reasoning > speculation | Reasoning > commonsense reasoning | 3 |
| Reasoning > option evaluation | Reasoning > logical reasoning | 3 |
| Reflection > meta-evaluation of a step | Reasoning > option evaluation | 3 |
| Conclusion > intermediate conclusion | Reasoning > logical reasoning | 3 |
| Reasoning > calculation | Reasoning > defining symbols | 3 |
## pytest output

```
........................................................................ [ 79%]
...................                                                      [100%]
91 passed in 0.29s
```
