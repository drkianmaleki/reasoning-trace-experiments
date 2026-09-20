# Stage one — what the block-boundary resampling run found — reasoning-trace-experiments — 2026-09-18 v1

File: 2026-09-18_stage1_results_v1.md (local version 1 = chat version 4 of the chat begun 2026-09-15 for this document). Claude drafted from the registered analysis; Kian confirmed the document on 2026-09-18. Every number comes from runs/experiments/resample_blocks_2026-09-17_1759/stage1_summary.md (commit 7577ab3) or was recomputed by Claude from the raw files (continuations.jsonl, transition_pnext.csv, the judge's label files); wherever both exist they agree. Kian's own re-derivation of P̂_m, Δ_m and the gaps from continuations.jsonl (pre-registration v2, Section 7.2; recipe in Appendix A) is the owner's check on those headline numbers and is recorded in the STATE file when done. The pre-registration's wording rule applies: the numbers are described, not judged.

This document is written for a reader who has not seen the project's notation. Every term is explained where it first appears, with an example from the traces themselves. The exact definitions live in the labeling scheme (docs/shared/2026-09-17_labeling_scheme_v6.md) and the registered design in the pre-registration (2026-09-17_preregistration_stage1_v2.md); nothing here contradicts them.

## 1. The question, in plain words

When a reasoning model thinks out loud before it answers, its written thoughts are a long text. We want to know where in that text the answer gets decided, and whether the order of the thoughts matters or only the kind of thought the model is currently having.

The model is Qwen 3.6-27B. The item is the bat-and-ball riddle with one clause deleted: "A bat and a ball cost $1.10 in total. The bat costs more than the ball. How much does the ball cost?" followed by six options — (A) it is $0.05; (B) it is probably $0.05; (C) there is not enough information, but the answer is most likely $0.05; (D) I am not sure; (E) the question is not well posed; (F) none of the above. The classic riddle says the bat costs $1.00 more than the ball, which fixes the answer at $0.05; without that clause any ball price below $0.55 works, so the "right" answer is a matter of reading: E says the question is broken, C says it is underdetermined but $0.05 is the intended answer, A says $0.05 flatly.

We studied two of the model's own thinking texts, called traces: the C-trace, a text that ends by answering C, and the E-trace, a text that ends by answering E. Each trace was cut into sentences (375 in the C-trace, 254 in the E-trace) and every sentence was given a label saying what kind of move it is — for instance Planning ("Let's check the options"), Reasoning ("then Bat = 1.10 − 0.55 = $0.55"), Restatement (repeating the question), Knowledge ("this is the classic cognitive reflection test question"), Assumption ("If Ball = $0.05,"), Reflection ("That checks out"), Example, or Conclusion. Consecutive sentences with the same label form a node, and the text is further grouped into blocks — stretches that begin where the model announces a new phase, typically a numbered heading such as "4. Identify the Nature of the Question:", or where it opens a new case, or says "Wait". The C-trace has 47 blocks, the E-trace 38. Which sentence gets which label was decided by Claude and reviewed by Kian; the blocks follow from the labels by fixed rules.

The experiment is resampling. Take the trace up to the end of a block — that prefix is called a cut — feed it back to the model as its own unfinished thinking, and let the model finish 25 times. Each finished text is a continuation; it ends with an answer letter, and it can be labeled and cut into blocks like the original. Two things are then measured for every cut. First, how often the continuations arrive at the trace's own final answer (C for the C-trace, E for the E-trace): written P(final answer | cut(B_m)) and estimated by P̂_m, read "P-hat", the fraction of the 25 continuations from the end of block m that reach it. Second, what kind of move comes next — written P(next = Y | cut(B_m)), the fraction whose first new node after the cut carries the label Y. A third kind of expression appears in Section 8: P(final answer | ⟨ X --> Y ⟩), the fraction of continuations whose text contains a move of kind X followed, at any later point, by a move of kind Y, and ends at the given answer. The angle brackets name a pattern in the text; the double arrow reads "and later".

Two extra conditions give the reference points below the first block. The no-think baseline: the model answers immediately with no thinking text at all (100 samples). Cut-0: the model thinks from an empty prefix, producing its own text from scratch (25 samples).

## 2. The short version

Three results, each stated as a number and then in words.

Reasoning changes the answer. Asked to answer without thinking, the model said C 49 times in 100, A 32 times, E 19 times. Asked to think first and then answer, it said E 18 times in 25 (72%) and C only 4 times (16%). The act of writing out its reasoning moved the model's majority answer from "$0.05 is the intended answer" to "the question is not well posed".

The decision is made in two places, not smoothly. In the C-trace the chance of ending at C starts at 16% (the cut-0 baseline) and reaches 100% after the twelfth block. Two blocks carry most of the movement: the first block, eight sentences of headings and restatement, raises it from 16% to 64% (a shift of +0.48); and the tenth block, C-B09, the passage where the model evaluates the six options one by one against the text of the question, raises it from 40% to 96% (+0.56). Between them the chance wanders between 28% and 68%. The two large shifts are about equal in size — the data cannot say which is larger. In the E-trace the movement is small (72% → 100%) and the chance dips once to 56%, right after the model writes the classic constraint "Bat = x + 1.00" into its algebra, and recovers when it notices the deletion ("Wait, the classic problem says…").

What comes next depends on more than the last move. If the model's next kind of move depended only on its current kind of move — a "Markov" or type-only process — then, whenever a cut ends on a Reasoning node, the distribution of the next move would be the same. It is not: at some cuts ending in Reasoning the continuations almost always open a new case ("If Ball = …", 96%), at others they almost always start a new heading (88%). The registered test rejects the type-only reading in both traces (p = 0.0001 in the C-trace, 0.0033 in the E-trace). And the next moves the model actually makes at a given cut are far from what a table of average transitions, counted over 44 similar traces, would predict.

Sections 3–7 give the details with examples; Section 8 asks whether the order of three particular kinds of thought predicts the answer; Section 9 places the results next to what others have found; Section 10 lists how each reading could be wrong; Section 11 is the budget, which a reader may skip; Section 12 says what follows.

## 3. The two baselines: answering without thinking, and thinking from nothing

Without any thinking text (the no-think baseline), the model was asked the question 100 times. It answered C ("not enough information, but most likely $0.05") 49 times, A ("it is $0.05") 32 times, and E ("the question is not well posed") 19 times; never B, D or F. The 95% interval for the chance of C is 0.39 to 0.59 — that is the range of true probabilities compatible with 49 of 100 — and for E it is 0.13 to 0.28.

Thinking from an empty prefix (cut-0), the model wrote its own thinking text 25 times and answered E 18 times, C 4 times, B twice, and once produced no readable answer letter (counted as "?"). The chance of E is 72% with a 95% interval of 0.52 to 0.86; the chance of C is 16% (0.06 to 0.35).

The only difference between the two conditions is whether the model reasons before it answers. Without reasoning, four in five answers treat $0.05 as the answer (A or C); with reasoning, seven in ten say the question is not well posed. The reasoning text is what carries the model from the riddle it remembers to the text it was actually given.

## 4. Where the C-trace's answer gets decided

### 4.1 Reading the table

For the C-trace, the model's own answer is C, so P̂ is the fraction of the 25 continuations that end at C. The table has one row per cut. The row "m = 0" is the cut after the first block, which ends at sentence 7; "m = 9" is the cut after the tenth block (blocks are numbered from 0), which ends at sentence 78. The columns C, E, other and "?" are the raw counts out of 25: how many continuations ended at C, at E, at some other letter, or without a readable letter. P̂ is C divided by 25, followed by its 95% interval in brackets. Δ (delta) is the change in P̂ from the previous cut — for m = 0, the change from cut-0 — with its own interval; a Δ whose interval excludes zero is a change the data can distinguish from noise. Tk is the length of the block in the model's own tokens (roughly, word pieces); the whole C-trace is 4,740 tokens.

| cut m | block ends at | C | E | other | ? | P̂ [95% interval] | Δ [95% interval] | Tk |
|---|---|---|---|---|---|---|---|---|
| 0 | s7 | 16 | 2 | 2 | 5 | 0.64 [0.45, 0.80] | +0.48 [0.21, 0.66] | 139 |
| 1 | s12 | 9 | 8 | 1 | 7 | 0.36 [0.20, 0.55] | −0.28 [−0.50, 0.00] | 60 |
| 2 | s14 | 14 | 6 | 0 | 5 | 0.56 [0.37, 0.73] | +0.20 [−0.07, 0.43] | 13 |
| 3 | s22 | 11 | 8 | 1 | 5 | 0.44 [0.27, 0.63] | −0.12 [−0.37, 0.15] | 91 |
| 4 | s30 | 7 | 11 | 0 | 7 | 0.28 [0.14, 0.48] | −0.16 [−0.39, 0.10] | 92 |
| 5 | s35 | 7 | 8 | 1 | 9 | 0.28 [0.14, 0.48] | 0.00 [−0.24, 0.24] | 79 |
| 6 | s41 | 17 | 2 | 1 | 5 | 0.68 [0.48, 0.83] | +0.40 [0.12, 0.60] | 87 |
| 7 | s42 | 12 | 3 | 1 | 9 | 0.48 [0.30, 0.67] | −0.20 [−0.43, 0.07] | 25 |
| 8 | s57 | 10 | 8 | 1 | 6 | 0.40 [0.23, 0.59] | −0.08 [−0.33, 0.18] | 211 |
| 9 | s78 | 24 | 0 | 0 | 1 | 0.96 [0.80, 0.99] | +0.56 [0.31, 0.73] | 321 |
| 10 | s97 | 24 | 0 | 0 | 1 | 0.96 [0.80, 0.99] | 0.00 [−0.16, 0.16] | 266 |
| 11 | s106 | 25 | 0 | 0 | 0 | 1.00 [0.87, 1.00] | +0.04 [−0.10, 0.20] | 109 |

### 4.2 What the table says

Starting from the 16% of cut-0, the chance of ending at C reaches 100% after block 11, a total movement of 0.84. The sampling stopped there, as the design prescribed: once all 25 continuations of a cut end at the trace's own answer, the later blocks are taken to be settled and are not sampled (34 blocks of the C-trace were not sampled for this reason).

The largest single shift, +0.56, happens across block 9, the passage from sentence 58 to sentence 78 headed "5. Evaluate the Options against the Textual Analysis:". Before it, 10 of 25 continuations ended at C; after it, 24 of 25. The block is 321 tokens long, 6.8% of the trace. The second largest, +0.48, happens across block 0, the first eight sentences — a heading and a restatement of the question, the options and the task. The two shifts are close: their difference (called the gap) is 0.08, and the range of gaps compatible with the data, obtained by resampling the continuations 10,000 times, is 0.00 to 0.32. In words: the data cannot tell which of the two blocks matters more.

Three further shifts have intervals that do not include zero or barely touch it: +0.40 across block 6, the passage "4. Identify the Nature of the Question:" where the model recognizes the classic riddle and its trap; −0.28 across block 1 (the model writes the equation and the condition); −0.20 across block 7, a one-sentence block that begins "But wait, the problem usually adds the constraint…". Two blocks moved nothing at all (Δ = 0): blocks 5 and 10. The sum of the three largest shifts, +0.56 +0.48 +0.40 = 1.44, exceeds the total movement of 0.84 because the chance also falls between them: the path is not a staircase but a climb with setbacks.

### 4.3 The continuations that never answered

At every cut before block 9, between 5 and 9 of the 25 continuations ran to the length limit of 16,000 tokens without producing a readable answer letter — the "?" column. From block 9 onward this never happened. The registered rule counts a "?" as "did not end at C", which lowers P̂ at the early cuts. An exploratory view, not part of the registered analysis: among the continuations that did produce a letter, the fraction ending at C was 0.80, 0.50, 0.70, 0.55, 0.39, 0.44, 0.85, 0.75, 0.53 for cuts 0 to 8, then 1.00 from cut 9 on. The picture is the same — two large steps and a plateau — with the plateau sitting higher. What the "?" column adds is an observation of its own: while the answer is undecided, the model's continuations are long enough to hit the cap; once it is decided, they are not.

## 5. Where the E-trace's answer gets decided

For the E-trace the model's own answer is E; the whole trace is 2,890 tokens.

| cut m | block ends at | E | C | other | ? | P̂ [95% interval] | Δ [95% interval] | Tk |
|---|---|---|---|---|---|---|---|---|
| 0 | s11 | 24 | 1 | 0 | 0 | 0.96 [0.80, 0.99] | +0.24 [0.03, 0.44] | 147 |
| 1 | s15 | 20 | 5 | 0 | 0 | 0.80 [0.61, 0.91] | −0.16 [−0.35, 0.03] | 59 |
| 2 | s18 | 14 | 10 | 1 | 0 | 0.56 [0.37, 0.73] | −0.24 [−0.46, 0.02] | 23 |
| 3 | s19 | 20 | 5 | 0 | 0 | 0.80 [0.61, 0.91] | +0.24 [−0.02, 0.46] | 52 |
| 4 | s41 | 24 | 1 | 0 | 0 | 0.96 [0.80, 0.99] | +0.16 [−0.03, 0.35] | 219 |
| 5 | s52 | 19 | 6 | 0 | 0 | 0.76 [0.57, 0.89] | −0.20 [−0.40, 0.00] | 204 |
| 6 | s70 | 24 | 0 | 1 | 0 | 0.96 [0.80, 0.99] | +0.20 [0.00, 0.40] | 255 |
| 7 | s74 | 25 | 0 | 0 | 0 | 1.00 [0.87, 1.00] | +0.04 [−0.10, 0.20] | 75 |

The E-trace starts high, at the 72% of cut-0, and reaches 100% after block 7; the total movement is only 0.28. Its first block — the heading "1. Analyze the User Input:" with the question, the options and the task listed under sub-headings — lifts the chance to 96% (+0.24). The chance then falls in two steps to 56% after block 2: block 1 recognizes the classic riddle and states its standard answer ($0.05 for the ball), block 2 begins to verify and writes the classic constraint into the algebra, "Ball = x, Bat = x + 1.00". From that point 10 of 25 continuations end at C — the model has, so to speak, been reminded of the riddle it knows. Block 3 is a single sentence, "(Wait, the classic problem says 'The bat costs $1.00 more than the ball.' But this problem…", and after it the chance is back to 80%. It rises to 96% after block 4 (the analysis of what the deletion does), dips to 76% after block 5 (the option-by-option evaluation), and settles at 96% and then 100%. The two largest shifts, +0.24 each, sit in blocks 0 and 3; the gap between them is 0 with an interval of 0.00 to 0.28. No E-trace continuation hit the length cap.

## 6. What the model does next after a cut

### 6.1 The measurement

For every cut we also asked: what kind of move does the model make first when it continues? Each continuation was cut into sentences and labeled by a second labeler, an LLM judge (Claude Sonnet 5 with a fixed prompt; see Section 8 on why this matters), and the label of the first new node was recorded. Since every cut sits at the end of a block, we also recorded whether that first move opened a new block — whether the model "turned the page" where the original trace did.

Across the 20 cuts, the first move opened a new block in 73% of continuations and was a Planning move in most of them — a new heading, a plan for the next step. At 8 of the 20 cuts, more than 88% of continuations began with Planning. Where the original trace's next move was an Assumption — opening a new case such as "If Ball = $0.01," in the middle of an enumeration of cases — the continuations followed with an Assumption 12%, 54% and 96% of the time at the three cuts concerned. Averaged over the 20 cuts, a continuation reproduced the original trace's own next move 74% of the time.

### 6.2 Does the next move depend only on the current one?

The registered test asks whether the label of the next move depends only on the label of the last move before the cut. Under that reading, all cuts that end on a Reasoning node should show the same distribution of next moves, up to sampling noise. The test pools the cuts that share a last label, measures how far each cut's next-move distribution sits from the pooled one (a total-variation distance: half the sum of the absolute differences between two probability tables, 0 for identical tables, 1 for tables with nothing in common), and asks whether the spread is larger than random reassignment of the continuations among those cuts would produce.

| trace | cuts in the test | groups of cuts sharing a last label | spread observed (S) | spread expected if type-only (mean) | p |
|---|---|---|---|---|---|
| C-trace | 10 | 3 | 0.351 | 0.100 | 0.0001 |
| E-trace | 4 | 2 | 0.090 | 0.040 | 0.0033 |
| both | 17 | 4 | 0.329 | 0.091 | 0.0001 |

In the C-trace the observed spread is three and a half times what the type-only reading allows; in 10,000 random reassignments it was never reached. The E-trace gives the same direction on only four cuts. Cuts whose last label occurs only once cannot be tested and were left out (two in the C-trace, four in the E-trace). Relabeling the continuations of two cuts a second time — the check on the labeler's noise — left every row unchanged.

An example of what the test sees. Six C-trace cuts end on a Reasoning node. After three of them (cuts 3, 4 and 5, inside the enumeration of cases "If Ball = $0.05 / $0.01 / $0.55"), the continuations mostly open another case: Assumption 54%, 96% and 44%. After the other three (cuts 6, 10 and 11) they mostly start a new heading: Planning 12%, 88% and 56%, Assumption 16%, 0% and 0%. Same current label, different next moves — the difference lies in where the model is in its process, not in the kind of sentence it just wrote.

### 6.3 Against the average behaviour of similar traces

A second reference is the corpus table: over 44 of the model's traces on the same item, count for every kind of move which kind follows it. In that table, after a Reasoning node comes Planning 45% of the time and Conclusion 25%; after a Planning node, Reasoning 40% and Restatement 31%. The resampled next moves at our cuts sit far from these averages: pooled over the cuts ending in Reasoning, the continuations give Planning 47%, Assumption 26%, Reasoning 25% and Conclusion 0% — a total-variation distance of 0.49 from the corpus row. Per last label the distances run from 0.32 (Reflection) to 0.75 (Example); per cut from 0.22 to 0.97. The table of averages does not describe what the model does at any particular point.

### 6.4 Does history matter, and does order matter?

With the labels in hand we can also ask whether an earlier move changes the next one. After a Reasoning node, the next-move distribution differs by a total-variation distance of 0.57 to 0.66 depending on whether a Reflection, Knowledge or Example node occurred earlier in the prefix: with such a node earlier, the next move is Planning 70–81% of the time; without one, an Assumption 42–65% of the time. Order also shows: cuts whose last two moves were Planning then Restatement differ from those with Restatement then Planning by 0.31. In a single trace, though, "earlier in the prefix" and "later in the text" are the same thing — the enumeration of cases occupies blocks 2 to 8 of the C-trace — so these history effects cannot be separated from position effects with this design.

## 7. Inside the blocks that moved the answer

This section looks at the chains of moves inside the blocks with the largest shifts, and at how the two traces build their blocks. A chain is written as the sequence of node labels, abbreviated Pl (Planning), Rs (Restatement), Re (Reasoning), Kn (Knowledge), As (Assumption), Rf (Reflection), Ex (Example), Co (Conclusion), with the number of sentences in parentheses when it is more than one; a sentence doing two things at once is written in brackets, such as [Re+Rf].

### 7.1 The first blocks: two ways to begin, two answers to end with

The C-trace's first block (eight sentences, shift +0.48 toward C) has the chain Pl(3) → Rs(5): "Here's a thinking process that leads to the suggested answer:", "1.", "Analyze the Request:", then the question, the options and the task restated in three bold inline items ("Problem: …", "Options: …", "Task: …").

The E-trace's first block (twelve sentences, shift +0.24 toward E) has the chain Pl(4) → Rs(3) → Pl → Rs → Pl → Rs(2): "Here's a thinking process:", "1.", "Analyze the User Input:", then three sub-headings each followed by its content — "- Question:" and the question, "- Options:" and the options, "- Task:" and the task.

The two blocks restate the same material; they differ in shape — inline items against sub-headings — and in wording ("Analyze the Request" against "Analyze the User Input"). Now the striking part. When the model starts from nothing (cut-0), 20 of its 25 continuations open with exactly the E-trace's chain, Pl(4) → Rs(3) → Pl → Rs → Pl → Rs(2), and 18 of the 25 end at E. The C-trace's opening shape is the rare one — only 2 of the 25 openings resemble it — and from the end of that opening 16 of 25 continuations end at C. In this run, the format of the first eight sentences already tilts the outcome. What we cannot tell from two traces is whether the format causes the tilt or merely reveals an orientation the model has already taken.

### 7.2 Block 6 of the C-trace: recognizing the riddle (+0.40)

Chain Pl(2) → Kn(2) → Re(2): the heading "4. Identify the Nature of the Question:", then two Knowledge sentences — "This is a classic cognitive reflection test question (often attributed to Keith Stanovich / Shane Frederick)" and "The Trap: Most people intuitively answer $0.10 (Ball) and $1.00 (Bat)" — then "Why?" and "Because $1.00 + $0.10 = $1.10." Recognizing the famous riddle and its standard trap raised the chance of C from 28% to 68%: knowing that the intended answer is $0.05 pulls toward "not enough information, but most likely $0.05". The one-sentence block that follows, "But wait, the problem usually adds the constraint 'The bat costs $1.00 more than the ball'", takes some of it back (−0.20).

### 7.3 Block 9 of the C-trace: evaluating the options (+0.56)

This is the block that contains s*, the sentence the submitted study had singled out. It is 21 sentences long with the chain Pl(3) → Re(3) → Pl → Re(2) → [Re+Rf] → Pl → Rf → Re(2) → Pl → Rf → Pl → [Re+Kn] → Re → Pl → Rf. Its heading is "5. Evaluate the Options against the Textual Analysis:", and its rhythm is a series of small plans and verdicts: a local plan naming an option — "(A) It is $0.05:" — followed by reasoning about it ("This assumes the standard version of the riddle…", "It is not necessarily $0.05") and a reflective verdict; then "(B) It is probably $0.05:" with a reading of the word "probably" ("'Probably' implies probability. Unless there's a distribution of prices given, we can't assign probability."); and so on through the options. Before this block 10 of 25 continuations ended at C; after it, 24 of 25. In terms of the labels, the block is the first place where the trace stops analysing the problem and starts scoring the answers.

What do the model's own continuations do at this point? Starting from the end of block 8, all 24 labeled continuations open a new Planning block, as the original does — but the pages they write are all different: chains such as Pl(2) → Re(13), Pl(3) → Rs(6), Pl(3) → Co(2) → Kn → Pl → Kn(2); no two share a shape. Yet 24 of 25 end at C. The turn of the page is fixed; its content is not; and the answer no longer depends on the content.

### 7.4 The E-trace's dip and recovery

Block 2 of the E-trace (chain Pl → Re → [Re+As]) is three sentences: "Let's verify:", "Ball = x,", "Bat = x + 1.00" — the last one both a calculation and an assumption, because it writes the classic constraint that the question does not contain. After it, 10 of 25 continuations end at C. Block 3 is the single combined sentence "(Wait, the classic problem says 'The bat costs $1.00 more than the ball.' But this problem…" — a doubt marker plus a comparison of the text with the classic version — and after it 20 of 25 continuations end at E again. Two sentences reminding the model of the riddle it knows cost it a third of its E-answers; one sentence noticing the difference restores them.

### 7.5 Do the two traces think in the same shapes?

Yes in grammar, no in mix. Both traces build a block the same way: a numbered heading (Planning) and then either a restatement or a stretch of reasoning. Of the C-trace's 47 blocks, 19 open with Planning followed by Reasoning and 14 with Planning followed by Restatement; of the E-trace's 38 blocks, 8 and 12. Both average about four nodes per block (4.1 and 3.9). The corpus table of 44 traces shows the same two openings as the most common (after Planning: Reasoning 40%, Restatement 31%).

The difference is what the blocks are spent on. The C-trace reasons: it contains four blocks that open directly with a case ("If Ball = $0.05," — Assumption then Reasoning), 162 Reasoning sentences out of 375, and long stretches of enumeration and option evaluation. The E-trace restates and concludes: 57 Restatement sentences out of 254, and among its block openings Planning → Knowledge, Planning → Conclusion and Planning → Reflection (5, 5 and 3 blocks) that the C-trace almost never uses. The E-trace also settles sooner: its answer is at 96% after four blocks (41 sentences), the C-trace's only after ten (78 sentences). Same building blocks, different buildings — one that works the problem through, one that recognizes it and moves to writing the reply.

## 8. Three kinds of thought and the order they come in

Kian singled out three kinds of sentence as the ones most likely to carry the decision. Algebra: any sentence that sets up or works the equations — "Bat + Ball = 1.10", "If Ball = $0.05, then Bat = $1.05", "any price below $0.55 works" (every leaf of the scheme ending in "algebra"). Famous-problem recognition: a sentence stating that this is the well-known cognitive reflection test riddle and what its standard answer is (the leaf "famous problem (CRT)"). Hedge-word analysis: a sentence weighing a hedge such as "probably" or "most likely" in the options — "'Probably' implies probability; unless there is a distribution of prices, we cannot assign one" (the leaf "hedge word analysis"). This section asks whether the order in which these three first appear predicts the answer. In the notation, the question about the first two reads

P(final answer | ⟨ algebra --> famous problem ⟩)  against  P(final answer | ⟨ famous problem --> algebra ⟩),

the fraction of continuations ending at C or E among those whose text does the algebra first and recognizes the riddle later, against the fraction among those that recognize first and compute later.

### 8.1 How the order was read

For each labeled continuation the whole text the model saw and wrote — the prefix with its reviewed labels, then the continuation with the judge's labels — was scanned for the first sentence of each kind. The pattern ⟨ X --> Y ⟩ holds when the first X comes before the first Y; a kind that never appears is left out of the pattern. Two views are given: all 523 labeled continuations, where most of the order is already fixed by the prefix — the C-trace does its algebra at sentence 10 and recognizes the riddle at sentence 38, the E-trace recognizes the riddle at sentence 14 and does its algebra at sentence 17 — and the 25 continuations from cut-0, where the model chose the order itself.

### 8.2 Algebra before or after recognizing the riddle

This is the pair that separates the answers. Over all 523 continuations:

- P(C | ⟨ algebra --> famous problem ⟩) = 0.58 and P(E | ⟨ algebra --> famous problem ⟩) = 0.19, over 293 continuations;
- P(C | ⟨ famous problem --> algebra ⟩) = 0.16 and P(E | ⟨ famous problem --> algebra ⟩) = 0.81, over 225 continuations.

In words: a text that first works the numbers and then remembers "this is the famous riddle" tends to land on "the intended answer is $0.05"; a text that first remembers the riddle and then works the numbers tends to land on "the question is not well posed". Most of this is the two traces speaking — the C-trace's prefixes carry ⟨ algebra --> famous problem ⟩, the E-trace's ⟨ famous problem --> algebra ⟩ — so the 25 cut-0 continuations are the honest test, and they point the same way: 19 of them chose ⟨ famous problem --> algebra ⟩ and 16 of those 19 ended at E, P(E | ⟨ famous problem --> algebra ⟩, cut-0) = 0.84; 4 chose ⟨ algebra --> famous problem ⟩ and 2 of those 4 ended at C, none at E. Four continuations is too few to build on; the direction is what the run shows, and the pattern's origin — whether doing the algebra first causes the C-answer or merely accompanies a way of reading that also produces it — is a question for an intervention (Section 12), not for this run.

### 8.3 Hedge words come last, and mark the C-leaning texts

Hedge-word analysis almost never comes early: ⟨ famous problem --> hedge word ⟩ holds in 341 continuations and ⟨ hedge word --> famous problem ⟩ in only 3; ⟨ algebra --> hedge word ⟩ in 345 and ⟨ hedge word --> algebra ⟩ in 1. So the comparison Kian asked for,

P(final answer | ⟨ famous problem --> hedge word ⟩)  against  P(final answer | ⟨ hedge word --> famous problem ⟩),

has almost no second term to compare with: the model weighs the hedge words after it has recognized the riddle and after it has done the algebra, essentially always. What the presence of the hedge-word analysis does mark is the answer: P(C | hedge word present) = 0.49 and P(E | hedge word present) = 0.33 over 299 continuations, against P(C | hedge word absent) = 0.21 and P(E | hedge word absent) = 0.72 over 224. The reason is visible in the traces: weighing "probably" and "most likely" is what a text does when it is scoring options B and C against each other, which the C-trace does at length in its option-evaluation block and the E-trace does briefly. Among the cut-0 continuations, the 7 that analysed a hedge word ended at C 29% and E 43% of the time; the 16 that did not, at E 88%.

### 8.4 All three together

Of the six possible orders of the three kinds, the texts used essentially two:

- P(C | ⟨ algebra --> famous problem --> hedge word ⟩) = 0.63 and P(E | …) = 0.15, over 248 continuations, 236 of them from C-trace cuts;
- P(C | ⟨ famous problem --> algebra ⟩ with or without hedge words after) = 0.16 and P(E | …) = 0.81, over 225 continuations, 197 from E-trace cuts.

The remaining orders together account for 50 continuations. Among the cut-0 continuations: ⟨ famous problem --> algebra ⟩ 14 (93% E), ⟨ famous problem --> algebra --> hedge word ⟩ 5 (60% E, none C), ⟨ algebra --> famous problem --> hedge word ⟩ 2 (both C), ⟨ algebra --> famous problem ⟩ 2, algebra alone 2. The order of the first two kinds carries the pattern; the hedge words arrive afterwards, in the texts that then go on to weigh the options.

### 8.5 The company each kind keeps

The neighbours of these sentences, from the judge's labels of the continuations: the recognition of the riddle is introduced by a plan in most cases (a heading or a sub-item, 272 of 496 occurrences, or a verification announcement, 67) and is followed by another plan item (134) or by a comparison of the given text with the classic version (86) — the model states what the riddle is, then compares. The hedge-word analysis is introduced by a restatement of the option text (119 of 299) — the model quotes "(B) It is probably $0.05" and then weighs "probably" — and is followed by a verification announcement (62), a new heading (46) or a verdict on the step (41). In the two source traces the recognition sits inside the block that raised the C-trace's P(C | cut(B_m)) from 0.28 to 0.68 (block 6, "Identify the Nature of the Question") and inside the E-trace's block 1, which lowered its P(E | cut(B_m)) from 0.96 to 0.80; the hedge-word analysis sits inside the C-trace's decisive block 9 and the E-trace's block 5.

## 9. Next to what others have found

Searched on 2026-09-18; every identifier below is to be verified against the paper itself before it is cited.

- Order in the input. Chen, Chi, Wang and Zhou, "Premise Order Matters in Reasoning with Large Language Models" (ICML 2024; arXiv 2402.08939), show that language models are brittle to the order of the premises in the prompt and do best when it matches the order of the proof; shuffling costs more than 30 points of accuracy. That is order in what the model is given, measured as accuracy. Section 8 is about order in what the model writes, measured as which answer it chooses.
- Order in a finished trace. "Rethinking Dense Sequential Chains" (arXiv 2605.07307, May 2026) shuffles the lines of a completed reasoning chain and finds the extracted answer changes by less than half a point. Read together with Section 8, this locates the order effect: if line order barely matters when a finished trace is read out, an order effect must act during generation — what the model writes after recognizing the riddle differs from what it writes after doing the algebra — which is what the resampling measures.
- Two sources of the answer. Wang et al., "Reasoning or Retrieval? A Study of Answer Attribution on Large Reasoning Models" (ICLR 2026; arXiv 2509.24156), show that final answers emerge from two competing mechanisms, deliberate chain-of-thought reasoning and direct retrieval from memory, whose dominance depends on domain, scale and fine-tuning; they perturb each mechanism separately. Section 8.2 is the temporal form of that competition — which mechanism appears first in the text predicts which one wins — which their design does not examine. Related is Google's "Thinking to Recall" (COLM 2026), on reasoning tokens priming factual recall.
- Where the answer is decided. "Beyond the Commitment Boundary" (arXiv 2606.13603) finds that commitment typically occurs at a single pivotal step around the midpoint of the chain; the C-trace here shows two steps of comparable size, one at the very start and one at the option evaluation, with reversals between them. Thought Anchors (arXiv 2506.19143) and Thought Branches (arXiv 2510.27484) attribute influence to individual sentences by resampling; neither types the moves or asks about the order of types.
- A methodological caution. "It's the Problem, Not the Path" (arXiv 2609.03436, September 2026) argues that claims about reasoning trajectories need a counterfactual control at the level of the claim. The mediation and transition results of Sections 4–6 have that control — the prefix is held fixed and only the continuation varies — but the order analysis of Section 8 inherits its order from the prefix at every cut but cut-0 and is observational; the intervention that would give it a control is stated in Section 12.
- The item. Hagendorff and colleagues, "Thinking Fast and Slow in Large Language Models" (arXiv 2212.05206; Nature Computational Science 2023), established that language models give the intuitive answers to cognitive-reflection items such as bat-and-ball and that chain-of-thought removes them, on the classic item; this study uses the item with its constraint deleted, where the question is not whether the model computes but which reading of an underdetermined question it adopts.

What none of these does, as far as the search shows: type the moves of a model's own trace, resample from typed block boundaries, and ask how the order of kinds of thought relates to the answer. That is the contribution Section 8 opens, and it is stated here as an observation awaiting its intervention.

## 10. How each reading could be wrong

1. Twenty-five continuations per cut is a small sample: the standard error of a proportion near one half is 0.10, so changes smaller than about 0.25 cannot be told from noise. The C-trace's wandering between blocks 1 and 8 should not be read block by block; only the shifts whose intervals exclude zero are individually trustworthy.
2. The unanswered continuations. Counting a "?" as "not C" is the registered rule; if the long continuations that hit the cap were mostly heading to one answer, the plateau before block 9 is mis-measured. The two large steps do not depend on this (Section 4.3).
3. The labeler. Every statement in Sections 6 and 7 about what the continuations do rests on labels produced by an LLM judge, Claude Sonnet 5 with prompt v3 and adaptive thinking at low effort. Against Kian's reviewed labels of the two traces it agrees on the kind of move (Level 1) with a kappa of 0.73–0.80; on this run's own continuations, relabeling twice gave kappa 0.78 and 0.83, and the first-move distributions came out identical. A different judge could move the transition numbers; the judge is a named source of uncertainty in this project, and its prompt is part of the record.
4. The blocks come from the reviewed labels of two traces. A different labeling would cut the text in different places.
5. One item, one model, two traces. Nothing here transfers by itself; the first-block observation in particular (Section 7.1) rests on 25 cut-0 continuations.
6. The order analysis of Section 8 is observational and, at every cut but cut-0, inherits its order from the prefix; only an intervention that changes the order can say whether it drives the answer (Section 9's methodological caution applies to it).
7. The blocks after the stopping point (C-trace blocks 12–46, E-trace 8–37) were not sampled; that they move nothing is an assumption of the design, supported by the 25-of-25 readings at the last sampled cuts and by the earlier study's finding that the answer never fell after s*.
8. The first-block effect may partly be an effect of format rather than content: a prefix written in one trace's heading style may commit the model to that trace's way of proceeding.

## 11. Budget and bookkeeping (skippable)

Sampling on DeepInfra (Qwen 3.6-27B, raw completions): 625 continuations, $13.06 against a ceiling of $45 (no-think baseline $0.87, cut-0 $0.39, C-trace $10.20, E-trace $1.58). Labeling on the Claude API (Sonnet 5, batch mode): $66.84 against a ceiling of $80 — six waves $63.02 including the automatic retries of continuations whose reply did not parse, plus $3.82 for the second labeling of two cuts. Two continuations of 525 remained unlabeled after three attempts and are excluded from Sections 6–7 only. The run took 17:59–22:27 on 2026-09-17 for the sampling and 22:29–02:53 for the labeling. No departure from the registered design occurred on the sampling side; the judge side logged the two unlabeled continuations. All files of the run are in the repository (commits 5ea708d and 7577ab3; the largest file is 19.7 MB). Project spending to date is about $148 of the $160 budget.

## 12. What follows

- Kian re-derives P̂, Δ and the gaps from the raw continuations (Appendix A) and confirms this document.
- The order finding of Section 8.2 is the natural first target for paper two's intervention: build two prefixes that differ only in the order of the algebra and the recognition of the riddle, resample both, and compare P(final answer | ⟨ algebra --> famous problem ⟩) with P(final answer | ⟨ famous problem --> algebra ⟩) under a control the observation of Section 8 lacks.
- Stage two, if taken: node-level cuts inside the blocks that carried the movement. Because the two largest C-trace shifts cannot be ranked, the registered near-tie rule points at both block 0 and block 9 — about eleven node-level cuts, roughly $9 of sampling and $30 of labeling.
- The paper: Sections 2–10 are its results, related work and limitations in draft; the judge statement (action summary v6, Section 2d) and the judge prompt go into its appendix.

## Appendix A — re-deriving the headline numbers

From runs/experiments/resample_blocks_2026-09-17_1759/continuations.jsonl: each line is one continuation with `condition` (nothink, cut0 or cut), `trace_arm` (c004 or e036), `block` (the cut's m) and `letters` (a list; a single letter is the answer, anything else counts as "?"). For each trace and m, P̂ = (continuations whose letter is the trace's own answer) / 25; Δ_m = P̂_m − P̂_{m−1}, with Δ_0 measured against cut-0's P̂ of the same letter; the gap = the difference between the two largest Δ_m. The 95% interval of a proportion p from n samples (Wilson): centre (p + z²/2n)/(1 + z²/n), half-width z·√(p(1−p)/n + z²/4n²)/(1 + z²/n), with z = 1.96.

## Changelog

- 2026-09-18 v1 (= chat4 of the chat begun 2026-09-15 for this document; confirmed by Kian 2026-09-18) — First results document of stage one, written for a reader without the notation: the question in plain words; the two baselines; the mediation tables of both traces explained; what follows a cut and the type-only test; the chains inside the large-shift blocks and the comparison of the two traces' shapes; the order of algebra, famous-problem recognition and hedge-word analysis in the pattern notation P(final answer | ⟨ X --> Y ⟩); the literature found on 2026-09-18 (to be verified before citing); how each reading could be wrong; budget in one skippable section; what follows. Built through four chat drafts on 2026-09-18.
