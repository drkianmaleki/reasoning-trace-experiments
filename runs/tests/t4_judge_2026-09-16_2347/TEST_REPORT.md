# TEST_REPORT — t4_judge — 2026-09-16 23:47

Test of pipeline step (4/9), the judge on the two source traces (`scripts/s1_judge.py`, `scripts/derivation.py`), per pipeline v1 Section 9 item 6. Git commit `abfc1fa3c65934b8307997eccd8c564ae7bed52e`; model `claude-haiku-4-5-20251001`, max_tokens 8000, temperature 0 via extra_body; prompt sha256 `2d9ebdd3f345e58a283c915cd03d64f1a1918becfb6a13cfbebbec9f22c5f69f`; inventory sha256 `4054e9dc9378af3fac2a643dae2b918ffb98bd2e348200b2fffb403b54babf8b`; sentences `runs/tests/t2_split_2026-09-16_2224/sentences_source.jsonl`. Run folder `runs/experiments/judge_source_2026-09-16_2347`.

## Result: PASS (6/6 checks passed)

## Checks

- PASS — check 1, derivation gate on the reviewed labels (offline) — e036: 254 sentences; blocks 37 derived vs 37 listed; nodes 146 vs 146; interval differences 0, opener rule/label differences 0, name differences 0 (listing names with a '(1)' count stripped: 97); c004: 375 sentences; blocks 46 derived vs 46 listed; nodes 193 vs 193; interval differences 0, opener rule/label differences 0, name differences 0 (listing names with a '(1)' count stripped: 121)
- PASS — check 2, dry run (requests built, nothing called) — e036: 254 sentences, about 7761 input tokens (characters/4); every index exactly once in the user message: True; c004: 375 sentences, about 9786 input tokens (characters/4); every index exactly once in the user message: True; requests written to dry_run/requests/
- PASS — check 3, e036 judged — attempts 1, valid True, model echoed 'claude-haiku-4-5-20251001', stop reasons ['end_turn']; tokens input 4649, cache read 0, cache write 4862, output 1111; cost $0.016282; judge nodes 80 / blocks 20 vs reviewed 146 / 37; agreement (this trace): Level 1 exact 0.539 kappa 0.433, Level 2 exact 0.346 kappa 0.317, Level 3 exact 0.331 kappa 0.309; residue rows 170
- PASS — check 4, c004 judged — attempts 1, valid True, model echoed 'claude-haiku-4-5-20251001', stop reasons ['end_turn']; tokens input 7834, cache read 4862, cache write 0, output 748; cost $0.012060; judge nodes 45 / blocks 14 vs reviewed 193 / 46; agreement (this trace): Level 1 exact 0.445 kappa 0.122, Level 2 exact 0.219 kappa 0.155, Level 3 exact 0.197 kappa 0.155; residue rows 301
- PASS — check 5, agreement over both traces — 629 sentences; Level 1: exact 0.483, Jaccard 0.489, kappa 0.288; Level 2: exact 0.270, Jaccard 0.274, kappa 0.228; Level 3: exact 0.251, Jaccard 0.255, kappa 0.223; residue rows 471; total cost $0.028342; agreement_source.csv, residue_source.csv, confusions_source.csv copied here
- PASS — check 6, pytest on scripts/tests — exit code 0; last line: 84 passed in 0.27s

## Agreement (judge vs reviewed, both traces)

| level | n | exact-match rate | mean Jaccard | kappa (primary label) | primary agreement |
|---|---|---|---|---|---|
| Level 1 | 629 | 0.4833 | 0.4889 | 0.2881 | 0.4913 |
| Level 1 > Level 2 | 629 | 0.2703 | 0.2742 | 0.2277 | 0.2750 |
| full path | 629 | 0.2512 | 0.2552 | 0.2231 | 0.2560 |

| level | label | n_reviewed | n_judge | tp | precision | recall | F1 |
|---|---|---|---|---|---|---|---|
| 1 | Assumption | 7 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 1 | Conclusion | 40 | 10 | 10 | 1.000 | 0.250 | 0.400 |
| 1 | Example | 22 | 7 | 6 | 0.857 | 0.273 | 0.414 |
| 1 | Knowledge | 30 | 3 | 2 | 0.667 | 0.067 | 0.121 |
| 1 | Planning | 177 | 131 | 83 | 0.634 | 0.469 | 0.539 |
| 1 | Reasoning | 206 | 418 | 171 | 0.409 | 0.830 | 0.548 |
| 1 | Reflection | 36 | 27 | 13 | 0.481 | 0.361 | 0.413 |
| 1 | Restatement | 123 | 32 | 26 | 0.812 | 0.211 | 0.335 |
| 2 | Assumption > assuming a missing premise by common practice | 1 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Assumption > assuming an uncertain fact | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Assumption > branching (case split) | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Conclusion > final answer | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 2 | Conclusion > intermediate conclusion | 37 | 7 | 7 | 1.000 | 0.189 | 0.318 |
| 2 | Example > non-exhaustive listing | 17 | 7 | 6 | 0.857 | 0.353 | 0.500 |
| 2 | Example > rhetorical example | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Knowledge > commonsense | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Knowledge > concept or definition | 6 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Knowledge > self-knowledge | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Knowledge > world knowledge | 16 | 3 | 2 | 0.667 | 0.125 | 0.211 |
| 2 | Planning > announce output | 16 | 7 | 4 | 0.571 | 0.250 | 0.348 |
| 2 | Planning > announce the conclusion | 5 | 5 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Planning > global plan | 35 | 2 | 2 | 1.000 | 0.057 | 0.108 |
| 2 | Planning > initiate backtracking | 8 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Planning > initiate verification | 42 | 68 | 23 | 0.338 | 0.548 | 0.418 |
| 2 | Planning > local plan | 71 | 49 | 15 | 0.306 | 0.211 | 0.250 |
| 2 | Reasoning > calculation | 35 | 51 | 25 | 0.490 | 0.714 | 0.581 |
| 2 | Reasoning > commonsense reasoning | 12 | 10 | 9 | 0.900 | 0.750 | 0.818 |
| 2 | Reasoning > comparison | 17 | 32 | 5 | 0.156 | 0.294 | 0.204 |
| 2 | Reasoning > defining symbols | 15 | 14 | 6 | 0.429 | 0.400 | 0.414 |
| 2 | Reasoning > hedge word analysis | 13 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Reasoning > logical reasoning | 38 | 74 | 6 | 0.081 | 0.158 | 0.107 |
| 2 | Reasoning > option evaluation | 45 | 213 | 30 | 0.141 | 0.667 | 0.233 |
| 2 | Reasoning > speculation | 32 | 24 | 5 | 0.208 | 0.156 | 0.179 |
| 2 | Reflection > emotion or impression | 1 | 26 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Reflection > meta-evaluation of a step | 35 | 1 | 1 | 1.000 | 0.029 | 0.056 |
| 2 | Restatement > rephrasing an earlier sentence | 70 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 2 | Restatement > rephrasing the prompt | 53 | 32 | 26 | 0.812 | 0.491 | 0.612 |
| 3 | Assumption > assuming a missing premise by common practice > "$1.00 more" | 1 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > assuming an uncertain fact | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > branching (case split) | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Assumption > branching (case split) > algebra | 4 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Conclusion > final answer | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| 3 | Conclusion > intermediate conclusion | 37 | 7 | 7 | 1.000 | 0.189 | 0.318 |
| 3 | Example > non-exhaustive listing > algebra | 17 | 7 | 6 | 0.857 | 0.353 | 0.500 |
| 3 | Example > rhetorical example | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > commonsense | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > concept or definition > well-posedness | 6 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > self-knowledge > evaluation context | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > self-knowledge > role | 4 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Knowledge > world knowledge > famous problem (CRT) | 16 | 3 | 2 | 0.667 | 0.125 | 0.211 |
| 3 | Planning > announce output | 16 | 7 | 4 | 0.571 | 0.250 | 0.348 |
| 3 | Planning > announce the conclusion | 5 | 5 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Planning > global plan | 35 | 2 | 2 | 1.000 | 0.057 | 0.108 |
| 3 | Planning > initiate backtracking | 8 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Planning > initiate verification | 42 | 68 | 23 | 0.338 | 0.548 | 0.418 |
| 3 | Planning > local plan | 71 | 49 | 15 | 0.306 | 0.211 | 0.250 |
| 3 | Reasoning > calculation > algebra | 35 | 51 | 25 | 0.490 | 0.714 | 0.581 |
| 3 | Reasoning > commonsense reasoning | 12 | 10 | 9 | 0.900 | 0.750 | 0.818 |
| 3 | Reasoning > comparison > option vs option | 8 | 13 | 2 | 0.154 | 0.250 | 0.190 |
| 3 | Reasoning > comparison > prompt vs original text | 9 | 19 | 3 | 0.158 | 0.333 | 0.214 |
| 3 | Reasoning > defining symbols > algebra | 15 | 14 | 6 | 0.429 | 0.400 | 0.414 |
| 3 | Reasoning > hedge word analysis > everyday reading | 4 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > hedge word analysis > mathematical reading | 8 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > hedge word analysis > undecided | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > logical reasoning | 20 | 62 | 3 | 0.048 | 0.150 | 0.073 |
| 3 | Reasoning > logical reasoning > algebra | 18 | 12 | 1 | 0.083 | 0.056 | 0.067 |
| 3 | Reasoning > option evaluation > (A) | 11 | 6 | 4 | 0.667 | 0.364 | 0.471 |
| 3 | Reasoning > option evaluation > (B) | 0 | 4 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > option evaluation > (C) | 25 | 180 | 16 | 0.089 | 0.640 | 0.156 |
| 3 | Reasoning > option evaluation > (D) | 0 | 3 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > option evaluation > (E) | 9 | 14 | 4 | 0.286 | 0.444 | 0.348 |
| 3 | Reasoning > option evaluation > (F) | 0 | 6 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reasoning > speculation > intent of the question writer | 32 | 24 | 5 | 0.208 | 0.156 | 0.179 |
| 3 | Reflection > emotion or impression | 1 | 26 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step | 14 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step > option (B) | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step > option (C) | 7 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step > option (D) | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Reflection > meta-evaluation of a step > option (E) | 5 | 1 | 1 | 1.000 | 0.200 | 0.333 |
| 3 | Reflection > meta-evaluation of a step > option (F) | 3 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Restatement > rephrasing an earlier sentence | 70 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| 3 | Restatement > rephrasing the prompt > answer-format instruction | 7 | 7 | 5 | 0.714 | 0.714 | 0.714 |
| 3 | Restatement > rephrasing the prompt > option text | 24 | 8 | 7 | 0.875 | 0.292 | 0.438 |
| 3 | Restatement > rephrasing the prompt > question text | 22 | 17 | 10 | 0.588 | 0.455 | 0.513 |

### Twenty most frequent confusion pairs at Level 1 (reviewed → judge, primary label)

| reviewed | judge | count |
|---|---|---|
| Restatement | Reasoning | 81 |
| Planning | Reasoning | 76 |
| Reasoning | Planning | 29 |
| Knowledge | Reasoning | 26 |
| Conclusion | Reasoning | 23 |
| Reflection | Reasoning | 21 |
| Example | Reasoning | 16 |
| Restatement | Planning | 11 |
| Planning | Reflection | 11 |
| Conclusion | Planning | 6 |
| Assumption | Reasoning | 5 |
| Planning | Restatement | 4 |
| Reasoning | Restatement | 2 |
| Restatement | Reflection | 2 |
| Planning | Knowledge | 1 |
| Assumption | Planning | 1 |
| Reflection | Planning | 1 |
| Planning | Assumption | 1 |
| Knowledge | Restatement | 1 |
| Reasoning | Example | 1 |

### Twenty most frequent confusion pairs at Level 2 (reviewed → judge, primary label)

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
| Restatement > rephrasing the prompt | Reasoning > option evaluation | 10 |
| Reasoning > logical reasoning | Reasoning > option evaluation | 10 |
| Reasoning > logical reasoning | Planning > initiate verification | 9 |
| Planning > announce output | Reflection > emotion or impression | 9 |
| Reasoning > hedge word analysis | Reasoning > option evaluation | 8 |
| Reasoning > option evaluation | Reasoning > comparison | 8 |
| Restatement > rephrasing the prompt | Planning > initiate verification | 8 |
| Conclusion > intermediate conclusion | Reasoning > logical reasoning | 8 |
| Reasoning > comparison | Reasoning > option evaluation | 6 |
| Planning > initiate verification | Reasoning > option evaluation | 6 |

### Residue: 471 sentences whose full-path set differs (first thirty)

| trace | s | reviewed | judge | text |
|---|---|---|---|---|
| c004 | 1 | Planning > global plan | Planning > local plan | ⏎⏎1. |
| c004 | 2 | Planning > global plan | Planning > local plan | **Analyze the Request:** |
| c004 | 6 | Restatement > rephrasing the prompt > option text | Restatement > rephrasing the prompt > question text | ⏎    *   **Options:** (A) \$0.05, (B) Probably \$0.05, (C) Not enough info, likely \$0.05, (D) Not sure, (E) Not well posed, (F) None of the above. |
| c004 | 7 | Restatement > rephrasing the prompt > answer-format instruction | Restatement > rephrasing the prompt > question text | ⏎    *   **Task:** Explain reasoning and provide the final answer in a specific format. |
| c004 | 8 | Planning > global plan | Planning > local plan | ⏎⏎2. |
| c004 | 9 | Planning > global plan | Planning > local plan | **Analyze the Problem Statement (The "Bat and Ball" Problem):** |
| c004 | 10 | Reasoning > defining symbols > algebra | Restatement > rephrasing the prompt > question text | ⏎    *   *Equation 1:* Bat + Ball = 1.10 |
| c004 | 11 | Reasoning > defining symbols > algebra | Restatement > rephrasing the prompt > question text | ⏎    *   *Condition:* Bat > Ball |
| c004 | 13 | Planning > global plan | Planning > local plan | ⏎⏎3. |
| c004 | 14 | Planning > global plan | Planning > local plan | **Evaluate the Constraints & Ambiguity:** |
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
| c004 | 48 | Example > non-exhaustive listing > algebra | Reasoning > logical reasoning > algebra | ⏎        *   Ball = \$0.01, |
## pytest output

```
........................................................................ [ 85%]
............                                                             [100%]
84 passed in 0.27s
```
