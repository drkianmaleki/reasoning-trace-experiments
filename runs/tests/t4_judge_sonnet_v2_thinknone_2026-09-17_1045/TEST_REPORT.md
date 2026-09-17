# TEST_REPORT — t4_judge — 2026-09-17 10:45

Test of pipeline step (4/9), the judge on the two source traces (`scripts/s1_judge.py`, `scripts/derivation.py`), per pipeline v1 Section 9 item 6. Git commit `5eed56dcbf8323af99574d5a82ff350e0a808250`; model `claude-sonnet-5` (sonnet); thinking mode none (thinking {'type': 'disabled'}, max_tokens 8000); temperature None (not sent: the model rejects sampling parameters); prompt v2 sha256 `98ac17659798c184bc75fba6336007fb87e0b771e5272dfa05bdc90781b2a65c`; inventory sha256 `51c5d0d142863a1d6461bcc871b08401f80c02abce45c31445de2cae07798ba2`; sentences `runs/tests/t2_split_2026-09-16_2224/sentences_source.jsonl`. Repeats: 1. Run folders: `runs/experiments/judge_source_sonnet_v2_thinknone_2026-09-17_1045`.

## Result: PASS (7/7 checks passed)

## Checks

- PASS — check 1, derivation gate on the reviewed labels (offline) — e036: 254 sentences; blocks 37 derived vs 37 listed; nodes 146 vs 146; interval differences 0, opener rule/label differences 0, name differences 0 (listing names with a '(1)' count stripped: 97); c004: 375 sentences; blocks 46 derived vs 46 listed; nodes 193 vs 193; interval differences 0, opener rule/label differences 0, name differences 0 (listing names with a '(1)' count stripped: 121)
- PASS — check 2, dry run (requests built, nothing called) — e036: 254 sentences, about 8805 input tokens (characters/4); every index exactly once in the user message: True; c004: 375 sentences, about 10830 input tokens (characters/4); every index exactly once in the user message: True; thinking parameters in the request: none; requests written to dry_run/requests/
- PASS — check 3, run 1, e036 judged — attempts 2, valid True, model echoed 'claude-sonnet-5', stop reasons ['end_turn', 'end_turn'], final end_turn; tokens input 13329, cache read 8109, cache write 8109, thinking 0, output 3775 (thinking included); <think> tag in text blocks per attempt [False, False]; thinking text chars per attempt [0, 0]; cost $0.086302; judge nodes 130 / blocks 33 vs reviewed 146 / 37; retry message: Your labeling was rejected: unparsable: expected '<first>-<last> <code>' or '<index> <code>' at line 1: s0 Pl.gp. Output the complete labeling again, every index from 0 to 253 exactly once, one run per line, codes only.; error: unparsable: expected '<first>-<last> <code>' or '<index> <code>' at line 1: s0 Pl.gp; agreement vs reviewed (this trace): Level 1 exact 0.827 kappa 0.792, Level 2 exact 0.740 kappa 0.724, Level 3 exact 0.720 kappa 0.707; residue rows 71
- PASS — check 4, run 1, c004 judged — attempts 1, valid True, model echoed 'claude-sonnet-5', stop reasons ['end_turn'], final end_turn; tokens input 9444, cache read 8109, cache write 0, thinking 0, output 3466 (thinking included); <think> tag in text blocks per attempt [False]; thinking text chars per attempt [0]; cost $0.055170; judge nodes 232 / blocks 48 vs reviewed 193 / 46; agreement vs reviewed (this trace): Level 1 exact 0.709 kappa 0.623, Level 2 exact 0.579 kappa 0.561, Level 3 exact 0.563 kappa 0.552; residue rows 164
- PASS — check 5, run 1, agreement vs reviewed over both traces — 629 sentences; Level 1: exact 0.757, Jaccard 0.766, kappa 0.701; Level 2: exact 0.644, Jaccard 0.651, kappa 0.628; Level 3: exact 0.626, Jaccard 0.633, kappa 0.616; residue rows 235; cost of this run $0.141472
- PASS — check 6, run 1, structural metrics vs reviewed (pooled) — block openers hits 69 / misses 14 (near 5) / extras 12, F1 0.841, rule agrees on 67 of 69 hits; next node after the reviewed cuts 69 / 81 (0.852); node ends F1 0.810, matched nodes Level 1 agree 0.749, reviewed nodes split 41 / merged 80; sentences L1 wrong 153 / L2 wrong 71 / L3 wrong 11 / all right 394 (L1 share of disagreements 0.651); structural_source.csv written
- PASS — check 7, pytest on scripts/tests — exit code 0; last line: 102 passed in 0.31s

## Run 1: agreement judge vs reviewed (both traces)

| level | n | exact-match rate | mean Jaccard | kappa (primary label) | primary agreement |
|---|---|---|---|---|---|
| Level 1 | 629 | 0.7568 | 0.7660 | 0.7009 | 0.7679 |
| Level 1 > Level 2 | 629 | 0.6439 | 0.6508 | 0.6284 | 0.6518 |
| full path | 629 | 0.6264 | 0.6333 | 0.6159 | 0.6343 |

| level | label | n_reviewed | n_judge | tp | precision | recall | F1 |
|---|---|---|---|---|---|---|---|
| 1 | Assumption | 7 | 4 | 3 | 0.750 | 0.429 | 0.545 |
| 1 | Conclusion | 40 | 56 | 32 | 0.571 | 0.800 | 0.667 |
| 1 | Example | 22 | 31 | 20 | 0.645 | 0.909 | 0.755 |
| 1 | Knowledge | 30 | 28 | 19 | 0.679 | 0.633 | 0.655 |
| 1 | Planning | 177 | 173 | 147 | 0.850 | 0.831 | 0.840 |
| 1 | Reasoning | 206 | 208 | 161 | 0.774 | 0.782 | 0.778 |
| 1 | Reflection | 36 | 36 | 24 | 0.667 | 0.667 | 0.667 |
| 1 | Restatement | 123 | 94 | 82 | 0.872 | 0.667 | 0.756 |
| 2 | Assumption > assuming a missing premise by common practice | 1 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Assumption > assuming an uncertain fact | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Assumption > branching (case split) | 5 | 3 | 3 | 1.000 | 0.600 | 0.750 |
| 2 | Conclusion > final answer | 3 | 6 | 3 | 0.500 | 1.000 | 0.667 |
| 2 | Conclusion > intermediate conclusion | 37 | 50 | 26 | 0.520 | 0.703 | 0.598 |
| 2 | Example > non-exhaustive listing | 17 | 27 | 16 | 0.593 | 0.941 | 0.727 |
| 2 | Example > rhetorical example | 5 | 4 | 4 | 1.000 | 0.800 | 0.889 |
| 2 | Knowledge > commonsense | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Knowledge > concept or definition | 6 | 7 | 5 | 0.714 | 0.833 | 0.769 |
| 2 | Knowledge > self-knowledge | 5 | 3 | 3 | 1.000 | 0.600 | 0.750 |
| 2 | Knowledge > world knowledge | 16 | 18 | 11 | 0.611 | 0.688 | 0.647 |
| 2 | Planning > announce output | 16 | 17 | 15 | 0.882 | 0.938 | 0.909 |
| 2 | Planning > announce the conclusion | 5 | 3 | 2 | 0.667 | 0.400 | 0.500 |
| 2 | Planning > global plan | 35 | 36 | 31 | 0.861 | 0.886 | 0.873 |
| 2 | Planning > initiate backtracking | 8 | 2 | 1 | 0.500 | 0.125 | 0.200 |
| 2 | Planning > initiate verification | 42 | 42 | 30 | 0.714 | 0.714 | 0.714 |
| 2 | Planning > local plan | 71 | 73 | 54 | 0.740 | 0.761 | 0.750 |
| 2 | Reasoning > calculation | 35 | 18 | 12 | 0.667 | 0.343 | 0.453 |
| 2 | Reasoning > commonsense reasoning | 12 | 8 | 8 | 1.000 | 0.667 | 0.800 |
| 2 | Reasoning > comparison | 17 | 14 | 10 | 0.714 | 0.588 | 0.645 |
| 2 | Reasoning > defining symbols | 15 | 18 | 8 | 0.444 | 0.533 | 0.485 |
| 2 | Reasoning > hedge word analysis | 13 | 2 | 2 | 1.000 | 0.154 | 0.267 |
| 2 | Reasoning > logical reasoning | 38 | 46 | 23 | 0.500 | 0.605 | 0.548 |
| 2 | Reasoning > option evaluation | 45 | 87 | 34 | 0.391 | 0.756 | 0.515 |
| 2 | Reasoning > speculation | 32 | 15 | 8 | 0.533 | 0.250 | 0.340 |
| 2 | Reflection > emotion or impression | 1 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Reflection > meta-evaluation of a step | 35 | 33 | 24 | 0.727 | 0.686 | 0.706 |
| 2 | Reflection > rhetorical phrase | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Restatement > rephrasing an earlier sentence | 70 | 38 | 32 | 0.842 | 0.457 | 0.593 |
| 2 | Restatement > rephrasing the prompt | 53 | 56 | 49 | 0.875 | 0.925 | 0.899 |
| 3 | Assumption > assuming a missing premise by common practice > "$1.00 more" | 1 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > assuming an uncertain fact | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > branching (case split) | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > branching (case split) > algebra | 4 | 3 | 3 | 1.000 | 0.750 | 0.857 |
| 3 | Conclusion > final answer | 3 | 6 | 3 | 0.500 | 1.000 | 0.667 |
| 3 | Conclusion > intermediate conclusion | 37 | 50 | 26 | 0.520 | 0.703 | 0.598 |
| 3 | Example > non-exhaustive listing > algebra | 17 | 27 | 16 | 0.593 | 0.941 | 0.727 |
| 3 | Example > rhetorical example | 5 | 4 | 4 | 1.000 | 0.800 | 0.889 |
| 3 | Knowledge > commonsense | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > concept or definition > well-posedness | 6 | 7 | 5 | 0.714 | 0.833 | 0.769 |
| 3 | Knowledge > self-knowledge > evaluation context | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| 3 | Knowledge > self-knowledge > role | 4 | 2 | 2 | 1.000 | 0.500 | 0.667 |
| 3 | Knowledge > world knowledge > famous problem (CRT) | 16 | 18 | 11 | 0.611 | 0.688 | 0.647 |
| 3 | Planning > announce output | 16 | 17 | 15 | 0.882 | 0.938 | 0.909 |
| 3 | Planning > announce the conclusion | 5 | 3 | 2 | 0.667 | 0.400 | 0.500 |
| 3 | Planning > global plan | 35 | 36 | 31 | 0.861 | 0.886 | 0.873 |
| 3 | Planning > initiate backtracking | 8 | 2 | 1 | 0.500 | 0.125 | 0.200 |
| 3 | Planning > initiate verification | 42 | 42 | 30 | 0.714 | 0.714 | 0.714 |
| 3 | Planning > local plan | 71 | 73 | 54 | 0.740 | 0.761 | 0.750 |
| 3 | Reasoning > calculation | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > calculation > algebra | 35 | 17 | 11 | 0.647 | 0.314 | 0.423 |
| 3 | Reasoning > commonsense reasoning | 12 | 8 | 8 | 1.000 | 0.667 | 0.800 |
| 3 | Reasoning > comparison > option vs option | 8 | 4 | 2 | 0.500 | 0.250 | 0.333 |
| 3 | Reasoning > comparison > prompt vs original text | 9 | 10 | 8 | 0.800 | 0.889 | 0.842 |
| 3 | Reasoning > defining symbols > algebra | 15 | 18 | 8 | 0.444 | 0.533 | 0.485 |
| 3 | Reasoning > hedge word analysis | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > hedge word analysis > everyday reading | 4 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > hedge word analysis > mathematical reading | 8 | 1 | 1 | 1.000 | 0.125 | 0.222 |
| 3 | Reasoning > hedge word analysis > undecided | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > logical reasoning | 20 | 27 | 12 | 0.444 | 0.600 | 0.511 |
| 3 | Reasoning > logical reasoning > algebra | 18 | 19 | 6 | 0.316 | 0.333 | 0.324 |
| 3 | Reasoning > option evaluation > (A) | 11 | 14 | 6 | 0.429 | 0.545 | 0.480 |
| 3 | Reasoning > option evaluation > (B) | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > option evaluation > (C) | 25 | 48 | 20 | 0.417 | 0.800 | 0.548 |
| 3 | Reasoning > option evaluation > (E) | 9 | 14 | 8 | 0.571 | 0.889 | 0.696 |
| 3 | Reasoning > option evaluation > (F) | 0 | 10 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > speculation > intent of the question writer | 32 | 15 | 8 | 0.533 | 0.250 | 0.340 |
| 3 | Reflection > emotion or impression | 1 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step | 14 | 16 | 12 | 0.750 | 0.857 | 0.800 |
| 3 | Reflection > meta-evaluation of a step > option (A) | 0 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step > option (B) | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| 3 | Reflection > meta-evaluation of a step > option (C) | 7 | 4 | 2 | 0.500 | 0.286 | 0.364 |
| 3 | Reflection > meta-evaluation of a step > option (D) | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 3 | Reflection > meta-evaluation of a step > option (E) | 5 | 4 | 2 | 0.500 | 0.400 | 0.444 |
| 3 | Reflection > meta-evaluation of a step > option (F) | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| 3 | Reflection > rhetorical phrase | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Restatement > rephrasing an earlier sentence | 70 | 38 | 32 | 0.842 | 0.457 | 0.593 |
| 3 | Restatement > rephrasing the prompt > answer-format instruction | 7 | 9 | 7 | 0.778 | 1.000 | 0.875 |
| 3 | Restatement > rephrasing the prompt > option text | 24 | 29 | 22 | 0.759 | 0.917 | 0.830 |
| 3 | Restatement > rephrasing the prompt > question text | 22 | 18 | 17 | 0.944 | 0.773 | 0.850 |

### Twenty most frequent confusion pairs at Level 1 (reference → other, primary label)

| reference | other | count |
|---|---|---|
| Reasoning | Planning | 18 |
| Reasoning | Conclusion | 14 |
| Restatement | Reasoning | 13 |
| Planning | Restatement | 11 |
| Reflection | Reasoning | 10 |
| Restatement | Example | 10 |
| Knowledge | Reasoning | 9 |
| Planning | Reasoning | 8 |
| Reasoning | Reflection | 6 |
| Conclusion | Reasoning | 6 |
| Restatement | Conclusion | 6 |
| Restatement | Knowledge | 6 |
| Restatement | Planning | 5 |
| Planning | Reflection | 4 |
| Planning | Conclusion | 4 |
| Reasoning | Restatement | 3 |
| Assumption | Planning | 2 |
| Example | Reasoning | 2 |
| Conclusion | Reflection | 2 |
| Assumption | Reasoning | 1 |

### Twenty most frequent confusion pairs at Level 2 (reference → other, primary label)

| reference | other | count |
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
| Reasoning > comparison | Reasoning > option evaluation | 5 |
| Conclusion > intermediate conclusion | Reasoning > option evaluation | 5 |
| Restatement > rephrasing an earlier sentence | Reasoning > defining symbols | 5 |
| Restatement > rephrasing an earlier sentence | Knowledge > world knowledge | 5 |
| Reasoning > option evaluation | Conclusion > intermediate conclusion | 4 |
| Reasoning > option evaluation | Planning > local plan | 4 |
| Restatement > rephrasing an earlier sentence | Planning > local plan | 4 |
| Reasoning > commonsense reasoning | Reasoning > logical reasoning | 4 |
| Reasoning > defining symbols | Reasoning > calculation | 4 |
| Reasoning > calculation | Planning > initiate verification | 3 |

### Residue: 235 sentences whose full-path set differs (first 30; the C-trace rows are held out of the prompt work)

| trace | s | reference | other | text |
|---|---|---|---|---|
| c004 | 0 | Planning > global plan | Reflection > rhetorical phrase | Here's a thinking process that leads to the suggested answer: |
| c004 | 12 | Restatement > rephrasing the prompt > question text | Planning > local plan | ⏎    *   *Goal:* Find cost of Ball. |
| c004 | 17 | Reasoning > calculation > algebra | Planning > local plan | ⏎        *   Does Bat > Ball? |
| c004 | 18 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | \$1.05 > \$0.05. |
| c004 | 20 | Reasoning > calculation > algebra | Planning > local plan | ⏎        *   Is the sum \$1.10? |
| c004 | 22 | Reasoning > logical reasoning > algebra | Conclusion > intermediate conclusion | ⏎        *   *Result:* \$0.05 is a *possible* solution. |
| c004 | 25 | Reasoning > calculation > algebra | Planning > local plan | ⏎        *   Does Bat > Ball? |
| c004 | 26 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | \$1.09 > \$0.01. |
| c004 | 28 | Reasoning > calculation > algebra | Planning > local plan | ⏎        *   Is the sum \$1.10? |
| c004 | 30 | Reasoning > logical reasoning > algebra | Conclusion > intermediate conclusion | ⏎        *   *Result:* \$0.01 is *also* a possible solution. |
| c004 | 33 | Reasoning > calculation > algebra | Planning > local plan | ⏎        *   Does Bat > Ball? |
| c004 | 34 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | \$0.55 is not greater than \$0.55 (it's equal). |
| c004 | 35 | Reasoning > logical reasoning > algebra | Conclusion > intermediate conclusion | ⏎        *   *Result:* \$0.55 is not a solution. |
| c004 | 39 | Knowledge > world knowledge > famous problem (CRT) | Reasoning > logical reasoning | ⏎    *   *The Trap:* Most people intuitively answer \$0.10 (Ball) and \$1.00 (Bat). |
| c004 | 40 | Reasoning > calculation > algebra | Planning > initiate verification | Why? |
| c004 | 41 | Reasoning > calculation > algebra | Reasoning > logical reasoning | Because \$1.00 + \$0.10 = \$1.10. |
| c004 | 43 | Planning > initiate verification || Restatement > rephrasing the prompt > question text | Planning > initiate verification | ⏎    *   *Check the text provided in the prompt again carefully:* "A bat and a ball cost \$1.10 in total. |
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
| c004 | 82 | Reasoning > speculation > intent of the question writer | Reflection > emotion or impression | ⏎    *   The prompt is a trick. |
| c004 | 83 | Knowledge > world knowledge > famous problem (CRT) | Reasoning > logical reasoning | It looks like the "Cognitive Reflection Test" (CRT) question. |
### Run 1: structural metrics judge vs reviewed

| scope | block openers: reviewed / judge | hits / misses (near) / extras | block P / R / F1 | rule agrees on hits | next node after cut: agree / cuts (rate) | node ends: hits / misses / extras | node F1 | matched nodes L1 agree (rate) | reviewed nodes split / merged | sentences: L1 wrong / L2 wrong / L3 wrong / all right | L1 share of disagreements |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e036 | 37 / 33 | 28 / 9 (3) / 5 | 0.848 / 0.757 / 0.800 | 28 / 28 | 29 / 36 (0.806) | 117 / 29 / 13 | 0.848 | 112 / 146 (0.767) | 12 / 46 | 44 / 22 / 5 / 183 | 0.620 |
| c004 | 46 / 48 | 41 / 5 (2) / 7 | 0.854 / 0.891 / 0.872 | 39 / 41 | 40 / 45 (0.889) | 167 / 26 / 65 | 0.786 | 142 / 193 (0.736) | 29 / 34 | 109 / 49 / 6 / 211 | 0.665 |
| pooled | 83 / 81 | 69 / 14 (5) / 12 | 0.852 / 0.831 / 0.841 | 67 / 69 | 69 / 81 (0.852) | 284 / 55 / 78 | 0.810 | 254 / 339 (0.749) | 41 / 80 | 153 / 71 / 11 / 394 | 0.651 |

Next-node confusions (reviewed → judge, pooled): Planning → Restatement 4; Planning → Reasoning 3; Planning → Reflection 2; Assumption → Planning 2; Planning → Conclusion 1
e036: missed reviewed openers at s19, s77, s96, s117, s144, s182, s193, s213, s245; extra judge openers at s91, s113, s145, s164, s244
c004: missed reviewed openers at s13, s114, s216, s227, s288; extra judge openers at s1, s12, s40, s289, s291, s328, s366
## pytest output

```
........................................................................ [ 70%]
..............................                                           [100%]
102 passed in 0.31s
```
