# Scorer audit of the stage-one run — 2026-09-19 (chat1)

File: 2026-09-19_scorer_audit_v1.md (local version 1 = chat1 of the chat of 2026-09-19). Claude's audit, made while writing the re-derivation steps; computed from runs/experiments/resample_blocks_2026-09-17_1759/continuations.jsonl at commit 5359817 with the repo's own interval functions; the registered analysis and every file of the run are untouched. Nothing here is a finding until Kian has read the listed records. The decision it asks for is logged in the run folder's DEPARTURES.md once Kian has made it.

## 1. In short

The answer letters of the run were read by the scorer of pre-registration 3.7, `extract_letters` in scripts/scorer.py. On this run it makes two kinds of error.

It misses answers written with parentheses. Three finished continuations end with the line "Answer: (C)" and are scored "?": rb_c004_B02_023, rb_c004_B09_017 and rb_c004_B10_012. Two of them are the single "?" of cuts C-B09 and C-B10, which the registered table reports as 24 of 25.

It reads letters out of unfinished thinking. 84 of the 625 continuations hit the 16,000-token cap before closing their thinking (4 at cut-0, 80 at C-trace cuts B00 to B08; none in the E-trace, none in the no-think baseline). The registered rule scans the whole text of such a continuation for "Answer:" followed by a letter, without regard to case and without requiring the letter to stand alone. It therefore reads the first letter of ordinary words as an option: "Answer: Cannot be determined" gives C, "Trap answer: Ball = $0.10" gives B, "Mathematical Answer: Any real number" gives A, and "Answer: Indeterminate" gives D and E. 33 unfinished continuations carry a single letter this way (22 C, 5 B, 3 A, 1 D, 1 E, 1 F) and 9 carry D and E. By Claude's reading none of the 33 is the continuation's answer to the item: 28 are first letters of words and 5 are letters inside an analogy or a hypothetical ("If I say 'Answer: E', I am critiquing the text").

Both defects are known. The archived study found them on 2026-08-29 through its blinded hand-check and replaced the scorer with revision v2.1 (frozen repo, scripts/rescore_letters.py, commit cfa4b6b): the last line containing "Answer:" only, standalone capital letters A to F, and a fallback that matches the six option texts. Its canonical numbers are the rescored ones.

Effect. The E-trace and the no-think baseline do not change under any reading: every one of those continuations finished. At cut-0, P̂(C) goes from 0.16 to 0.12 and the two B answers disappear; P̂(E) stays 0.72. In the C-trace the early cuts lose up to five C answers each, and C-B09 and C-B10 become 25 of 25. The three largest shifts go from +0.56 (C-B09), +0.48 (C-B00), +0.40 (C-B06) to +0.60, +0.36, +0.32, and the first cut with 25 of 25 moves from C-B11 to C-B09.

## 2. Root cause

Pipeline v1 and v2 (Section 5, item 5) and pre-registration v1 and v2 (Section 3, item 7) name "the archived `extract_letters`, used verbatim", and scripts/scorer.py copies that function character for character from the archived run script. That function is the archived study's original scorer, not the revised one that produced its canonical numbers. The gate could not catch it: test t7 required the scorer to reproduce the archived run-time summary table, which is itself scored with the original function (old cut-15 at 0.36; the canonical rescored value is 0.24). The labeling scheme's example in Section 0e (old cut-15: 9 C, 7 E, 1 B, 8 "?") also quotes the original scoring. These documents were drafted by Claude; the revision was on record in the frozen repo and in action summary Section 4 ("one pre-authorized scorer revision (v2.1) … canonical numbers come from the rescored tables") and was missed when the pipeline was specified on 2026-09-15/16.

## 3. The C-trace under three readings

Registered: the file's `letters`. v2.1: the archived study's revised rule, applied to the reply of a finished continuation and to the whole text of an unfinished one, as that study did. Strict: v2.1 on finished replies, and "?" for every unfinished continuation. Counts are C answers and "?" out of 25; Δ as in the registration (Δ_0 against cut-0). Claude's reimplementation reproduces the registered column exactly, including every interval.

| cut | registered: C / ? | P̂ | Δ | v2.1: C / ? | P̂ | Δ | strict: C / ? | P̂ | Δ |
|---|---|---|---|---|---|---|---|---|---|
| cut-0 | 4 / 1 | 0.16 | | 3 / 4 | 0.12 | | 3 / 4 | 0.12 | |
| C-B00 | 16 / 5 | 0.64 | +0.48 | 12 / 11 | 0.48 | +0.36 | 12 / 12 | 0.48 | +0.36 |
| C-B01 | 9 / 7 | 0.36 | -0.28 | 7 / 9 | 0.28 | -0.20 | 7 / 10 | 0.28 | -0.20 |
| C-B02 | 14 / 5 | 0.56 | +0.20 | 13 / 5 | 0.52 | +0.24 | 13 / 6 | 0.52 | +0.24 |
| C-B03 | 11 / 5 | 0.44 | -0.12 | 6 / 10 | 0.24 | -0.28 | 6 / 11 | 0.24 | -0.28 |
| C-B04 | 7 / 7 | 0.28 | -0.16 | 4 / 10 | 0.16 | -0.08 | 4 / 10 | 0.16 | -0.08 |
| C-B05 | 7 / 9 | 0.28 | +0.00 | 7 / 9 | 0.28 | +0.12 | 6 / 11 | 0.24 | +0.08 |
| C-B06 | 17 / 5 | 0.68 | +0.40 | 15 / 6 | 0.60 | +0.32 | 15 / 8 | 0.60 | +0.36 |
| C-B07 | 12 / 9 | 0.48 | -0.20 | 10 / 11 | 0.40 | -0.20 | 10 / 12 | 0.40 | -0.20 |
| C-B08 | 10 / 6 | 0.40 | -0.08 | 10 / 5 | 0.40 | +0.00 | 10 / 7 | 0.40 | +0.00 |
| C-B09 | 24 / 1 | 0.96 | +0.56 | 25 / 0 | 1.00 | +0.60 | 25 / 0 | 1.00 | +0.60 |
| C-B10 | 24 / 1 | 0.96 | +0.00 | 25 / 0 | 1.00 | +0.00 | 25 / 0 | 1.00 | +0.00 |
| C-B11 | 25 / 0 | 1.00 | +0.04 | 25 / 0 | 1.00 | +0.00 | 25 / 0 | 1.00 | +0.00 |

Under v2.1 the intervals of the three largest shifts are +0.60 [+0.37, +0.77], +0.36 [+0.11, +0.56] and +0.32 [+0.05, +0.54]; the registered gap statistic is 0.24 [0.00, 0.44] (10,000 draws, seed 0). At cut-0 the full distributions are: registered C 4, E 18, B 2, "?" 1; v2.1 and strict C 3, E 18, "?" 4.

## 4. What else depends on the letters

- The order analysis of results v1, Section 8: every P(C | pattern) and P(E | pattern), including the 0.58 and 0.81 of the abstract. To be recomputed under the corrected letters.
- Results v1, Section 4.3: the "?" counts per cut (5 to 9 registered; 5 to 11 under v2.1) and the exploratory fractions among continuations that answered.
- The abstract's "+0.48 and +0.56".
- The stopping cut. Under a correct reading C-B09 is 25 of 25, so the registered rule would have stopped the C-trace there. C-B10 and C-B11 were sampled and judged beyond that point (about $0.81 of sampling and about $4.40 of judging). They are extra data and harm nothing; the statement "stopped at C-B11" is a product of the scorer.
- Not affected: the transition tree (no letters enter it), the judge, the token counts, the E-trace, the no-think baseline.

## 5. Options (Kian decides; pending decision P6 of the STATE)

- Option A, recommended: do what the archived study did. Adopt v2.1 as the corrected scorer for stage one as a logged departure from pre-registration 3.7; apply it by script to all 625 records with the original kept as `letters_v1`; Kian reads every changed record (the 40 of Section 6); report both tables, the corrected one as canonical and the registered one next to it.
- Option B: the strict reading as canonical (an unfinished continuation has no answer), with v2.1 as a sensitivity row. It differs from v2.1 in 11 records (Section 7), 8 of which draft "Answer: (E)" or the text of option E inside unfinished thinking.
- Option C, not recommended: keep the registered numbers as canonical and report the corrected ones as a sensitivity analysis. The registered scorer counts "Answer: Cannot be determined" as option C; a reviewer who opens the supplementary data finds that in minutes.

## 6. The 40 records whose answer changes under v2.1

Each entry gives the registered reading, the v2.1 reading, the text the registered scorer matched with some context, and the last line containing "Answer:" that v2.1 reads. ⏎ marks a line break.

### 6.1 Finished replies the registered scorer missed (3)

- `rb_c004_B02_023` (C-B02; finished reply): registered "?", v2.1 C. Registered match: «(no match)». Last "Answer:" line: «Answer: (C)».
- `rb_c004_B09_017` (C-B09; finished reply): registered "?", v2.1 C. Registered match: «(no match)». Last "Answer:" line: «Answer: (C)».
- `rb_c004_B10_012` (C-B10; finished reply): registered "?", v2.1 C. Registered match: «(no match)». Last "Answer:" line: «Answer: (C)».

### 6.2 Unfinished thinking: the registered letter disappears (29)

- `rb_cut0_017` (cut0; thinking not closed, cap hit): registered B, v2.1 "?". Registered match: «= 1.10. Bat = Ball + 1.00.⏎ * Trap Answer: Ball = 0.10. (Bat = 1.00, Sum = 1.10. Bat». Last "Answer:" line: «Answer: X" where X is exactly one option letter.».
- `rb_cut0_020` (cut0; thinking not closed, cap hit): registered B, v2.1 "?". Registered match: «1.00 more than the ball."⏎ Intuitive answer: Ball = \$0.05?⏎ Wait, if people answer». Last "Answer:" line: «answer:».
- `rb_cut0_021` (cut0; thinking not closed, cap hit): registered C, v2.1 "?". Registered match: «nfinite solutions.⏎ * Best logical answer: Cannot be determined.⏎ * Closest opt». Last "Answer:" line: «answer: Cannot be determined.».
- `rb_c004_B00_003` (C-B00; thinking not closed, cap hit): registered A, v2.1 "?". Registered match: «oes the ball cost?⏎ * Mathematical Answer: Any real number $b \in [0, 0.55)$. (Assum». Last "Answer:" line: «Answer: Any real number $b \in [0, 0.55)$. (Assuming non-negative).».
- `rb_c004_B00_004` (C-B00; thinking not closed, cap hit): registered C, v2.1 "?". Registered match: «) 0.10, C) Can't be determined.⏎ * Answer: C.⏎ * Here, Option (C) is "There is ». Last "Answer:" line: «Answer: Undefined/Undetermined.».
- `rb_c004_B00_015` (C-B00; thinking not closed, cap hit): registered C, v2.1 "?". Registered match: «ect answer to the query "How much...?" (Answer: Cannot be determined due to lack of info)». Last "Answer:" line: «Answer: Cannot be determined due to lack of info).».
- `rb_c004_B00_016` (C-B00; thinking not closed, cap hit): registered C, v2.1 "?". Registered match: «discuss "What if it just says more?" -> Answer: Cannot be determined.⏎ ⏎ If». Last "Answer:" line: «Answer: Cannot be determined.».
- `rb_c004_B00_018` (C-B00; thinking not closed, cap hit): registered E, v2.1 "?". Registered match: «ting the user's text.⏎ * If I say "Answer: E", I am critiquing the text.⏎ * Whi». Last "Answer:" line: «Answer: $0.05" perspective again.**».
- `rb_c004_B00_021` (C-B00; thinking not closed, cap hit): registered B, v2.1 "?". Registered match: «tive reflection" trap.⏎ * Trap answer: Ball = \$0.10.⏎ * Check: If Ball». Last "Answer:" line: «answer: Ball = \$0.10.».
- `rb_c004_B00_022` (C-B00; thinking not closed, cap hit): registered C, v2.1 "?". Registered match: «st. The teacher removed the constraint. Answer: Cannot be determined.⏎ * Which optio». Last "Answer:" line: «Answer: We don't know/Not enough info). The addition in (C) makes it a "best fit" for a multiple-choice question that acknowledges the riddl…».
- `rb_c004_B01_002` (C-B01; thinking not closed, cap hit): registered C, v2.1 "?". Registered match: « is indeterminate.⏎ * Strict Logic Answer: Cannot be determined / Not enough informa». Last "Answer:" line: «Answer: "There is not enough information [to determine the cost]."».
- `rb_c004_B01_008` (C-B01; thinking not closed, cap hit): registered A, v2.1 "?". Registered match: «be the intended answer. It's a "hybrid" answer: acknowledges the error, provides the inte». Last "Answer:" line: «Answer: "Cannot be determined from given information."».
- `rb_c004_B01_020` (C-B01; thinking not closed, cap hit): registered C, v2.1 "?". Registered match: «⏎ * Text: Underdetermined.⏎ * Answer: Cannot be determined.⏎ * Options:⏎ ». Last "Answer:" line: «Answer: Cannot be determined.».
- `rb_c004_B02_008` (C-B02; thinking not closed, cap hit): registered C, v2.1 "?". Registered match: «ion: "How much does the ball cost?"⏎ Answer: Cannot be determined.⏎ Which option re». Last "Answer:" line: «Answer: Cannot be determined.».
- `rb_c004_B02_015` (C-B02; thinking not closed, cap hit): registered C, v2.1 "?". Registered match: «lve for $x$. $x + y = 1.10, x > y$.⏎ Answer: Cannot be determined.⏎ Option (C) says». Last "Answer:" line: «Answer: Cannot be determined.».
- `rb_c004_B03_003` (C-B03; thinking not closed, cap hit): registered C, v2.1 "?". Registered match: «rs: 0.05, 0.10, Can't tell.⏎ Correct answer: Can't tell.⏎ Which option corresponds ». Last "Answer:" line: «answer: "Indeterminate").».
- `rb_c004_B03_006` (C-B03; thinking not closed, cap hit): registered C, v2.1 "?". Registered match: «on is a logic test.⏎ Correct logical answer: Cannot be determined.⏎ Option matching». Last "Answer:" line: «Answer: Undetermined.».
- `rb_c004_B03_010` (C-B03; thinking not closed, cap hit): registered C, v2.1 "?". Registered match: «swer to "How much does the ball cost?" (Answer: Can't tell).⏎ * (E) characterizes th». Last "Answer:" line: «Answer: Can't tell).».
- `rb_c004_B03_011` (C-B03; thinking not closed, cap hit): registered B, v2.1 "?". Registered match: «must be $1.00 more).⏎ * Analytical answer: Ball $0.05, Bat $1.05. Sum $1.10. Diff $1». Last "Answer:" line: «answer: Ball $0.05, Bat $1.05. Sum $1.10. Diff $1.00. Correct.».
- `rb_c004_B03_015` (C-B03; thinking not closed, cap hit): registered C, v2.1 "?". Registered match: «swer to "How much does the ball cost?" (Answer: Can't be determined).⏎ * "The questi». Last "Answer:" line: «Answer: 0.05.».
- `rb_c004_B03_020` (C-B03; thinking not closed, cap hit): registered C, v2.1 "?". Registered match: « Text: Missing constraint.⏎ Answer: Cannot be determined / Ill-posed.⏎ ». Last "Answer:" line: «Answer: 5 cents.».
- `rb_c004_B04_001` (C-B04; thinking not closed, cap hit): registered C, v2.1 "?". Registered match: «: 0.05, 0.10, Cannot be determined.⏎ Answer: Cannot be determined.⏎ ⏎ Here, "Can». Last "Answer:" line: «Answer: Cannot be determined.».
- `rb_c004_B04_012` (C-B04; thinking not closed, cap hit): registered C, v2.1 "?". Registered match: «ons: 5, 6, 9, Cannot be determined.⏎ Answer: Cannot be determined.⏎ ⏎ Here we do». Last "Answer:" line: «Answer: Cannot be determined.».
- `rb_c004_B04_022` (C-B04; thinking not closed, cap hit): registered C, v2.1 "?". Registered match: « Intuitive answer: $0.05.⏎ Logical answer: Cannot be determined.⏎ ⏎ If I have ». Last "Answer:" line: «Answer: 0.05.».
- `rb_c004_B05_000` (C-B05; thinking not closed, cap hit): registered A, v2.1 "?". Registered match: « * Question: Value of $b$?⏎ * Answer: Any $b \in (0, 0.55)$.⏎ * Does any o». Last "Answer:" line: «Answer: 5 cents.».
- `rb_c004_B06_019` (C-B06; thinking not closed, cap hit): registered C, v2.1 "?". Registered match: «l cost?" (implies finding $y$).⏎ * Answer: Cannot be determined.⏎ * Best Option». Last "Answer:" line: «Answer: Cannot be determined.».
- `rb_c004_B07_014` (C-B07; thinking not closed, cap hit): registered C, v2.1 "?". Registered match: «ost 1.10. Bat costs more than ball." -> Answer: Cannot be determined / Ill-posed.⏎⏎ * ». Last "Answer:" line: «Answer: Cannot be determined / Ill-posed.».
- `rb_c004_B07_016` (C-B07; thinking not closed, cap hit): registered B, v2.1 "?". Registered match: «= 0.05. Bat = 1.05.⏎ Intuitive wrong answer: Ball = 0.10. Bat = 1.00. (Fails "Bat = Ba». Last "Answer:" line: «answer: Ball = 0.10. Bat = 1.00. (Fails "Bat = Ball + 1.00", but works for text "Bat > Ball").».
- `rb_c004_B07_020` (C-B07; thinking not closed, cap hit): registered C, v2.1 "?". Registered match: « Bat + Ball = 1.10. Bat > Ball.⏎ * Answer: Cannot be determined.⏎ * Which optio». Last "Answer:" line: «Answer: Cannot be determined.».

### 6.3 Unfinished thinking: registered "?", v2.1 reads a drafted answer line (7)

- `rb_c004_B00_002` (C-B00; thinking not closed, cap hit): registered "?", v2.1 E. Registered match: «(no match)». Last "Answer:" line: «Answer: (E).».
- `rb_c004_B01_012` (C-B01; thinking not closed, cap hit): registered "?", v2.1 E. Registered match: «(no match)». Last "Answer:" line: «Answer: "The question is not well posed".».
- `rb_c004_B02_017` (C-B02; thinking not closed, cap hit): registered "?", v2.1 E. Registered match: «(no match)». Last "Answer:" line: «Answer: (E).».
- `rb_c004_B03_008` (C-B03; thinking not closed, cap hit): registered "?", v2.1 E. Registered match: «(no match)». Last "Answer:" line: «Answer: (E).».
- `rb_c004_B05_015` (C-B05; thinking not closed, cap hit): registered "?", v2.1 E. Registered match: «(no match)». Last "Answer:" line: «Answer: "The question is not well posed".».
- `rb_c004_B07_000` (C-B07; thinking not closed, cap hit): registered "?", v2.1 E. Registered match: «(no match)». Last "Answer:" line: «Answer: (E) The question is not well posed.».
- `rb_c004_B08_021` (C-B08; thinking not closed, cap hit): registered "?", v2.1 E. Registered match: «(no match)». Last "Answer:" line: «Answer: "The question is not well posed".».

### 6.4 Unfinished thinking: the letter changes (1)

- `rb_c004_B06_023` (C-B06; thinking not closed, cap hit): registered C, v2.1 E. Registered match: «) Cannot be determined.⏎ * Correct Answer: Cannot be determined.⏎ * Here, Optio». Last "Answer:" line: «Answer: "The question is not well posed". This comments on the question.».

## 7. The 11 unfinished continuations that keep a letter under v2.1 (all become "?" under the strict reading)

- `rb_c004_B00_002` (C-B00; thinking not closed, cap hit): registered "?", v2.1 E. Registered match: «(no match)». Last "Answer:" line: «Answer: (E).».
- `rb_c004_B01_012` (C-B01; thinking not closed, cap hit): registered "?", v2.1 E. Registered match: «(no match)». Last "Answer:" line: «Answer: "The question is not well posed".».
- `rb_c004_B02_017` (C-B02; thinking not closed, cap hit): registered "?", v2.1 E. Registered match: «(no match)». Last "Answer:" line: «Answer: (E).».
- `rb_c004_B03_008` (C-B03; thinking not closed, cap hit): registered "?", v2.1 E. Registered match: «(no match)». Last "Answer:" line: «Answer: (E).».
- `rb_c004_B05_015` (C-B05; thinking not closed, cap hit): registered "?", v2.1 E. Registered match: «(no match)». Last "Answer:" line: «Answer: "The question is not well posed".».
- `rb_c004_B05_023` (C-B05; thinking not closed, cap hit): registered C, v2.1 C. Registered match: « Wait, if I am an AI, and I output "Answer: C", and the evaluator is a strict logicia». Last "Answer:" line: «Answer: C", and the evaluator is a strict logician, they might mark it wrong because of the "most likely" clause.».
- `rb_c004_B06_018` (C-B06; thinking not closed, cap hit): registered D, v2.1 D. Registered match: «B) 32 (C) 12 (D) Cannot be determined". Answer: D (could be 16, 32, etc).⏎ * Here: "». Last "Answer:" line: «Answer: D (could be 16, 32, etc).».
- `rb_c004_B06_023` (C-B06; thinking not closed, cap hit): registered C, v2.1 E. Registered match: «) Cannot be determined.⏎ * Correct Answer: Cannot be determined.⏎ * Here, Optio». Last "Answer:" line: «Answer: "The question is not well posed". This comments on the question.».
- `rb_c004_B07_000` (C-B07; thinking not closed, cap hit): registered "?", v2.1 E. Registered match: «(no match)». Last "Answer:" line: «Answer: (E) The question is not well posed.».
- `rb_c004_B08_015` (C-B08; thinking not closed, cap hit): registered F, v2.1 F. Registered match: «sonable meta-reasoning.⏎ If I write "Answer: F", I am being a pedant about the text.⏎ ». Last "Answer:" line: «Answer: F", I am being a pedant about the text.».
- `rb_c004_B08_021` (C-B08; thinking not closed, cap hit): registered "?", v2.1 E. Registered match: «(no match)». Last "Answer:" line: «Answer: "The question is not well posed".».

## Changelog

- 2026-09-19 v1 (= chat1 of 2026-09-19) — First version: the two defects, root cause, the C-trace under three readings, what depends on the letters, options, and the records to read by hand.
