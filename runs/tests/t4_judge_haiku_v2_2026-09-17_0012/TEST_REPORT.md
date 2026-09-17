# TEST_REPORT — t4_judge — 2026-09-17 00:12

Test of pipeline step (4/9), the judge on the two source traces (`scripts/s1_judge.py`, `scripts/derivation.py`), per pipeline v1 Section 9 item 6. Git commit `90c8358c5561adf6006bd7c0289a7b25903a9338`; model `claude-haiku-4-5-20251001` (haiku), max_tokens 8000, temperature 0 (via extra_body), thinking omitted; prompt v2 sha256 `98ac17659798c184bc75fba6336007fb87e0b771e5272dfa05bdc90781b2a65c`; inventory sha256 `51c5d0d142863a1d6461bcc871b08401f80c02abce45c31445de2cae07798ba2`; sentences `runs/tests/t2_split_2026-09-16_2224/sentences_source.jsonl`. Run folder `runs/experiments/judge_source_haiku_v2_2026-09-17_0012`.

## Result: PASS (6/6 checks passed)

## Checks

- PASS — check 1, derivation gate on the reviewed labels (offline) — e036: 254 sentences; blocks 37 derived vs 37 listed; nodes 146 vs 146; interval differences 0, opener rule/label differences 0, name differences 0 (listing names with a '(1)' count stripped: 97); c004: 375 sentences; blocks 46 derived vs 46 listed; nodes 193 vs 193; interval differences 0, opener rule/label differences 0, name differences 0 (listing names with a '(1)' count stripped: 121)
- PASS — check 2, dry run (requests built, nothing called) — e036: 254 sentences, about 8774 input tokens (characters/4); every index exactly once in the user message: True; c004: 375 sentences, about 10799 input tokens (characters/4); every index exactly once in the user message: True; requests written to dry_run/requests/
- PASS — check 3, e036 judged — attempts 1, valid True, model echoed 'claude-haiku-4-5-20251001', stop reasons ['end_turn']; tokens input 4649, cache read 0, cache write 5858, output 592; cost $0.014932; judge nodes 49 / blocks 15 vs reviewed 146 / 37; agreement (this trace): Level 1 exact 0.535 kappa 0.422, Level 2 exact 0.362 kappa 0.328, Level 3 exact 0.319 kappa 0.289; residue rows 173
- PASS — check 4, c004 judged — attempts 1, valid True, model echoed 'claude-haiku-4-5-20251001', stop reasons ['end_turn']; tokens input 7834, cache read 5858, cache write 0, output 704; cost $0.011940; judge nodes 41 / blocks 5 vs reviewed 193 / 46; agreement (this trace): Level 1 exact 0.507 kappa 0.192, Level 2 exact 0.251 kappa 0.188, Level 3 exact 0.184 kappa 0.144; residue rows 306
- PASS — check 5, agreement over both traces — 629 sentences; Level 1: exact 0.518, Jaccard 0.525, kappa 0.336; Level 2: exact 0.296, Jaccard 0.299, kappa 0.254; Level 3: exact 0.238, Jaccard 0.241, kappa 0.210; residue rows 479; total cost $0.026871; agreement_source.csv, residue_source.csv, confusions_source.csv copied here
- PASS — check 6, pytest on scripts/tests — exit code 0; last line: 87 passed in 0.27s

## Agreement (judge vs reviewed, both traces)

| level | n | exact-match rate | mean Jaccard | kappa (primary label) | primary agreement |
|---|---|---|---|---|---|
| Level 1 | 629 | 0.5183 | 0.5246 | 0.3361 | 0.5231 |
| Level 1 > Level 2 | 629 | 0.2957 | 0.2989 | 0.2541 | 0.2989 |
| full path | 629 | 0.2385 | 0.2409 | 0.2100 | 0.2401 |

| level | label | n_reviewed | n_judge | tp | precision | recall | F1 |
|---|---|---|---|---|---|---|---|
| 1 | Assumption | 7 | 3 | 1 | 0.333 | 0.143 | 0.200 |
| 1 | Conclusion | 40 | 19 | 15 | 0.789 | 0.375 | 0.508 |
| 1 | Example | 22 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 1 | Knowledge | 30 | 13 | 5 | 0.385 | 0.167 | 0.233 |
| 1 | Planning | 177 | 74 | 64 | 0.865 | 0.362 | 0.510 |
| 1 | Reasoning | 206 | 446 | 197 | 0.442 | 0.956 | 0.604 |
| 1 | Reflection | 36 | 20 | 9 | 0.450 | 0.250 | 0.321 |
| 1 | Restatement | 123 | 54 | 43 | 0.796 | 0.350 | 0.486 |
| 2 | Assumption > assuming a missing premise by common practice | 1 | 3 | 1 | 0.333 | 1.000 | 0.500 |
| 2 | Assumption > assuming an uncertain fact | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Assumption > branching (case split) | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Conclusion > final answer | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 2 | Conclusion > intermediate conclusion | 37 | 16 | 12 | 0.750 | 0.324 | 0.453 |
| 2 | Example > non-exhaustive listing | 17 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Example > rhetorical example | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Knowledge > commonsense | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Knowledge > concept or definition | 6 | 8 | 2 | 0.250 | 0.333 | 0.286 |
| 2 | Knowledge > self-knowledge | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Knowledge > world knowledge | 16 | 5 | 3 | 0.600 | 0.188 | 0.286 |
| 2 | Planning > announce output | 16 | 15 | 10 | 0.667 | 0.625 | 0.645 |
| 2 | Planning > announce the conclusion | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Planning > global plan | 35 | 41 | 14 | 0.341 | 0.400 | 0.368 |
| 2 | Planning > initiate backtracking | 8 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Planning > initiate verification | 42 | 1 | 1 | 1.000 | 0.024 | 0.047 |
| 2 | Planning > local plan | 71 | 17 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Reasoning > calculation | 35 | 79 | 23 | 0.291 | 0.657 | 0.404 |
| 2 | Reasoning > commonsense reasoning | 12 | 10 | 9 | 0.900 | 0.750 | 0.818 |
| 2 | Reasoning > comparison | 17 | 20 | 4 | 0.200 | 0.235 | 0.216 |
| 2 | Reasoning > defining symbols | 15 | 4 | 2 | 0.500 | 0.133 | 0.211 |
| 2 | Reasoning > hedge word analysis | 13 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Reasoning > logical reasoning | 38 | 189 | 16 | 0.085 | 0.421 | 0.141 |
| 2 | Reasoning > option evaluation | 45 | 108 | 33 | 0.306 | 0.733 | 0.431 |
| 2 | Reasoning > speculation | 32 | 36 | 6 | 0.167 | 0.188 | 0.176 |
| 2 | Reflection > emotion or impression | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Reflection > meta-evaluation of a step | 35 | 20 | 9 | 0.450 | 0.257 | 0.327 |
| 2 | Restatement > rephrasing an earlier sentence | 70 | 21 | 16 | 0.762 | 0.229 | 0.352 |
| 2 | Restatement > rephrasing the prompt | 53 | 33 | 26 | 0.788 | 0.491 | 0.605 |
| 3 | Assumption > assuming a missing premise by common practice > "$1.00 more" | 1 | 3 | 1 | 0.333 | 1.000 | 0.500 |
| 3 | Assumption > assuming an uncertain fact | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > branching (case split) | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > branching (case split) > algebra | 4 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Conclusion > final answer | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 3 | Conclusion > intermediate conclusion | 37 | 16 | 12 | 0.750 | 0.324 | 0.453 |
| 3 | Example > non-exhaustive listing > algebra | 17 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Example > rhetorical example | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > commonsense | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > concept or definition > well-posedness | 6 | 8 | 2 | 0.250 | 0.333 | 0.286 |
| 3 | Knowledge > self-knowledge > evaluation context | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > self-knowledge > role | 4 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > world knowledge > famous problem (CRT) | 16 | 5 | 3 | 0.600 | 0.188 | 0.286 |
| 3 | Planning > announce output | 16 | 15 | 10 | 0.667 | 0.625 | 0.645 |
| 3 | Planning > announce the conclusion | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Planning > global plan | 35 | 41 | 14 | 0.341 | 0.400 | 0.368 |
| 3 | Planning > initiate backtracking | 8 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Planning > initiate verification | 42 | 1 | 1 | 1.000 | 0.024 | 0.047 |
| 3 | Planning > local plan | 71 | 17 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > calculation > algebra | 35 | 79 | 23 | 0.291 | 0.657 | 0.404 |
| 3 | Reasoning > commonsense reasoning | 12 | 10 | 9 | 0.900 | 0.750 | 0.818 |
| 3 | Reasoning > comparison > option vs option | 8 | 9 | 1 | 0.111 | 0.125 | 0.118 |
| 3 | Reasoning > comparison > prompt vs original text | 9 | 11 | 3 | 0.273 | 0.333 | 0.300 |
| 3 | Reasoning > defining symbols > algebra | 15 | 4 | 2 | 0.500 | 0.133 | 0.211 |
| 3 | Reasoning > hedge word analysis > everyday reading | 4 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > hedge word analysis > mathematical reading | 8 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > hedge word analysis > undecided | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > logical reasoning | 20 | 16 | 2 | 0.125 | 0.100 | 0.111 |
| 3 | Reasoning > logical reasoning > algebra | 18 | 173 | 2 | 0.012 | 0.111 | 0.021 |
| 3 | Reasoning > option evaluation | 0 | 14 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > option evaluation > (A) | 11 | 4 | 3 | 0.750 | 0.273 | 0.400 |
| 3 | Reasoning > option evaluation > (B) | 0 | 4 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > option evaluation > (C) | 25 | 61 | 14 | 0.230 | 0.560 | 0.326 |
| 3 | Reasoning > option evaluation > (D) | 0 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > option evaluation > (E) | 9 | 21 | 4 | 0.190 | 0.444 | 0.267 |
| 3 | Reasoning > option evaluation > (F) | 0 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > speculation > intent of the question writer | 32 | 36 | 6 | 0.167 | 0.188 | 0.176 |
| 3 | Reflection > emotion or impression | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step | 14 | 20 | 9 | 0.450 | 0.643 | 0.529 |
| 3 | Reflection > meta-evaluation of a step > option (B) | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step > option (C) | 7 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step > option (D) | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step > option (E) | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step > option (F) | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Restatement > rephrasing an earlier sentence | 70 | 21 | 16 | 0.762 | 0.229 | 0.352 |
| 3 | Restatement > rephrasing the prompt | 0 | 14 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Restatement > rephrasing the prompt > answer-format instruction | 7 | 5 | 3 | 0.600 | 0.429 | 0.500 |
| 3 | Restatement > rephrasing the prompt > option text | 24 | 7 | 6 | 0.857 | 0.250 | 0.387 |
| 3 | Restatement > rephrasing the prompt > question text | 22 | 7 | 4 | 0.571 | 0.182 | 0.276 |

### Twenty most frequent confusion pairs at Level 1 (reviewed → judge, primary label)

| reviewed | judge | count |
|---|---|---|
| Planning | Reasoning | 89 |
| Restatement | Reasoning | 71 |
| Knowledge | Reasoning | 24 |
| Example | Reasoning | 22 |
| Reflection | Reasoning | 22 |
| Conclusion | Reasoning | 18 |
| Planning | Reflection | 8 |
| Planning | Restatement | 7 |
| Assumption | Reasoning | 6 |
| Restatement | Planning | 5 |
| Planning | Conclusion | 4 |
| Planning | Knowledge | 3 |
| Reasoning | Knowledge | 3 |
| Conclusion | Planning | 3 |
| Reasoning | Restatement | 2 |
| Reflection | Restatement | 2 |
| Reasoning | Assumption | 2 |
| Conclusion | Reflection | 2 |
| Planning | Assumption | 1 |
| Conclusion | Knowledge | 1 |

### Twenty most frequent confusion pairs at Level 2 (reviewed → judge, primary label)

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
| Example > non-exhaustive listing | Reasoning > logical reasoning | 10 |
| Planning > local plan | Reasoning > option evaluation | 9 |
| Restatement > rephrasing the prompt | Reasoning > logical reasoning | 9 |
| Conclusion > intermediate conclusion | Reasoning > logical reasoning | 9 |
| Reasoning > calculation | Reasoning > logical reasoning | 8 |
| Restatement > rephrasing an earlier sentence | Reasoning > calculation | 8 |
| Restatement > rephrasing the prompt | Reasoning > comparison | 7 |
| Reasoning > option evaluation | Reasoning > logical reasoning | 7 |
| Reasoning > logical reasoning | Reasoning > option evaluation | 7 |
| Example > non-exhaustive listing | Reasoning > calculation | 7 |

### Residue: 479 sentences whose full-path set differs (first thirty)

| trace | s | reviewed | judge | text |
|---|---|---|---|---|
| c004 | 1 | Planning > global plan | Planning > local plan | ⏎⏎1. |
| c004 | 2 | Planning > global plan | Planning > local plan | **Analyze the Request:** |
| c004 | 3 | Restatement > rephrasing the prompt > question text | Restatement > rephrasing the prompt | ⏎    *   **Problem:** "A bat and a ball cost \$1.10 in total. |
| c004 | 4 | Restatement > rephrasing the prompt > question text | Restatement > rephrasing the prompt | The bat costs more than the ball. |
| c004 | 5 | Restatement > rephrasing the prompt > question text | Restatement > rephrasing the prompt | How much does the ball cost?" |
| c004 | 6 | Restatement > rephrasing the prompt > option text | Restatement > rephrasing the prompt | ⏎    *   **Options:** (A) \$0.05, (B) Probably \$0.05, (C) Not enough info, likely \$0.05, (D) Not sure, (E) Not well posed, (F) None of the above. |
| c004 | 7 | Restatement > rephrasing the prompt > answer-format instruction | Restatement > rephrasing the prompt | ⏎    *   **Task:** Explain reasoning and provide the final answer in a specific format. |
| c004 | 8 | Planning > global plan | Planning > local plan | ⏎⏎2. |
| c004 | 10 | Reasoning > defining symbols > algebra | Restatement > rephrasing the prompt > question text | ⏎    *   *Equation 1:* Bat + Ball = 1.10 |
| c004 | 11 | Reasoning > defining symbols > algebra | Restatement > rephrasing the prompt > question text | ⏎    *   *Condition:* Bat > Ball |
| c004 | 13 | Planning > global plan | Planning > local plan | ⏎⏎3. |
| c004 | 15 | Assumption > branching (case split) > algebra | Reasoning > calculation > algebra | ⏎    *   If Ball = \$0.05, |
| c004 | 19 | Reasoning > logical reasoning > algebra | Reasoning > calculation > algebra | Yes. |
| c004 | 21 | Reasoning > logical reasoning > algebra | Reasoning > calculation > algebra | Yes. |
| c004 | 22 | Reasoning > logical reasoning > algebra | Reasoning > calculation > algebra | ⏎        *   *Result:* \$0.05 is a *possible* solution. |
| c004 | 23 | Assumption > branching (case split) > algebra | Reasoning > calculation > algebra | ⏎    *   If Ball = \$0.01, |
| c004 | 27 | Reasoning > logical reasoning > algebra | Reasoning > calculation > algebra | Yes. |
| c004 | 29 | Reasoning > logical reasoning > algebra | Reasoning > calculation > algebra | Yes. |
| c004 | 30 | Reasoning > logical reasoning > algebra | Reasoning > calculation > algebra | ⏎        *   *Result:* \$0.01 is *also* a possible solution. |
| c004 | 31 | Assumption > branching (case split) > algebra | Reasoning > calculation > algebra | ⏎    *   If Ball = \$0.55, |
| c004 | 35 | Reasoning > logical reasoning > algebra | Reasoning > calculation > algebra | ⏎        *   *Result:* \$0.55 is not a solution. |
| c004 | 36 | Planning > global plan | Planning > local plan | ⏎⏎4. |
| c004 | 37 | Planning > global plan | Knowledge > world knowledge > famous problem (CRT) | **Identify the Nature of the Question:** |
| c004 | 39 | Knowledge > world knowledge > famous problem (CRT) | Reasoning > speculation > intent of the question writer | ⏎    *   *The Trap:* Most people intuitively answer \$0.10 (Ball) and \$1.00 (Bat). |
| c004 | 40 | Reasoning > calculation > algebra | Reasoning > speculation > intent of the question writer | Why? |
| c004 | 41 | Reasoning > calculation > algebra | Reasoning > speculation > intent of the question writer | Because \$1.00 + \$0.10 = \$1.10. |
| c004 | 42 | Knowledge > world knowledge > famous problem (CRT) | Reasoning > speculation > intent of the question writer | But wait, the problem usually adds the constraint "The bat costs **\$1.00 more than the ball**." |
| c004 | 43 | Planning > initiate verification || Restatement > rephrasing the prompt > question text | Reasoning > comparison > prompt vs original text | ⏎    *   *Check the text provided in the prompt again carefully:* "A bat and a ball cost \$1.10 in total. |
| c004 | 44 | Restatement > rephrasing the prompt > question text | Reasoning > comparison > prompt vs original text | The bat costs more than the ball." |
| c004 | 47 | Reasoning > calculation > algebra | Reasoning > logical reasoning > algebra | Any price for the ball ($x$) where $0 < x < 0.55$ works. |
## pytest output

```
........................................................................ [ 82%]
...............                                                          [100%]
87 passed in 0.27s
```
