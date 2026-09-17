# TEST_REPORT — t4_judge — 2026-09-17 00:12

Test of pipeline step (4/9), the judge on the two source traces (`scripts/s1_judge.py`, `scripts/derivation.py`), per pipeline v1 Section 9 item 6. Git commit `90c8358c5561adf6006bd7c0289a7b25903a9338`; model `claude-sonnet-5` (sonnet), max_tokens 8000, temperature None (not sent: the model rejects sampling parameters), thinking {'type': 'disabled'}; prompt v2 sha256 `98ac17659798c184bc75fba6336007fb87e0b771e5272dfa05bdc90781b2a65c`; inventory sha256 `51c5d0d142863a1d6461bcc871b08401f80c02abce45c31445de2cae07798ba2`; sentences `runs/tests/t2_split_2026-09-16_2224/sentences_source.jsonl`. Run folder `runs/experiments/judge_source_sonnet_v2_2026-09-17_0012`.

## Result: PASS (6/6 checks passed)

## Checks

- PASS — check 1, derivation gate on the reviewed labels (offline) — e036: 254 sentences; blocks 37 derived vs 37 listed; nodes 146 vs 146; interval differences 0, opener rule/label differences 0, name differences 0 (listing names with a '(1)' count stripped: 97); c004: 375 sentences; blocks 46 derived vs 46 listed; nodes 193 vs 193; interval differences 0, opener rule/label differences 0, name differences 0 (listing names with a '(1)' count stripped: 121)
- PASS — check 2, dry run (requests built, nothing called) — e036: 254 sentences, about 8774 input tokens (characters/4); every index exactly once in the user message: True; c004: 375 sentences, about 10799 input tokens (characters/4); every index exactly once in the user message: True; requests written to dry_run/requests/
- PASS — check 3, e036 judged — attempts 2, valid True, model echoed 'claude-sonnet-5', stop reasons ['max_tokens', 'end_turn']; tokens input 19355, cache read 8109, cache write 8109, output 10005; cost $0.160654; judge nodes 157 / blocks 33 vs reviewed 146 / 37; retry message: Your labeling was rejected: unparsable: expected '<first>-<last> <code>' or '<index> <code>' at line 1: <think>. Output the complete labeling again, every index from 0 to 253 exactly once, one run per line, codes only.; error: unparsable: expected '<first>-<last> <code>' or '<index> <code>' at line 1: <think>; agreement (this trace): Level 1 exact 0.858 kappa 0.830, Level 2 exact 0.807 kappa 0.800, Level 3 exact 0.787 kappa 0.782; residue rows 54
- PASS — check 4, c004 judged — attempts 2, valid True, model echoed 'claude-sonnet-5', stop reasons ['max_tokens', 'end_turn']; tokens input 26891, cache read 16218, cache write 0, output 10663; cost $0.163656; judge nodes 195 / blocks 46 vs reviewed 193 / 46; retry message: Your labeling was rejected: unparsable: expected '<first>-<last> <code>' or '<index> <code>' at line 1: <think>. Output the complete labeling again, every index from 0 to 374 exactly once, one run per line, codes only.; error: unparsable: expected '<first>-<last> <code>' or '<index> <code>' at line 1: <think>; agreement (this trace): Level 1 exact 0.811 kappa 0.764, Level 2 exact 0.648 kappa 0.632, Level 3 exact 0.635 kappa 0.624; residue rows 137
- PASS — check 5, agreement over both traces — 629 sentences; Level 1: exact 0.830, Jaccard 0.837, kappa 0.796; Level 2: exact 0.712, Jaccard 0.717, kappa 0.701; Level 3: exact 0.696, Jaccard 0.701, kappa 0.689; residue rows 191; total cost $0.324310; agreement_source.csv, residue_source.csv, confusions_source.csv copied here
- PASS — check 6, pytest on scripts/tests — exit code 0; last line: 87 passed in 0.28s

## Agreement (judge vs reviewed, both traces)

| level | n | exact-match rate | mean Jaccard | kappa (primary label) | primary agreement |
|---|---|---|---|---|---|
| Level 1 | 629 | 0.8299 | 0.8368 | 0.7956 | 0.8394 |
| Level 1 > Level 2 | 629 | 0.7122 | 0.7167 | 0.7009 | 0.7202 |
| full path | 629 | 0.6963 | 0.7008 | 0.6885 | 0.7043 |

| level | label | n_reviewed | n_judge | tp | precision | recall | F1 |
|---|---|---|---|---|---|---|---|
| 1 | Assumption | 7 | 3 | 3 | 1.000 | 0.429 | 0.600 |
| 1 | Conclusion | 40 | 68 | 35 | 0.515 | 0.875 | 0.648 |
| 1 | Example | 22 | 33 | 21 | 0.636 | 0.955 | 0.764 |
| 1 | Knowledge | 30 | 30 | 27 | 0.900 | 0.900 | 0.900 |
| 1 | Planning | 177 | 169 | 162 | 0.959 | 0.915 | 0.936 |
| 1 | Reasoning | 206 | 178 | 162 | 0.910 | 0.786 | 0.844 |
| 1 | Reflection | 36 | 35 | 28 | 0.800 | 0.778 | 0.789 |
| 1 | Restatement | 123 | 117 | 96 | 0.821 | 0.780 | 0.800 |
| 2 | Assumption > assuming a missing premise by common practice | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Assumption > assuming an uncertain fact | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Assumption > branching (case split) | 5 | 3 | 3 | 1.000 | 0.600 | 0.750 |
| 2 | Conclusion > final answer | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 2 | Conclusion > intermediate conclusion | 37 | 65 | 32 | 0.492 | 0.865 | 0.627 |
| 2 | Example > non-exhaustive listing | 17 | 33 | 16 | 0.485 | 0.941 | 0.640 |
| 2 | Example > rhetorical example | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Knowledge > commonsense | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Knowledge > concept or definition | 6 | 5 | 5 | 1.000 | 0.833 | 0.909 |
| 2 | Knowledge > self-knowledge | 5 | 5 | 5 | 1.000 | 1.000 | 1.000 |
| 2 | Knowledge > world knowledge | 16 | 20 | 16 | 0.800 | 1.000 | 0.889 |
| 2 | Planning > announce output | 16 | 17 | 16 | 0.941 | 1.000 | 0.970 |
| 2 | Planning > announce the conclusion | 5 | 3 | 3 | 1.000 | 0.600 | 0.750 |
| 2 | Planning > global plan | 35 | 36 | 32 | 0.889 | 0.914 | 0.901 |
| 2 | Planning > initiate backtracking | 8 | 3 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Planning > initiate verification | 42 | 42 | 34 | 0.810 | 0.810 | 0.810 |
| 2 | Planning > local plan | 71 | 68 | 61 | 0.897 | 0.859 | 0.878 |
| 2 | Reasoning > calculation | 35 | 14 | 11 | 0.786 | 0.314 | 0.449 |
| 2 | Reasoning > commonsense reasoning | 12 | 14 | 11 | 0.786 | 0.917 | 0.846 |
| 2 | Reasoning > comparison | 17 | 12 | 10 | 0.833 | 0.588 | 0.690 |
| 2 | Reasoning > defining symbols | 15 | 7 | 6 | 0.857 | 0.400 | 0.545 |
| 2 | Reasoning > hedge word analysis | 13 | 5 | 4 | 0.800 | 0.308 | 0.444 |
| 2 | Reasoning > logical reasoning | 38 | 46 | 24 | 0.522 | 0.632 | 0.571 |
| 2 | Reasoning > option evaluation | 45 | 69 | 34 | 0.493 | 0.756 | 0.596 |
| 2 | Reasoning > speculation | 32 | 11 | 10 | 0.909 | 0.312 | 0.465 |
| 2 | Reflection > emotion or impression | 1 | 4 | 1 | 0.250 | 1.000 | 0.400 |
| 2 | Reflection > meta-evaluation of a step | 35 | 31 | 26 | 0.839 | 0.743 | 0.788 |
| 2 | Restatement > rephrasing an earlier sentence | 70 | 60 | 45 | 0.750 | 0.643 | 0.692 |
| 2 | Restatement > rephrasing the prompt | 53 | 57 | 49 | 0.860 | 0.925 | 0.891 |
| 3 | Assumption > assuming a missing premise by common practice > "$1.00 more" | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > assuming an uncertain fact | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > branching (case split) | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > branching (case split) > algebra | 4 | 3 | 3 | 1.000 | 0.750 | 0.857 |
| 3 | Conclusion > final answer | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 3 | Conclusion > intermediate conclusion | 37 | 65 | 32 | 0.492 | 0.865 | 0.627 |
| 3 | Example > non-exhaustive listing | 0 | 5 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Example > non-exhaustive listing > algebra | 17 | 28 | 16 | 0.571 | 0.941 | 0.711 |
| 3 | Example > rhetorical example | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > commonsense | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > concept or definition > well-posedness | 6 | 5 | 5 | 1.000 | 0.833 | 0.909 |
| 3 | Knowledge > self-knowledge > evaluation context | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| 3 | Knowledge > self-knowledge > role | 4 | 4 | 4 | 1.000 | 1.000 | 1.000 |
| 3 | Knowledge > world knowledge | 0 | 6 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > world knowledge > famous problem (CRT) | 16 | 14 | 13 | 0.929 | 0.812 | 0.867 |
| 3 | Planning > announce output | 16 | 17 | 16 | 0.941 | 1.000 | 0.970 |
| 3 | Planning > announce the conclusion | 5 | 3 | 3 | 1.000 | 0.600 | 0.750 |
| 3 | Planning > global plan | 35 | 36 | 32 | 0.889 | 0.914 | 0.901 |
| 3 | Planning > initiate backtracking | 8 | 3 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Planning > initiate verification | 42 | 42 | 34 | 0.810 | 0.810 | 0.810 |
| 3 | Planning > local plan | 71 | 68 | 61 | 0.897 | 0.859 | 0.878 |
| 3 | Reasoning > calculation > algebra | 35 | 14 | 11 | 0.786 | 0.314 | 0.449 |
| 3 | Reasoning > commonsense reasoning | 12 | 14 | 11 | 0.786 | 0.917 | 0.846 |
| 3 | Reasoning > comparison > option vs option | 8 | 6 | 4 | 0.667 | 0.500 | 0.571 |
| 3 | Reasoning > comparison > prompt vs original text | 9 | 6 | 6 | 1.000 | 0.667 | 0.800 |
| 3 | Reasoning > defining symbols > algebra | 15 | 7 | 6 | 0.857 | 0.400 | 0.545 |
| 3 | Reasoning > hedge word analysis > everyday reading | 4 | 2 | 1 | 0.500 | 0.250 | 0.333 |
| 3 | Reasoning > hedge word analysis > mathematical reading | 8 | 1 | 1 | 1.000 | 0.125 | 0.222 |
| 3 | Reasoning > hedge word analysis > undecided | 1 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > logical reasoning | 20 | 20 | 13 | 0.650 | 0.650 | 0.650 |
| 3 | Reasoning > logical reasoning > algebra | 18 | 26 | 6 | 0.231 | 0.333 | 0.273 |
| 3 | Reasoning > option evaluation > (A) | 11 | 7 | 5 | 0.714 | 0.455 | 0.556 |
| 3 | Reasoning > option evaluation > (B) | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > option evaluation > (C) | 25 | 37 | 21 | 0.568 | 0.840 | 0.677 |
| 3 | Reasoning > option evaluation > (E) | 9 | 17 | 8 | 0.471 | 0.889 | 0.615 |
| 3 | Reasoning > option evaluation > (F) | 0 | 7 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > speculation > intent of the question writer | 32 | 11 | 10 | 0.909 | 0.312 | 0.465 |
| 3 | Reflection > emotion or impression | 1 | 4 | 1 | 0.250 | 1.000 | 0.400 |
| 3 | Reflection > meta-evaluation of a step | 14 | 14 | 14 | 1.000 | 1.000 | 1.000 |
| 3 | Reflection > meta-evaluation of a step > option (A) | 0 | 3 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step > option (B) | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| 3 | Reflection > meta-evaluation of a step > option (C) | 7 | 2 | 1 | 0.500 | 0.143 | 0.222 |
| 3 | Reflection > meta-evaluation of a step > option (D) | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 3 | Reflection > meta-evaluation of a step > option (E) | 5 | 4 | 3 | 0.750 | 0.600 | 0.667 |
| 3 | Reflection > meta-evaluation of a step > option (F) | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 3 | Restatement > rephrasing an earlier sentence | 70 | 60 | 45 | 0.750 | 0.643 | 0.692 |
| 3 | Restatement > rephrasing the prompt > answer-format instruction | 7 | 6 | 6 | 1.000 | 0.857 | 0.923 |
| 3 | Restatement > rephrasing the prompt > option text | 24 | 30 | 23 | 0.767 | 0.958 | 0.852 |
| 3 | Restatement > rephrasing the prompt > question text | 22 | 21 | 20 | 0.952 | 0.909 | 0.930 |

### Twenty most frequent confusion pairs at Level 1 (reviewed → judge, primary label)

| reviewed | judge | count |
|---|---|---|
| Reasoning | Conclusion | 25 |
| Reasoning | Restatement | 12 |
| Restatement | Example | 12 |
| Planning | Restatement | 7 |
| Reflection | Reasoning | 6 |
| Restatement | Conclusion | 6 |
| Reasoning | Reflection | 5 |
| Planning | Reasoning | 5 |
| Restatement | Planning | 4 |
| Restatement | Reasoning | 2 |
| Assumption | Planning | 2 |
| Conclusion | Restatement | 2 |
| Knowledge | Reasoning | 2 |
| Conclusion | Reasoning | 2 |
| Assumption | Reasoning | 1 |
| Restatement | Knowledge | 1 |
| Reflection | Conclusion | 1 |
| Restatement | Reflection | 1 |
| Example | Reasoning | 1 |
| Planning | Conclusion | 1 |

### Twenty most frequent confusion pairs at Level 2 (reviewed → judge, primary label)

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
| Reflection > meta-evaluation of a step | Reasoning > option evaluation | 5 |
| Example > rhetorical example | Example > non-exhaustive listing | 5 |
| Restatement > rephrasing an earlier sentence | Planning > local plan | 4 |
| Reasoning > comparison | Reasoning > option evaluation | 3 |
| Planning > initiate verification | Planning > initiate backtracking | 3 |
| Reasoning > speculation | Reasoning > logical reasoning | 3 |
| Reasoning > calculation | Conclusion > intermediate conclusion | 3 |
| Reasoning > speculation | Conclusion > intermediate conclusion | 3 |
| Reasoning > option evaluation | Reflection > meta-evaluation of a step | 3 |
| Reasoning > calculation | Reasoning > commonsense reasoning | 2 |

### Residue: 191 sentences whose full-path set differs (first thirty)

| trace | s | reviewed | judge | text |
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
| c004 | 47 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | Any price for the ball ($x$) where $0 < x < 0.55$ works. |
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
| c004 | 82 | Reasoning > speculation > intent of the question writer | Reflection > emotion or impression | ⏎    *   The prompt is a trick. |
| c004 | 92 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | If $b + B = 1.10$ and $B > b$ (where $B$ is bat, $b$ is ball), then $b$ can be any value in $(0, 0.55)$. |
| c004 | 93 | Reasoning > option evaluation > (A) | Conclusion > intermediate conclusion | ⏎    *   Therefore, "It is \$0.05" (A) is logically false based *only* on the provided text. |
| c004 | 96 | Restatement > rephrasing the prompt > option text | Reasoning > option evaluation > (C) | It then adds "...but the answer is most likely \$0.05". |
| c004 | 97 | Reasoning > hedge word analysis > everyday reading | Reasoning > option evaluation > (C) | This acknowledges the cultural context/intent of the riddle. |
## pytest output

```
........................................................................ [ 82%]
...............                                                          [100%]
87 passed in 0.28s
```
