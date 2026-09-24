# Stage one — what the block-boundary resampling run found — reasoning-trace-experiments — 2026-09-19 v2

File: 2026-09-19_stage1_results_v2.md (local version 2 = chat version 3 of the chat of 2026-09-19). Supersedes 2026-09-18_stage1_results_v1.md (→ archive/docs/shared/). Claude drafted; Kian confirmed on 2026-09-19 and owns every decision recorded here.

What changed since v1, in one paragraph. The scorer named in the pre-registration misread 36 of the 625 continuations, and the strict reading adopted on 2026-09-19 (decision P6) is now canonical: a continuation has an answer only if it finished, and the answer is the letter on the last line of its reply. Every mediation number in Sections 3 to 5 is therefore new; the transition results of Section 6 are unchanged, because no answer letter enters them. Three errata of v1 are corrected in place (Sections 4.2, 6.1, 6.2). Section 8, the order of kinds of thought, is rebuilt on a different measurement and its former numbers are withdrawn, not adjusted. Section 9 is new: what the labeling scheme could not measure, and what that implies for the instrument. The re-derivation asked for by pre-registration 7.2 is done and is recorded in Section 12.

Where the numbers come from. The mediation and transition tables of `runs/experiments/resample_blocks_2026-09-17_1759_strict/`, produced by `scripts/s5_rescore.py` and then by the registered analysis `scripts/s4_analyze.py` unchanged; the order analysis of Section 8 from the 69 prefix-free traces, computed from their text and their labels. The registered run folder is untouched and its tables are quoted wherever the two differ. The pre-registration's wording rule applies throughout: the numbers are described, not judged.

This document is written for a reader who has not seen the project's notation. Every term is explained where it first appears. The exact definitions live in the labeling scheme (`docs/shared/2026-09-17_labeling_scheme_v6.md`), the design in `2026-09-17_preregistration_stage1_v2.md`, and the scoring decision in the run folder's `DEPARTURES.md` and `docs/shared/2026-09-19_scorer_audit_v1.md`.

## 1. The question, in plain words

When a reasoning model thinks out loud before it answers, its written thoughts are a long text. We want to know how the answer the model goes on to give changes as more of that text is fixed, and whether what the model does next depends on more than the kind of thought it is currently having.

The model is Qwen 3.6-27B. The item is the bat-and-ball riddle with one clause deleted: "A bat and a ball cost $1.10 in total. The bat costs more than the ball. How much does the ball cost?" followed by six options — (A) it is $0.05; (B) it is probably $0.05; (C) there is not enough information, but the answer is most likely $0.05; (D) I am not sure; (E) the question is not well posed; (F) none of the above. The classic riddle says the bat costs $1.00 more than the ball, which fixes the answer at $0.05; without that clause any ball price below $0.55 works, so the "right" answer is a matter of reading: E says the question is broken, C says it is underdetermined but $0.05 is the intended answer, A says $0.05 flatly.

We studied two of the model's own thinking texts, called traces: the C-trace, which ends at C, and the E-trace, which ends at E. Each was cut into sentences (375 and 254) and every sentence was labeled with the kind of move it makes — Planning ("Let's check the options"), Reasoning ("then Bat = 1.10 − 0.55 = $0.55"), Restatement (repeating the question), Knowledge ("this is the classic cognitive reflection test question"), Assumption ("If Ball = $0.05,"), Reflection ("That checks out"), Example, Conclusion. Consecutive sentences with the same label form a node; the text is grouped further into blocks, stretches that begin where the model announces a new phase, opens a new case, or says "Wait". The C-trace has 47 blocks, the E-trace 38. The labels were produced by an LLM assistant and reviewed by the author; the blocks follow from the labels by fixed rules.

The experiment is resampling. Take the trace up to the end of a block — that prefix is a cut — feed it back to the model as its own unfinished thinking, and let it finish 25 times. Each finished text is a continuation. Two quantities are measured at every cut. The first is how often the continuations complete with the trace's own answer, written P(final answer | cut(B_m)) and estimated by P̂_m, the fraction of the 25. Stated exactly, it is the probability that a continuation of that prefix finishes within 16,000 generated tokens and gives that answer; it is a statement about what the model outputs from a given prefix, not about an internal state, and a continuation that does not finish counts against it (Section 3.1). The second is what kind of move comes first after the cut, written P(next = Y | cut(B_m)). Section 8 uses a third form, P(final answer | ⟨ X --> Y ⟩): the fraction of texts in which a thing of kind X occurs before a thing of kind Y, and which end at the given answer. The angle brackets name a pattern in the text; the arrow reads "and later".

Two reference conditions sit below the first block. The no-think baseline: the model answers with no thinking text at all (100 samples). Cut-0: the model thinks from an empty prefix (25 samples).

## 2. The short version

**Reasoning changes the answer.** Without thinking, the model answered C 49 times in 100, A 32, E 19. Thinking first, it answered E 18 times in 25 and C 3 times. Writing out its reasoning moves the model's most frequent answer from C, "not enough information, but most likely $0.05", to E, "the question is not well posed".

**The largest change in the answer distribution occurs across one block: the passage where the model evaluates the options one at a time and weighs the hedge words inside them.** In the C-trace the completed-C frequency starts at 0.12 and reaches 1.00. The largest observed shift, +0.60, occurs across block 9, where the model takes the six options in turn against the text of the question and, at its centre, reads the words "probably" and "most likely" that options (B) and (C) hang on. A second shift of +0.36 occurs across the opening block. Both survive the most adverse assumption about the continuations that never finished; a third shift of +0.36, across the block that recognizes the riddle, does not. Each large rise is flanked by blocks that do not rise, so each is captured whole inside one block. The E-trace starts high, at 0.72, dips to 0.56 when it writes the classic constraint into its own algebra, recovers when it notices the deletion, and ends at 1.00.

**The kind of the last move does not determine what comes next.** If the next kind of move depended only on the Level 1 kind of the last one, all cuts ending on the same kind would show the same distribution of next moves. They do not. The registered test rejects that last-type-only reading (C-trace p ≤ 0.0001 on 10,000 permutations; E-trace p = 0.0033). The sharpest instance needs no coarse labels at all: three C-trace cuts end on a sentence with the identical full label path, the "Result:" line of three successive cases, and the continuations open a new case in 13 of 24, 24 of 25 and 11 of 25. What differs between those cuts is how far the enumeration has gone. This rejects one specific state description, the last Level 1 label; it does not show that no richer state would do.

**The order in which the model brings in what it knows is associated with the answer (exploratory).** In 69 traces written with no prefix at all, P(C | ⟨ algebra --> constraint imported ⟩) = 0.31 against P(C | ⟨ constraint imported --> algebra ⟩) = 0.04, a difference of +0.27 [0.08, 0.52]. C is rare in both orders and about eight times as frequent when the algebra comes first; most algebra-first traces still end at E. The model chose both the order and the answer, so this is an association, not evidence that changing the order would change the answer.

Sections 3 to 7 give the details; Section 8 the order; Section 9 what the instrument could not measure; Section 10 the literature; Section 11 how each reading could be wrong; Section 12 the bookkeeping; Section 13 what follows.

## 3. The two baselines, and how an answer is read

### 3.1 The reading rule

An answer letter is read from a continuation only if it finished: the model stopped of its own accord and closed its thinking. The answer is then the option letter on the last non-blank line of its reply. A continuation that ran into the 16,000-token limit has no answer and is counted as unresolved, written "?"; unresolved continuations stay in every denominator.

The quantity estimated is therefore P(completed answer = a within 16,000 generated tokens | prefix). It is not the probability of the answer the model would eventually give with an unlimited budget, and it is not a measure of when the model has internally settled. Where unresolved continuations are numerous the two can differ, so every table gives the unresolved count, Section 4.3 gives the fraction among continuations that answered, and Section 4.4 gives the range each large shift could take under any assumption about the unresolved ones.

This is not the rule the pre-registration named. The registered scorer missed answers written "Answer: (C)" and, in continuations that never finished, read the first letter of ordinary words as an option — "Answer: Cannot be determined" became C. It misread 36 of the 625 continuations. The departure is logged in the run folder and documented in the scorer audit; the registered numbers are given alongside the corrected ones throughout. Of the 625 continuations, 534 finished and every one of them carries a readable answer line; 91 hit the limit, all of them at cut-0 or at C-trace cuts B00 to B08.

### 3.2 The baselines

Without any thinking text, the model was asked 100 times. It answered C 49 times, A 32, E 19; never B, D or F. The 95% interval for C is 0.39 to 0.59, for E 0.13 to 0.28.

Thinking from an empty prefix (cut-0), it wrote its own text 25 times and answered E 18 times (0.72, interval 0.52 to 0.86), C 3 times (0.12, 0.04 to 0.30), with 4 unresolved.

The only difference between the two conditions is whether the model reasons before it answers. Without reasoning, a third of answers assert $0.05 flatly (A) and half acknowledge the missing information while still naming $0.05 (C); with reasoning, A disappears and seven in ten say the question is not well posed (E).

## 4. How the C-trace's answer distribution moves across its blocks

### 4.1 The table

P̂ is the fraction of the 25 continuations ending at C, with its 95% Wilson interval. Δ is the change from the previous cut — for m = 0, from cut-0 — with a Newcombe interval; a Δ whose interval excludes zero is a change the data distinguish from noise. Tk is the block's length in the model's own tokens; the whole trace is 4,740.

| cut m | block ends at | C | E | other | ? | P̂ [95%] | Δ [95%] | Tk |
|---|---|---|---|---|---|---|---|---|
| 0 | s7 | 12 | 1 | 0 | 12 | 0.48 [0.30, 0.67] | +0.36 [0.11, 0.56] | 139 |
| 1 | s12 | 7 | 8 | 0 | 10 | 0.28 [0.14, 0.48] | −0.20 [−0.43, 0.07] | 60 |
| 2 | s14 | 13 | 6 | 0 | 6 | 0.52 [0.34, 0.70] | +0.24 [−0.03, 0.47] | 13 |
| 3 | s22 | 6 | 8 | 0 | 11 | 0.24 [0.12, 0.43] | −0.28 [−0.50, −0.01] | 91 |
| 4 | s30 | 4 | 11 | 0 | 10 | 0.16 [0.06, 0.35] | −0.08 [−0.30, 0.14] | 92 |
| 5 | s35 | 6 | 8 | 0 | 11 | 0.24 [0.12, 0.43] | +0.08 [−0.14, 0.30] | 79 |
| 6 | s41 | 15 | 2 | 0 | 8 | 0.60 [0.41, 0.77] | +0.36 [0.09, 0.57] | 87 |
| 7 | s42 | 10 | 3 | 0 | 12 | 0.40 [0.23, 0.59] | −0.20 [−0.43, 0.07] | 25 |
| 8 | s57 | 10 | 8 | 0 | 7 | 0.40 [0.23, 0.59] | 0.00 [−0.25, 0.25] | 211 |
| 9 | s78 | 25 | 0 | 0 | 0 | 1.00 [0.87, 1.00] | +0.60 [0.37, 0.77] | 321 |
| 10 | s97 | 25 | 0 | 0 | 0 | 1.00 [0.87, 1.00] | 0.00 [−0.13, 0.13] | 266 |
| 11 | s106 | 25 | 0 | 0 | 0 | 1.00 [0.87, 1.00] | 0.00 [−0.13, 0.13] | 109 |

### 4.2 What the table says

From 0.12 at cut-0 the completed-C frequency reaches 1.00 after block 9, a total movement of 0.88. Each cut is a different prefix, so a shift is the difference between the output distributions of two prefixes; it does not by itself say which sentence, content or formatting inside the block is responsible.

The largest shift, +0.60, happens across block 9, sentences 58 to 78, headed "5. Evaluate the Options against the Textual Analysis:"; the trace's first hedge-word sentences sit inside it, at s65 to s67 (Section 7.3). Before it 10 of 25 continuations ended at C; after it 25 of 25. The block is 321 tokens, 6.8% of the trace. Two further shifts of +0.36 each: block 0, the first eight sentences, a heading and a restatement of the question, the options and the task; and block 6, "4. Identify the Nature of the Question:", where the model recognizes the classic riddle and its trap. One negative shift has an interval excluding zero, −0.28 across block 3, inside the enumeration of cases.

The registered gap statistic, the difference between the largest and the second-largest shift, is 0.24 with a bootstrap interval of 0.00 to 0.40 (10,000 draws; the upper end moves to 0.44 under other seeds, one grid step of Monte Carlo noise). This statistic is non-negative by construction, so its interval can touch zero and can never cross it. The signed difference between the two named blocks, an exploratory quantity, is Δ(block 9) − Δ(block 0) = +0.24 with a bootstrap interval of −0.08 to +0.52. Either way the two cannot be separated with 25 continuations per cut, and the registered near-tie rule names both.

Three blocks moved nothing at all (blocks 8, 10 and 11). The sum of the three largest shifts, 1.32, exceeds the total movement of 0.88 because the chance also falls between them: the path is a climb with setbacks, not a staircase.

**Each large rise sits inside one block.** Block 9's +0.60 sits between 0.00 and 0.00; block 6's +0.36 between +0.08 and −0.20; block 0's +0.36 is followed by −0.20. No large rise is spread across neighbours. What happens inside a block is not measured by this design, which places no cut inside a block; the archived sentence-level study of the same trace found the rise inside block 9 concentrated at one sentence, under different cuts and the earlier scoring.

**The largest shift is a selected quantity.** Block 9 is named because its observed shift is the largest of twelve, and an interval computed for one pre-named difference does not account for that selection. The interval [0.37, 0.77] is reported as the interval of that difference, not as a selection-adjusted statement; the bounds of Section 4.4 and a repetition on fresh continuations are the relevant checks.

**Against the registered numbers.** The registered scorer gave +0.56, +0.48 and +0.40 at blocks 9, 0 and 6, a cut-0 baseline of 0.16, a gap of 0.08 [0.00, 0.32], and put the first cut with 25 of 25 at block 11. The direction and the ranking of the three blocks are the same; the sizes differ because the registered reading credited answers to continuations that never finished. Under the corrected reading the sampling rule would have stopped the C-trace at block 9, so blocks 10 and 11 were sampled and judged beyond the registered stopping point; they are extra data and change nothing.

### 4.3 The continuations that never answered

At every cut before block 9, between 6 and 12 of the 25 continuations ran to the 16,000-token limit; from block 9 onward none did. Under the corrected reading "unresolved" has exactly one meaning, that the continuation hit the limit. Unfinished generations are concentrated at the early cuts and absent once the completed-C frequency reaches 1.00. That is an observation about generation length; it does not show that the model was undecided, since a continuation may have settled on an answer and gone on writing.

Among the continuations that did answer, the fraction ending at C is 0.92, 0.47, 0.68, 0.43, 0.27, 0.43, 0.88, 0.77, 0.56 for cuts 0 to 8 and 1.00 from cut 9 on. This view is exploratory and is a selected subset, not an unbiased estimate of eventual answers: which continuations finish may itself depend on where they are heading.

### 4.4 What the unresolved continuations could change

Holding the observed batches fixed, a shift is smallest if every unresolved continuation before the block would have ended at C and none after it, and largest in the reverse case. These are bounds on the missing outcomes, not sampling intervals.

| block | before: C, ? | after: C, ? | observed shift | range under any assignment |
|---|---|---|---|---|
| 9 | 10, 7 | 25, 0 | +0.60 | +0.32 to +0.60 |
| 0 | 3, 4 | 12, 12 | +0.36 | +0.20 to +0.84 |
| 6 | 6, 11 | 15, 8 | +0.36 | −0.08 to +0.68 |

The shifts across blocks 9 and 0 stay positive under every assignment. The shift across block 6 does not: if the eleven unresolved continuations before it had all been heading to C, it would vanish. Block 6 is therefore reported as an observed shift that the unresolved continuations leave open.

## 5. How the E-trace's answer distribution moves across its blocks

The E-trace is unaffected by the scoring correction: all 200 of its continuations finished. Its numbers are identical to v1.

| cut m | block ends at | E | C | other | ? | P̂ [95%] | Δ [95%] | Tk |
|---|---|---|---|---|---|---|---|---|
| 0 | s11 | 24 | 1 | 0 | 0 | 0.96 [0.80, 0.99] | +0.24 [0.03, 0.44] | 147 |
| 1 | s15 | 20 | 5 | 0 | 0 | 0.80 [0.61, 0.91] | −0.16 [−0.35, 0.03] | 59 |
| 2 | s18 | 14 | 10 | 1 | 0 | 0.56 [0.37, 0.73] | −0.24 [−0.46, 0.02] | 23 |
| 3 | s19 | 20 | 5 | 0 | 0 | 0.80 [0.61, 0.91] | +0.24 [−0.02, 0.46] | 52 |
| 4 | s41 | 24 | 1 | 0 | 0 | 0.96 [0.80, 0.99] | +0.16 [−0.03, 0.35] | 219 |
| 5 | s52 | 19 | 6 | 0 | 0 | 0.76 [0.57, 0.89] | −0.20 [−0.40, 0.00] | 204 |
| 6 | s70 | 24 | 0 | 1 | 0 | 0.96 [0.80, 0.99] | +0.20 [0.00, 0.40] | 255 |
| 7 | s74 | 25 | 0 | 0 | 0 | 1.00 [0.87, 1.00] | +0.04 [−0.10, 0.20] | 75 |

The E-trace starts at the 0.72 of cut-0 and reaches 1.00 after block 7; total movement 0.28. Its first block lifts the chance to 0.96. It then falls in two steps to 0.56: block 1 recognizes the classic riddle and states its standard answer, block 2 writes the classic constraint into the algebra, "Ball = x, Bat = x + 1.00". From that point 10 of 25 continuations end at C. Block 3 is a single sentence, "(Wait, the classic problem says 'The bat costs $1.00 more than the ball.' But this problem…", and after it the chance is back to 0.80. The two largest shifts, +0.24 each, sit at blocks 0 and 3; the gap is 0.00 with an interval of 0.00 to 0.28.

After two sentences that bring in the riddle the model knows, a third fewer continuations end at E; after one sentence that notes the difference, the earlier frequency returns. Section 8 looks at the same kind of event across 69 independent traces.

## 6. What the model does next after a cut

### 6.1 The measurement

Each continuation was cut into sentences and labeled by an LLM judge (Claude Sonnet 5, prompt v3, low thinking effort), and the label of the first new node recorded. Since every cut sits at a block end, we also recorded whether that first move opened a new block.

Across the 20 cuts, the first move opened a new block in 73% of continuations and was a Planning move in most. At 9 of the 20 cuts more than 88% of continuations began with Planning, and at a tenth exactly 88% did. Averaged over the cuts, a continuation reproduced the original trace's own next move 74% of the time. None of this depends on the answer letters, so Section 6 is unchanged by the scoring correction.

*(Erratum against v1: v1 said "8 of the 20 cuts"; the correct count above 0.88 is 9, and a tenth cut sits exactly at 0.88.)*

### 6.2 Does the next move depend only on the current one?

The registered test asks whether the label of the next move depends only on the label of the last move before the cut. Under that reading, all cuts sharing a last label should show the same distribution of next moves, up to sampling noise. The test pools the cuts that share a last label, measures how far each cut's distribution sits from the pooled one (total-variation distance: half the sum of absolute differences, 0 for identical tables, 1 for disjoint ones), and asks whether the spread S exceeds what random reassignment of continuations among those cuts produces.

| trace | cuts tested | groups | S observed | S expected if type-only | p |
|---|---|---|---|---|---|
| C-trace | 10 | 3 | 0.351 | 0.100 | ≤ 0.0001 |
| E-trace | 4 | 2 | 0.090 | 0.040 | 0.0033 |
| both | 17 | 4 | 0.329 | 0.091 | ≤ 0.0001 |

What the test rejects is precise: that the Level 1 label of the last move, alone, fixes the distribution of the next move across the tested prefixes. It does not show that the process is non-Markovian in general; a richer state — finer labels, content, progress through the task, position — might well have Markovian dynamics.

In the C-trace the observed spread is three and a half times what the last-type-only reading allows, and in 10,000 permutations it was never reached; with 10,000 permutations the smallest attainable value is 1/10,001, so the result is written as p ≤ 0.0001. The E-trace gives the same direction on four cuts with a ratio of 2.3. Cuts whose last label occurs only once cannot be tested and were excluded (two in the C-trace, four in the E-trace).

An example of what the test sees. Six C-trace cuts end on a Reasoning node. After cuts 3, 4 and 5, inside the enumeration of cases "If Ball = $0.05 / $0.01 / $0.55", the continuations open another case in 54%, 96% and 44% of the time; at cut 5 that 44% ties with plain Reasoning. After cut 6 they keep reasoning (Reasoning 64%, Assumption 16%, Planning 12%); after cuts 10 and 11 the most frequent first move is a new heading (Planning 88% and 56%). Same last label, different next-move distributions.

*(Erratum against v1: v1 grouped cut 6 with cuts 10 and 11 as cuts after which continuations "mostly start a new heading", and called 44% "mostly". At cut 6 Planning is 12%; the continuations keep reasoning. The corrected example is above.)*

**The same full label, different next moves.** The test is at Level 1, where one label covers unlike moves: in the C-trace's Reasoning group the last sentences before the cut carry `logical reasoning > algebra` (cuts 3, 4, 5), `calculation > algebra` (6), `hedge word analysis` (10) and `comparison > option vs option` (11), so a Markov chain over finer types could absorb part of the Level 1 spread. What survives the finest typing available: cuts 3, 4 and 5 end on the identical full path, the "Result:" sentence of each case of the enumeration, and their next-move distributions still differ — a new case is opened in 13 of 24, 24 of 25 and 11 of 25 continuations. An exploratory permutation test restricted to those three cuts gives S = 0.209 against a null mean of 0.078, p = 0.0006. This is the result to lead with, because it removes the objection that Level 1 is too coarse. What differs between the three cuts is how many cases have already been tried. That is progress through the task, and in a single trace it is inseparable from position in the text and from the content of the prefix; the comparison shows that the last label does not carry it, not that any one of those factors acts alone.

**Robustness of the labeling.** The registered second labeling covered two cuts, C-B09 and E-B06, and left every row unchanged. That check is weak: at both cuts the first new node is Planning in 25 of 25 continuations under either labeling, at E-B06 every continuation opens with a "Wait" sentence, which a deterministic rule labels whatever the judge says, and C-B09's last label is a singleton excluded from the C-trace test. What the check does establish is a noise floor: Level 1 agreement between the two labelings has a kappa of 0.78 and 0.83 on this run's continuations. The robustness of the conclusion rests instead on the history result below, which is registered and does not depend on a relabeling.

### 6.3 Against the average behaviour of similar traces

A second reference is the corpus table: over 44 traces of the model on the same item, which kind of move follows which. There, after a Reasoning node comes Planning 45% of the time and Conclusion 25%; after Planning, Reasoning 40% and Restatement 31%. The resampled next moves sit far from these averages: pooled over the cuts ending in Reasoning, the continuations give Planning 47%, Assumption 26%, Reasoning 25%, Conclusion 0%, a total-variation distance of 0.49 from the corpus row. Per last label the distances run from 0.32 to 0.75; per cut from 0.22 to 0.97. A table of averages does not describe what the model does at any particular point.

### 6.4 History, directly

Among cuts whose last move is Reasoning, the next-move distribution differs by a total-variation distance of 0.655 according to whether a Knowledge move occurred earlier in the prefix; the same comparison for Reflection and for Example gives 0.574 each. With such a node earlier the next move is Planning 70 to 81% of the time; without one it is an Assumption 42 to 65% of the time. Order shows too: cuts whose last two moves were Planning then Restatement differ from those with Restatement then Planning by 0.307.

In a single trace, "earlier in the prefix" and "earlier in the text" are the same thing — the enumeration of cases occupies blocks 2 to 8 of the C-trace — so these history effects cannot be separated from position effects with this design. They are associations between the next move and the context of the prefix. They do not show that an earlier Knowledge move causes the change, and they are not used as such; their role is to show, alongside the same-label result of Section 6.2, that the next-move distribution varies with something the last label does not record.

## 7. Inside the blocks that moved the answer

A chain is the sequence of node labels, abbreviated Pl, Rs, Re, Kn, As, Rf, Ex, Co, with the number of sentences in parentheses when more than one, and brackets for a sentence doing two things at once.

### 7.1 The first blocks

The C-trace's first block (eight sentences, +0.36) has the chain Pl(3) → Rs(5): "Here's a thinking process that leads to the suggested answer:", "1.", "Analyze the Request:", then the question, the options and the task restated as three bold inline items.

The E-trace's first block (twelve sentences, +0.24) has Pl(4) → Rs(3) → Pl → Rs → Pl → Rs(2): the same material under three sub-headings.

The two blocks restate the same thing and differ in shape and wording. When the model starts from nothing, 20 of its 25 cut-0 continuations open with the E-trace's chain and 18 of 25 end at E; only 2 of the 25 openings resemble the C-trace's. Whether the format causes the tilt or reveals an orientation already taken cannot be told from two traces.

### 7.2 Block 6 of the C-trace: recognizing the riddle (+0.36)

Chain Pl(2) → Kn(2) → Re(2): the heading "4. Identify the Nature of the Question:", then "This is a classic cognitive reflection test question (often attributed to Keith Stanovich / Shane Frederick)" and "The Trap: Most people intuitively answer $0.10 (Ball) and $1.00 (Bat)", then "Why?" and "Because $1.00 + $0.10 = $1.10." Recognizing the riddle and its trap raised the chance of C from 0.24 to 0.60. The one-sentence block that follows, "But wait, the problem usually adds the constraint 'The bat costs $1.00 more than the ball'", takes 0.20 of it back.

### 7.3 Block 9 of the C-trace: evaluating the options (+0.60)

Twenty-one sentences, chain Pl(3) → Re(3) → Pl → Re(2) → [Re+Rf] → Pl → Rf → Re(2) → Pl → Rf → Pl → [Re+Kn] → Re → Pl → Rf, under the heading "5. Evaluate the Options against the Textual Analysis:". Its rhythm is a series of small plans and verdicts: "(A) It is $0.05:" followed by reasoning about it and a verdict; "(B) It is probably $0.05:" with a reading of the word "probably" ("'Probably' implies probability. Unless there's a distribution of prices given, we can't assign probability."); and so on. Sentences 65 to 67 are the trace's first hedge-word analysis and are where the block turns: "'Probably' implies probability.", "Unless there's a distribution of prices given, we can't assign probability.", then a sentence weighing option (B) against the riddle's likely intent. Options (A), (B) and (C) name the same price and differ only in how firmly they claim it, so scoring them is reading those words. Before the block 10 of 25 continuations ended at C; after it 25 of 25. In terms of the labels, this is the first place where the trace stops analysing the problem and starts scoring answers.

The hedge word is not by itself a rise. The E-trace also analyses hedge words, at sentences 46, 69 and 147, and the first of those sits inside its block 5, which moves −0.20. What rises in the C-trace is the option evaluation; on this item the hedge words are how that evaluation is carried out, because they are what separates three of the six options.

What the continuations do here is the striking part. Starting from the end of block 8, all 24 labeled continuations open a new Planning block, as the original does, but the pages they then write are all different — Pl(2) → Re(13), Pl(3) → Rs(6), Pl(3) → Co(2) → Kn → Pl → Kn(2), no two alike. Yet all 25 sampled continuations end at C despite that variation in their text. With 25 samples this is limited evidence of stability across the continuations observed, not proof that the answer no longer depends on what is written.

### 7.4 The E-trace's dip and recovery

Block 2 (chain Pl → Re → [Re+As]) is three sentences: "Let's verify:", "Ball = x,", "Bat = x + 1.00" — the last both a calculation and an assumption, because it writes a constraint the question does not contain. After it 10 of 25 continuations end at C. Block 3 is the single combined sentence "(Wait, the classic problem says 'The bat costs $1.00 more than the ball.' But this problem…", and after it 20 of 25 end at E again.

### 7.5 Do the two traces think in the same shapes?

Yes in grammar, no in mix. Both build a block the same way: a numbered heading and then either a restatement or a stretch of reasoning. Of the C-trace's 47 blocks, 19 open Planning → Reasoning and 14 Planning → Restatement; of the E-trace's 38, 8 and 12. Both average about four nodes per block. The corpus table shows the same two openings as most common.

The difference is what the blocks are spent on. The C-trace reasons: four blocks opening directly with a case, 162 Reasoning sentences of 375, long stretches of enumeration and option evaluation. The E-trace restates and concludes: 57 Restatement sentences of 254, and block openings Planning → Knowledge, Planning → Conclusion, Planning → Reflection that the C-trace almost never uses. The E-trace reaches a high completed-E frequency early, 0.96 after its first block, but does not hold it: it falls to 0.56 and to 0.76 before ending at 1.00. The C-trace reaches 1.00 only at its tenth block and stays there. Same building blocks, different buildings.

## 8. The order in which the model brings in what it knows (exploratory)

### 8.1 What is being asked, and on which texts

The two traces differ in when the classic riddle enters. The C-trace writes its equations at sentence 10 and first brings in the riddle's missing constraint at sentence 42, as an interruption: "But wait, the problem usually adds the constraint 'The bat costs $1.00 more than the ball'." The E-trace brings the constraint in at sentence 18, before any algebra of its own, and works from it. This section asks whether that difference predicts the answer.

It is asked on texts with **no prefix at all**, so that the order is the model's own: the 25 cut-0 continuations of this run and the 44 archived traces of the same item, 69 texts in total. Each text is one observation; there is no clustering and nothing is inherited.

The two batches share the item text, the six options and the answer-format instruction word for word, the model (Qwen 3.6-27B), the provider, temperature 1.0 and the 16,000-token limit. They differ in how the request was sent: the archived traces through the chat endpoint, the model opening its own thinking; the cut-0 continuations through the completions endpoint with the chat template written out and the thinking block opened for the model. Section 8.2 gives the result for each batch separately.

The quantities are read from the text of each trace, not from a label:

- **algebra**: a sentence that sets up, manipulates or draws a conclusion from the item's quantities — the two prices, their sum, the inequality, the solution set.
- **constraint imported**: a sentence that brings in the missing clause of the classic riddle, "the bat costs $1.00 more than the ball", in words or as a relation such as B = b + 1.00.

The first of each is located, and the pattern is the order in which they occur.

One sentence can be both: "Bat = x + 1.00" sets up the quantities and imports the constraint at once. When the first algebra and the first constraint import fall in the same sentence the order is undefined at this resolution, and the trace is a **tie**. Three of the 69 traces are ties. They are counted with the constraint-first traces in the table below, on the ground that the constraint is present from the first moment of the algebra; Section 8.2 gives the result under the other two treatments.

This analysis is exploratory throughout. It was added after the pre-registration, and its definition of "constraint imported" was settled while these same 69 traces were being examined (Section 11).

### 8.2 The result

| pattern | traces | C | E | unresolved | P(C) [95%] |
|---|---|---|---|---|---|
| ⟨ algebra --> constraint imported ⟩ | 16 | 5 | 10 | 1 | 0.31 [0.14, 0.56] |
| ⟨ constraint imported --> algebra ⟩, ties included | 53 | 2 | 47 | 4 | 0.04 [0.01, 0.13] |

Unresolved traces are kept in the denominator, as everywhere in this document. The difference in P(C) is +0.27 [0.08, 0.52]; Fisher's exact test, two-sided, gives p = 0.006. Conditional on answering the figures are 5 of 15 against 2 of 49, a difference of +0.29 [0.09, 0.54], p = 0.006.

In words: C is rare under both orders, about one trace in three when the algebra comes first and about one in twenty-five when the constraint comes first, roughly eight times as frequent. Ten of the sixteen algebra-first traces still end at E, and two constraint-first traces end at C, so the order neither fixes the answer nor is necessary for C.

**How far the result depends on choices that could have gone otherwise.**

- *Ties.* Excluding the three ties gives 5 of 16 against 2 of 50, difference +0.27, p = 0.007; counting them as algebra-first gives 5 of 19 against 2 of 50, difference +0.22 [0.05, 0.45], p = 0.015. The direction holds under all three treatments.
- *Unresolved traces.* The most adverse assignment, in which the one unresolved algebra-first trace would not have ended at C and all four unresolved constraint-first traces would have, gives 5 of 16 against 6 of 53 and p = 0.11. That assignment is not an estimate of what those traces would do; it shows that the conventional significance of the result is conditional on how the five unfinished traces are treated.
- *Batch.* At cut-0 of this run, 2 of 5 algebra-first traces end at C against 1 of 20 constraint-first (p = 0.09); in the archived batch, 3 of 11 against 1 of 33 (p = 0.04). The direction is the same in both, and neither batch alone carries the claim.
- *The two source traces.* The C-trace and the E-trace of this study were chosen from the archived batch. Without them the comparison is 4 of 14 against 2 of 53, a difference of +0.25 [0.06, 0.51].

The two arms differ in shape as well as in outcome. In the constraint-first traces the sequence is close to mechanical: the riddle is named around sentence 14, its constraint quoted around sentence 17, the algebra done from about sentence 23. In the algebra-first traces the algebra is already under way, at a median first index of 17, when the constraint arrives at a median of 20, frequently in a sentence beginning "But wait" or "Wait, check the prompt carefully".

**What this does and does not show.** The model chose both the order and the answer, and nothing was manipulated. An orientation toward one reading of the item could produce both the order and the answer, in which case the order would be a symptom and not a cause. The result is an association in spontaneously generated text. Testing whether the order drives the answer would need an intervention that rearranges matched reasoning content with controls for wording and position, which this study does not attempt.

**Robustness to the definition of algebra.** Requiring the algebra sentence to contain a written relation (=, >, <), rather than accepting a statement about the quantities in words, moves the first-algebra index in 32 of the 69 traces and changes the result not at all: the same traces fall in the same arms.

### 8.3 What was withdrawn, and why

Version 1 of this document reported P(C | ⟨ algebra --> famous problem ⟩) = 0.58 over 293 continuations and P(E | ⟨ famous problem --> algebra ⟩) = 0.81 over 225, pooled over all cuts of both traces. Those numbers are withdrawn. Two reasons, both about measurement rather than outcome.

First, they located the famous problem by its label, the leaf `Knowledge > world knowledge > famous problem (CRT)`. In the author's own reviewed labels that leaf marks 10 of the 43 C-trace sentences that touch the riddle and 6 of 31 in the E-trace, because a sentence that mentions the riddle while doing something else takes the label of what it does. The leaf marks sentences whose main job is recalling the riddle, not sentences that use it.

Second, they were pooled over cuts at which the order is inherited from the prefix rather than chosen: 289 of the 293 algebra-first continuations came from C-trace cuts and 197 of the 225 constraint-first ones from E-trace cuts, and all 25 continuations of a cut share one pattern. The comparison was between two prefixes as much as between two orders.

The analysis above avoids both: it uses no label, and it uses only texts with no prefix.

### 8.4 Recognition is not use

Naming the riddle carries no information here. Among the 69 prefix-free traces, every one names it, 67 of them by sentence 20, with a median first mention at sentence 14. A variable with almost no variance cannot separate the answers, and it does not: sorting the same 69 traces by whether the naming precedes the algebra leaves 2 traces in one arm and 67 in the other.

What varies, and what is associated with the answer, is when the content of the riddle is brought to bear. The distinction matters for the instrument as much as for the result, and Section 9 takes it up.

## 9. What the instrument could not measure

The labeling scheme has one axis. Levels 1 and 2 record what a sentence does — Planning, Reasoning, Knowledge, and their sub-kinds — and Level 3 records, where it exists, what the sentence is about. That arrangement has two consequences this run made visible.

**The same object scatters across the tree.** "Algebra" is a Level 3 leaf under five different parents: `Reasoning > calculation`, `Reasoning > logical reasoning`, `Reasoning > defining symbols`, `Assumption > branching (case split)` and `Example > non-exhaustive listing`. Asking when the model first does algebra therefore means querying five paths, and asking it of a kind of sentence the scheme does not separate is impossible.

**Objects are typed at different resolutions.** Hedge-word analysis is a Level 2 node with three leaves recording how the hedge is read: everyday, mathematical, undecided. The famous problem is a single leaf with no record of how it enters. The scheme already does for one object what Section 8 needed for the other, and simply did not do it there.

The result is that a sentence carries the axis that happened to win. In one trace, "If the question intended to ask the standard riddle, it is missing the phrase '$1.00 more'" carries `Reasoning > logical reasoning > algebra`: the function is an inference, the object is the wording of the question, and the label records neither accurately.

A proposal for a later run, not a result of this one, is to separate the two axes: a function path as now, and an object with its own leaves — algebra as symbols, relation, computation, solution set, verification; the famous problem as recognition, constraint import, standard answer, contrast with the item. Both of this run's questions then become single queries rather than scans, and the distinction of Section 8.4 is available by construction. That is scheme v7 and future work; this paper reports the instrument as it was registered and run.

## 10. Next to what others have found

Searched on 2026-09-18; every identifier below is to be verified against the paper itself before it is cited.

- **Order in the input.** Chen, Chi, Wang and Zhou, "Premise Order Matters in Reasoning with Large Language Models" (ICML 2024; arXiv 2402.08939): models are brittle to the order of premises in the prompt and do best when it matches the order of the proof. That is order in what the model is given, measured as accuracy. Section 8 is about order in what the model writes, measured as which answer it chooses.
- **Order in a finished trace.** "Rethinking Dense Sequential Chains" (arXiv 2605.07307): shuffling the lines of a completed chain changes the extracted answer by less than half a point. That study and Section 8 look at different stages, reading a finished trace against generating one; the two together do not establish where an order effect would arise.
- **Two sources of the answer.** Wang et al., "Reasoning or Retrieval? A Study of Answer Attribution on Large Reasoning Models" (ICLR 2026; arXiv 2509.24156): answers emerge from competing chain-of-thought reasoning and direct retrieval from memory. Section 8 observes, in text, an association between which of the two appears first and the answer; it does not measure the mechanisms.
- **Answer stabilization and sentence-level attribution.** "Beyond the Commitment Boundary" (arXiv 2606.13603) studies where the answer stabilizes and finds a single pivotal step near the midpoint. Thought Anchors (Bogdan et al.; arXiv 2506.19143; checked against the paper on 2026-09-19) already does two things this study does: it labels every sentence with a function taxonomy of eight categories (problem setup, plan generation, fact retrieval, active computation, uncertainty management, result consolidation, self checking, final answer emission), assigned by an LLM, and it measures each sentence's counterfactual importance by resampling continuations and comparing answer distributions. It reports that the sentences with outsized influence are typically planning or backtracking sentences, which agrees with the blocks here opening on Planning moves and on "Wait". Thought Branches (arXiv 2510.27484) also studies continuations by resampling.
- **A methodological caution.** "It's the Problem, Not the Path" (arXiv 2609.03436) argues that claims about reasoning trajectories need a counterfactual control at the level of the claim. Sections 4 to 6 have that control: the prefix is held fixed and only the continuation varies. Section 8 does not; it is observational, on texts where the model chose its own order.
- **The item.** Hagendorff and colleagues, "Thinking Fast and Slow in Large Language Models" (arXiv 2212.05206): models give the intuitive answer to cognitive-reflection items and chain-of-thought removes it, on the classic item. Here the item has its constraint deleted, so the question is not whether the model computes but which reading of an underdetermined question it adopts.

Typing the moves of a trace and resampling continuations are therefore not new, separately or together. What this study adds is narrower: a hierarchical labeling with blocks derived from it by fixed rules; cuts placed at those block boundaries rather than at every sentence; an explicit registered test of whether the last label fixes the next-label distribution, with the same-full-label comparison of Section 6.2; and the exploratory measurement of the order of algebra and constraint import in prefix-free traces. Each of these distinctions is to be checked against the full text of the papers above before it is claimed, and every identifier in this section is an arXiv record whose publication status is to be verified.

## 11. How each reading could be wrong

0. What is estimated. Every P̂ is the frequency of a completed answer within 16,000 tokens from a given prefix. It is not the eventual answer under an unlimited budget and not a measure of internal commitment. A shift between two cuts is a difference between the output distributions of two prefixes; the design does not isolate which content inside the block produces it.
1. Twenty-five continuations per cut is a small sample. Near one half the standard error of a proportion is 0.10, so changes smaller than about 0.25 cannot be told from noise. The C-trace's wandering between blocks 1 and 8 should not be read block by block; only shifts whose intervals exclude zero are individually trustworthy.
2. The scoring rule is a departure from the pre-registration. It was adopted after the run, on the ground that the registered scorer misreads 36 continuations, and both readings are reported. A reader who prefers the registered numbers will find them in Section 4.2 and in the run folder.
3. The unresolved continuations. Under the corrected rule a continuation that hits the token cap has no answer, which lowers P̂ at the early C-trace cuts, where 6 to 12 of 25 hit it. The shifts across blocks 9 and 0 stay positive under every assignment of the unresolved continuations; the shift across block 6 does not (Section 4.4).
4. The labeler. Everything in Sections 6 and 7 rests on labels produced by an LLM judge. Against the author's reviewed labels of the two traces it agrees at Level 1 with a kappa of 0.73 to 0.80; relabeling this run's continuations at two cuts gave kappa 0.78 and 0.83. The judge is a named source of uncertainty and its prompt is part of the record.
5. The reviewed labels themselves were produced by an LLM assistant and reviewed by the author for face validity, not labeled blind by a second human, and the scheme's rules were written on these same two traces.
6. The blocks come from those labels. A different labeling would cut the text in different places.
7. One item, one model, two traces, and for Section 8 one prompt condition. This is a case study; nothing here transfers by itself. The two traces were chosen from 44 because one ends at C and one at E, so they do not represent the range of the model's trajectories on this item, and 39 of those 44 end at E.
8. Section 8 is exploratory and observational. It shows that texts which do the algebra first end at C more often; it does not show that changing the order would change the answer, since the model chose both. Its definition of "constraint imported" was settled while these same 69 traces were being examined, so its interval and p-value are not those of a pre-specified test. Its events were located by a text rule applied by one reader, without a second annotator blind to the answer. Its significance depends on how five unfinished traces are treated (Section 8.2). A test of the frozen definition on fresh traces is stated in Section 13.
9. Stopping. The registered rule stops a trace at the first cut where all 25 continuations give its answer, and the later blocks are then assumed, not measured, to move nothing. Under the corrected reading that cut is block 9 of the C-trace, so blocks 10 and 11 were in fact sampled beyond the stopping point and both read 25 of 25; blocks 12 to 46 of the C-trace and 8 to 37 of the E-trace were not sampled. The stopping rule is adaptive, and the intervals reported do not adjust for it.
10. The largest shift is selected as the largest of twelve, and its interval does not adjust for that selection (Section 4.2).
11. Labels and blocks together. A disagreement about a label can move a block boundary as well as a transition count. Agreement was measured on the labels; the sensitivity of the block boundaries, and so of the cuts, to the labeling was not.
12. The first-block observation may be an effect of format rather than content: a prefix in one trace's heading style may commit the model to that trace's way of proceeding.

## 12. Bookkeeping

**The re-derivation.** Pre-registration 7.2 asks for an independent re-derivation of P̂, Δ and the gap from the raw continuations. The quantities were computed three times by separate code from the same records: the registered pipeline; an independent script written by a second AI system from a written procedure, without sight of the registered tables; and the author's own script. All three agree on every count, proportion, shift and interval, under both the registered and the corrected reading. The three share one written procedure and one definition of the corrected rule, so they verify the computation, not the sampling.

**Money and time.** Sampling on DeepInfra: 625 continuations, $13.06 against a ceiling of $45. Labeling on the Claude API in batch mode: $66.84 against a ceiling of $80, including automatic retries and $3.82 for the second labeling of two cuts. Two continuations of 525 remained unlabeled after three attempts and are excluded from Sections 6 and 7 only. The run took 17:59 to 22:27 on 2026-09-17 for the sampling and 22:29 to 02:53 for the labeling. The rescoring and the reanalysis cost nothing; the archived traces of Section 8 and their labels were already in the repository.

**Departures from the registered design.** Two logged by the judge (the unlabeled continuations) and one adopted afterwards (the scoring rule). All three are in the run folder's `DEPARTURES.md`.

## 13. What follows

- The order result of Section 8 is exploratory. Freezing the two event definitions and the tie rule, sampling fresh prefix-free traces of the same prompt, and having a second reader locate the events blind to the answer on a subset would turn it into a confirmatory test; it needs no judge, since the events are read from the text.
- A stronger labeling check than the registered one: an independent second labeling of a stratified sample of the informative cuts, those in the Reasoning group of Section 6.2, with the transition test rerun on it.
- A predictive complement to the permutation test: held-out prediction of the next label from the last label alone against a model with pre-specified additional features of the prefix.
- Scheme v7, with the function and object axes separated (Section 9), before any further labeled run.
- Stage two, node-level cuts inside the blocks that carried the movement, is not part of this paper.
- The paper: organized around three questions rather than around this document's history — how the completed-answer distribution and the unresolved rate move across block boundaries; whether the last Level 1 label fixes the next-label distribution; whether the order of algebra and constraint import is associated with the answer in prefix-free traces, stated as exploratory. The scorer audit, the re-derivation procedure, the cost accounting and the changelog go to supplementary material, with a short statement of the departures and their effect on the estimand in the methods.

## Appendix A — re-deriving the headline numbers

The procedure is `docs/shared/2026-09-19_rederivation_steps_v1.md`, nine steps in two passes: from the recorded `letters` field, which reproduces the registered tables, and from the text of each continuation, which checks the scorer. The corrected tables of this document are produced by `scripts/s5_rescore.py` followed by the registered `scripts/s4_analyze.py`, and the order analysis of Section 8 by the procedure described there.

## Changelog

- 2026-09-19 v2 (= chat3 of 2026-09-19; confirmed by Kian 2026-09-19) — Revised after an external scientific review of the first draft of this version. The estimand is defined as the completed answer within 16,000 tokens (Sections 1, 3.1, 11) and the language of an internal decision is replaced by language about observed answer distributions (Sections 2, 4, 5, 7.3, 7.5; section titles 4 and 5). New Section 4.4 gives the range each large C-trace shift can take under any assignment of the unresolved continuations: blocks 9 and 0 stay positive, block 6 does not, and Section 2 now says so. Section 6.2 states exactly what the test rejects (the last Level 1 label as sole state), leads with the same-full-label comparison, and corrects "mostly" for 44%. Section 8 is labeled exploratory, uses the document's own denominator convention (0.31 against 0.04), states the tie rule with three ties, and adds sensitivity to ties, to the unresolved traces, to the batch and to the two source traces; the sentence that algebra-first "makes the classic answer available at all" is removed as false. Section 10 corrects the account of Thought Anchors, which does type sentences and resample, and narrows the novelty statement. Section 11 gains items on the estimand, selection of the largest shift, the adaptive stopping rule, source-trace selection and block-boundary sensitivity. Section 3.2 reports A and C separately.
- 2026-09-19 (chat2 of the same chat, superseded before saving) — Section 2's headline sentence names the hedge words as well as the option evaluation, since the trace's first hedge-word sentences (s65 to s67) sit inside block 9; Sections 4.2 and 7.3 say the same, and 7.3 adds the E-trace caution that a hedge-word sentence is not by itself a rise (its block 5 moves −0.20). Nothing else changed.
- 2026-09-19 (chat1 of the same chat, superseded before saving) — Second results document. Corrected scoring throughout (decision P6): new mediation tables and figures for the C-trace and the two baselines, the E-trace unchanged. Errata of v1 corrected: the count of cuts above 88% Planning (Section 6.1), the example of the type-only test (Section 6.2), and the list of shifts whose intervals exclude zero (Section 4.2). Section 6.2 gains the finer-typing check and the honest account of the second labeling. Section 8 rebuilt on 69 prefix-free traces and the constraint-import definition; the v1 numbers withdrawn with the reasons. Section 9 new. Section 12 records the re-derivation as complete.
