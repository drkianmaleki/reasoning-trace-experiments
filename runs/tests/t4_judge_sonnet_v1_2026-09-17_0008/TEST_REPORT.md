# TEST_REPORT — t4_judge — 2026-09-17 00:08

Test of pipeline step (4/9), the judge on the two source traces (`scripts/s1_judge.py`, `scripts/derivation.py`), per pipeline v1 Section 9 item 6. Git commit `90c8358c5561adf6006bd7c0289a7b25903a9338`; model `claude-sonnet-5` (sonnet), max_tokens 8000, temperature None (not sent: the model rejects sampling parameters), thinking {'type': 'disabled'}; prompt v1 sha256 `2d9ebdd3f345e58a283c915cd03d64f1a1918becfb6a13cfbebbec9f22c5f69f`; inventory sha256 `4054e9dc9378af3fac2a643dae2b918ffb98bd2e348200b2fffb403b54babf8b`; sentences `runs/tests/t2_split_2026-09-16_2224/sentences_source.jsonl`. Run folder `runs/experiments/judge_source_sonnet_v1_2026-09-17_0008`.

## Result: PASS (6/6 checks passed)

## Checks

- PASS — check 1, derivation gate on the reviewed labels (offline) — e036: 254 sentences; blocks 37 derived vs 37 listed; nodes 146 vs 146; interval differences 0, opener rule/label differences 0, name differences 0 (listing names with a '(1)' count stripped: 97); c004: 375 sentences; blocks 46 derived vs 46 listed; nodes 193 vs 193; interval differences 0, opener rule/label differences 0, name differences 0 (listing names with a '(1)' count stripped: 121)
- PASS — check 2, dry run (requests built, nothing called) — e036: 254 sentences, about 7761 input tokens (characters/4); every index exactly once in the user message: True; c004: 375 sentences, about 9786 input tokens (characters/4); every index exactly once in the user message: True; requests written to dry_run/requests/
- PASS — check 3, e036 judged — attempts 2, valid True, model echoed 'claude-sonnet-5', stop reasons ['max_tokens', 'end_turn']; tokens input 19355, cache read 6718, cache write 6718, output 9947; cost $0.156319; judge nodes 152 / blocks 37 vs reviewed 146 / 37; retry message: Your labeling was rejected: unparsable: expected '<first>-<last> <code>' or '<index> <code>' at line 1: <think>. Output the complete labeling again, every index from 0 to 253 exactly once, one run per line, codes only.; error: unparsable: expected '<first>-<last> <code>' or '<index> <code>' at line 1: <think>; agreement (this trace): Level 1 exact 0.791 kappa 0.746, Level 2 exact 0.661 kappa 0.641, Level 3 exact 0.634 kappa 0.617; residue rows 93
- PASS — check 4, c004 judged — attempts 2, valid True, model echoed 'claude-sonnet-5', stop reasons ['max_tokens', 'end_turn']; tokens input 26891, cache read 13436, cache write 0, output 11574; cost $0.172209; judge nodes 202 / blocks 40 vs reviewed 193 / 46; retry message: Your labeling was rejected: unparsable: expected '<first>-<last> <code>' or '<index> <code>' at line 1: <think>. Output the complete labeling again, every index from 0 to 374 exactly once, one run per line, codes only.; error: unparsable: expected '<first>-<last> <code>' or '<index> <code>' at line 1: <think>; agreement (this trace): Level 1 exact 0.747 kappa 0.662, Level 2 exact 0.579 kappa 0.556, Level 3 exact 0.571 kappa 0.557; residue rows 161
- PASS — check 5, agreement over both traces — 629 sentences; Level 1: exact 0.765, Jaccard 0.773, kappa 0.707; Level 2: exact 0.612, Jaccard 0.618, kappa 0.593; Level 3: exact 0.596, Jaccard 0.602, kappa 0.583; residue rows 254; total cost $0.328528; agreement_source.csv, residue_source.csv, confusions_source.csv copied here
- PASS — check 6, pytest on scripts/tests — exit code 0; last line: 87 passed in 0.62s

## Agreement (judge vs reviewed, both traces)

| level | n | exact-match rate | mean Jaccard | kappa (primary label) | primary agreement |
|---|---|---|---|---|---|
| Level 1 | 629 | 0.7647 | 0.7734 | 0.7072 | 0.7758 |
| Level 1 > Level 2 | 629 | 0.6121 | 0.6176 | 0.5932 | 0.6184 |
| full path | 629 | 0.5962 | 0.6017 | 0.5835 | 0.6025 |

| level | label | n_reviewed | n_judge | tp | precision | recall | F1 |
|---|---|---|---|---|---|---|---|
| 1 | Assumption | 7 | 5 | 4 | 0.800 | 0.571 | 0.667 |
| 1 | Conclusion | 40 | 39 | 30 | 0.769 | 0.750 | 0.759 |
| 1 | Example | 22 | 28 | 16 | 0.571 | 0.727 | 0.640 |
| 1 | Knowledge | 30 | 43 | 24 | 0.558 | 0.800 | 0.658 |
| 1 | Planning | 177 | 181 | 160 | 0.884 | 0.904 | 0.894 |
| 1 | Reasoning | 206 | 239 | 181 | 0.757 | 0.879 | 0.813 |
| 1 | Reflection | 36 | 23 | 18 | 0.783 | 0.500 | 0.610 |
| 1 | Restatement | 123 | 76 | 62 | 0.816 | 0.504 | 0.623 |
| 2 | Assumption > assuming a missing premise by common practice | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Assumption > assuming an uncertain fact | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Assumption > branching (case split) | 5 | 5 | 3 | 0.600 | 0.600 | 0.600 |
| 2 | Conclusion > final answer | 3 | 9 | 2 | 0.222 | 0.667 | 0.333 |
| 2 | Conclusion > intermediate conclusion | 37 | 30 | 23 | 0.767 | 0.622 | 0.687 |
| 2 | Example > non-exhaustive listing | 17 | 28 | 16 | 0.571 | 0.941 | 0.711 |
| 2 | Example > rhetorical example | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Knowledge > commonsense | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Knowledge > concept or definition | 6 | 6 | 5 | 0.833 | 0.833 | 0.833 |
| 2 | Knowledge > self-knowledge | 5 | 4 | 3 | 0.750 | 0.600 | 0.667 |
| 2 | Knowledge > world knowledge | 16 | 33 | 15 | 0.455 | 0.938 | 0.612 |
| 2 | Planning > announce output | 16 | 18 | 15 | 0.833 | 0.938 | 0.882 |
| 2 | Planning > announce the conclusion | 5 | 7 | 4 | 0.571 | 0.800 | 0.667 |
| 2 | Planning > global plan | 35 | 13 | 12 | 0.923 | 0.343 | 0.500 |
| 2 | Planning > initiate backtracking | 8 | 5 | 2 | 0.400 | 0.250 | 0.308 |
| 2 | Planning > initiate verification | 42 | 36 | 31 | 0.861 | 0.738 | 0.795 |
| 2 | Planning > local plan | 71 | 102 | 62 | 0.608 | 0.873 | 0.717 |
| 2 | Reasoning > calculation | 35 | 22 | 18 | 0.818 | 0.514 | 0.632 |
| 2 | Reasoning > commonsense reasoning | 12 | 8 | 8 | 1.000 | 0.667 | 0.800 |
| 2 | Reasoning > comparison | 17 | 12 | 8 | 0.667 | 0.471 | 0.552 |
| 2 | Reasoning > defining symbols | 15 | 20 | 10 | 0.500 | 0.667 | 0.571 |
| 2 | Reasoning > hedge word analysis | 13 | 3 | 3 | 1.000 | 0.231 | 0.375 |
| 2 | Reasoning > logical reasoning | 38 | 70 | 32 | 0.457 | 0.842 | 0.593 |
| 2 | Reasoning > option evaluation | 45 | 89 | 37 | 0.416 | 0.822 | 0.552 |
| 2 | Reasoning > speculation | 32 | 15 | 10 | 0.667 | 0.312 | 0.426 |
| 2 | Reflection > emotion or impression | 1 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Reflection > meta-evaluation of a step | 35 | 20 | 17 | 0.850 | 0.486 | 0.618 |
| 2 | Reflection > rhetorical phrase | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Restatement > rephrasing an earlier sentence | 70 | 12 | 7 | 0.583 | 0.100 | 0.171 |
| 2 | Restatement > rephrasing the prompt | 53 | 64 | 52 | 0.812 | 0.981 | 0.889 |
| 3 | Assumption > assuming a missing premise by common practice > "$1.00 more" | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > assuming an uncertain fact | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > branching (case split) | 1 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > branching (case split) > algebra | 4 | 4 | 3 | 0.750 | 0.750 | 0.750 |
| 3 | Conclusion > final answer | 3 | 9 | 2 | 0.222 | 0.667 | 0.333 |
| 3 | Conclusion > intermediate conclusion | 37 | 30 | 23 | 0.767 | 0.622 | 0.687 |
| 3 | Example > non-exhaustive listing > algebra | 17 | 28 | 16 | 0.571 | 0.941 | 0.711 |
| 3 | Example > rhetorical example | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > commonsense | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > concept or definition > well-posedness | 6 | 6 | 5 | 0.833 | 0.833 | 0.833 |
| 3 | Knowledge > self-knowledge > evaluation context | 1 | 2 | 1 | 0.500 | 1.000 | 0.667 |
| 3 | Knowledge > self-knowledge > role | 4 | 2 | 2 | 1.000 | 0.500 | 0.667 |
| 3 | Knowledge > world knowledge | 0 | 4 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > world knowledge > famous problem (CRT) | 16 | 29 | 12 | 0.414 | 0.750 | 0.533 |
| 3 | Planning > announce output | 16 | 18 | 15 | 0.833 | 0.938 | 0.882 |
| 3 | Planning > announce the conclusion | 5 | 7 | 4 | 0.571 | 0.800 | 0.667 |
| 3 | Planning > global plan | 35 | 13 | 12 | 0.923 | 0.343 | 0.500 |
| 3 | Planning > initiate backtracking | 8 | 5 | 2 | 0.400 | 0.250 | 0.308 |
| 3 | Planning > initiate verification | 42 | 36 | 31 | 0.861 | 0.738 | 0.795 |
| 3 | Planning > local plan | 71 | 102 | 62 | 0.608 | 0.873 | 0.717 |
| 3 | Reasoning > calculation | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > calculation > algebra | 35 | 21 | 17 | 0.810 | 0.486 | 0.607 |
| 3 | Reasoning > commonsense reasoning | 12 | 8 | 8 | 1.000 | 0.667 | 0.800 |
| 3 | Reasoning > comparison > option vs option | 8 | 4 | 2 | 0.500 | 0.250 | 0.333 |
| 3 | Reasoning > comparison > prompt vs original text | 9 | 8 | 6 | 0.750 | 0.667 | 0.706 |
| 3 | Reasoning > defining symbols > algebra | 15 | 20 | 10 | 0.500 | 0.667 | 0.571 |
| 3 | Reasoning > hedge word analysis | 0 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > hedge word analysis > everyday reading | 4 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > hedge word analysis > mathematical reading | 8 | 1 | 1 | 1.000 | 0.125 | 0.222 |
| 3 | Reasoning > hedge word analysis > undecided | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > logical reasoning | 20 | 37 | 19 | 0.514 | 0.950 | 0.667 |
| 3 | Reasoning > logical reasoning > algebra | 18 | 33 | 11 | 0.333 | 0.611 | 0.431 |
| 3 | Reasoning > option evaluation > (A) | 11 | 15 | 10 | 0.667 | 0.909 | 0.769 |
| 3 | Reasoning > option evaluation > (B) | 0 | 3 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > option evaluation > (C) | 25 | 41 | 20 | 0.488 | 0.800 | 0.606 |
| 3 | Reasoning > option evaluation > (D) | 0 | 3 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > option evaluation > (E) | 9 | 15 | 7 | 0.467 | 0.778 | 0.583 |
| 3 | Reasoning > option evaluation > (F) | 0 | 12 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > speculation > intent of the question writer | 32 | 15 | 10 | 0.667 | 0.312 | 0.426 |
| 3 | Reflection > emotion or impression | 1 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step | 14 | 15 | 12 | 0.800 | 0.857 | 0.828 |
| 3 | Reflection > meta-evaluation of a step > option (B) | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step > option (C) | 7 | 3 | 3 | 1.000 | 0.429 | 0.600 |
| 3 | Reflection > meta-evaluation of a step > option (D) | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step > option (E) | 5 | 2 | 2 | 1.000 | 0.400 | 0.571 |
| 3 | Reflection > meta-evaluation of a step > option (F) | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > rhetorical phrase | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Restatement > rephrasing an earlier sentence | 70 | 12 | 7 | 0.583 | 0.100 | 0.171 |
| 3 | Restatement > rephrasing the prompt > answer-format instruction | 7 | 9 | 7 | 0.778 | 1.000 | 0.875 |
| 3 | Restatement > rephrasing the prompt > option text | 24 | 29 | 22 | 0.759 | 0.917 | 0.830 |
| 3 | Restatement > rephrasing the prompt > question text | 22 | 26 | 21 | 0.808 | 0.955 | 0.875 |

### Twenty most frequent confusion pairs at Level 1 (reviewed → judge, primary label)

| reviewed | judge | count |
|---|---|---|
| Restatement | Reasoning | 27 |
| Reflection | Reasoning | 15 |
| Restatement | Example | 12 |
| Restatement | Knowledge | 11 |
| Planning | Restatement | 7 |
| Reasoning | Planning | 7 |
| Planning | Reasoning | 7 |
| Reasoning | Restatement | 6 |
| Restatement | Planning | 6 |
| Conclusion | Reasoning | 5 |
| Restatement | Conclusion | 5 |
| Reasoning | Knowledge | 4 |
| Knowledge | Reasoning | 4 |
| Example | Knowledge | 4 |
| Reasoning | Conclusion | 3 |
| Reasoning | Reflection | 3 |
| Conclusion | Planning | 3 |
| Assumption | Planning | 2 |
| Example | Reasoning | 2 |
| Knowledge | Planning | 1 |

### Twenty most frequent confusion pairs at Level 2 (reviewed → judge, primary label)

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
| Reasoning > comparison | Reasoning > option evaluation | 6 |
| Restatement > rephrasing an earlier sentence | Planning > local plan | 6 |
| Reasoning > speculation | Reasoning > logical reasoning | 5 |
| Conclusion > intermediate conclusion | Reasoning > option evaluation | 5 |
| Restatement > rephrasing an earlier sentence | Reasoning > option evaluation | 5 |
| Conclusion > intermediate conclusion | Conclusion > final answer | 5 |
| Reasoning > option evaluation | Planning > local plan | 4 |
| Reasoning > commonsense reasoning | Reasoning > logical reasoning | 4 |
| Example > rhetorical example | Knowledge > world knowledge | 4 |
| Reasoning > logical reasoning | Conclusion > intermediate conclusion | 3 |

### Residue: 254 sentences whose full-path set differs (first thirty)

| trace | s | reviewed | judge | text |
|---|---|---|---|---|
| c004 | 1 | Planning > global plan | Planning > local plan | ⏎⏎1. |
| c004 | 2 | Planning > global plan | Planning > local plan | **Analyze the Request:** |
| c004 | 8 | Planning > global plan | Planning > local plan | ⏎⏎2. |
| c004 | 9 | Planning > global plan | Planning > local plan | **Analyze the Problem Statement (The "Bat and Ball" Problem):** |
| c004 | 13 | Planning > global plan | Planning > local plan | ⏎⏎3. |
| c004 | 14 | Planning > global plan | Planning > local plan | **Evaluate the Constraints & Ambiguity:** |
| c004 | 17 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | ⏎        *   Does Bat > Ball? |
| c004 | 20 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | ⏎        *   Is the sum \$1.10? |
| c004 | 22 | Reasoning > logical reasoning > algebra | Conclusion > intermediate conclusion | ⏎        *   *Result:* \$0.05 is a *possible* solution. |
| c004 | 25 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | ⏎        *   Does Bat > Ball? |
| c004 | 28 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | ⏎        *   Is the sum \$1.10? |
| c004 | 30 | Reasoning > logical reasoning > algebra | Conclusion > intermediate conclusion | ⏎        *   *Result:* \$0.01 is *also* a possible solution. |
| c004 | 33 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | ⏎        *   Does Bat > Ball? |
| c004 | 35 | Reasoning > logical reasoning > algebra | Conclusion > intermediate conclusion | ⏎        *   *Result:* \$0.55 is not a solution. |
| c004 | 36 | Planning > global plan | Planning > local plan | ⏎⏎4. |
| c004 | 37 | Planning > global plan | Planning > local plan | **Identify the Nature of the Question:** |
| c004 | 40 | Reasoning > calculation > algebra | Reasoning > logical reasoning | Why? |
| c004 | 41 | Reasoning > calculation > algebra | Reasoning > calculation | Because \$1.00 + \$0.10 = \$1.10. |
| c004 | 58 | Planning > global plan | Planning > local plan | ⏎⏎5. |
| c004 | 59 | Planning > global plan | Planning > local plan | **Evaluate the Options against the Textual Analysis:** |
| c004 | 60 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎⏎    *   *(A) It is \$0.05*: |
| c004 | 64 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(B) It is probably \$0.05*: |
| c004 | 65 | Reasoning > hedge word analysis > mathematical reading | Reasoning > hedge word analysis | "Probably" implies probability. |
| c004 | 66 | Reasoning > hedge word analysis > mathematical reading | Reasoning > hedge word analysis | Unless there's a distribution of prices given, we can't assign probability. |
| c004 | 67 | Reasoning > hedge word analysis > everyday reading || Reflection > meta-evaluation of a step > option (B) | Reasoning > option evaluation > (B) | However, in the context of riddles, this option acknowledges the likely intent of the user (referring to the famous riddle) while acknowledging the missing constraint. |
| c004 | 68 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(C) There is not enough information, but the answer is most likely \$0.05*: |
| c004 | 69 | Reflection > meta-evaluation of a step > option (C) | Reasoning > option evaluation > (C) | This is logically the most accurate description. |
| c004 | 72 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(D) I am not sure*: |
| c004 | 73 | Reflection > meta-evaluation of a step > option (D) | Reasoning > option evaluation > (D) | Too vague. |
| c004 | 74 | Planning > local plan | Restatement > rephrasing the prompt > option text | ⏎    *   *(E) The question is not well posed*: |
## pytest output

```
........................................................................ [ 82%]
...............                                                          [100%]
87 passed in 0.62s
```
