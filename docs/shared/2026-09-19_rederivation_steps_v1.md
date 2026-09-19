# Re-deriving the headline numbers of stage one — detailed steps — 2026-09-19 (chat1)

File: 2026-09-19_rederivation_steps_v1.md (local version 1 = chat1 of the chat of 2026-09-19). It expands Appendix A of 2026-09-18_stage1_results_v1.md and becomes Appendix A of results v2 once confirmed. Claude wrote the procedure; Kian does the re-derivation with his own code, and Claude wrote no code for it. The formulas are those of the registered analysis (scripts/stats_utils.py at commit 5359817), restated so that they can be implemented without reading that code.

## 0. Overview

What is re-derived. Everything comes from one file, runs/experiments/resample_blocks_2026-09-17_1759/continuations.jsonl. The quantities are those of pre-registration 7.2: for the two baselines the answer counts and P̂; for each trace the counts per cut, P̂_m with its Wilson interval, Δ_m with its Newcombe interval, the stopping cut M, the block with the largest Δ_m, and the gap between the two largest Δ_m with its bootstrap interval. None of it depends on the judge.

Two passes. Pass A takes the file's `letters` field as given and re-derives everything downstream of it; it checks the arithmetic of the registered analysis and the counts in pcut.csv. Pass B checks `letters` itself against the text of each continuation; it checks the scorer. Pass B is needed because `letters` is the scorer's output, so an error in the scorer passes through Pass A unseen. Claude's audit of 2026-09-19 found such an error (scorer_audit_chat1.md): Pass A should reproduce the registered numbers, and Pass B is where they change.

Order of work. Steps (1/9) to (7/9) are Pass A, step (8/9) is Pass B, step (9/9) is what to bring back. Compare with stage1_summary.md only after your own tables exist.

## 1. Pass A — from the `letters` field

### (1/9) The file and its shape

The repository at commit 5359817; the file has 625 lines, one JSON object per line, UTF-8.

Fields used: `id`, `condition`, `trace_arm`, `block`, `seq`, `letters`, `think_closed`, `finish`, `cont_text`, `prompt`, and `usage.prompt_tokens`. The field `answer` restates `letters` and is left alone, so that nothing of the scorer's summary enters your numbers by the back door.

The group key is the triple (`condition`, `trace_arm`, `block`). There are 22 groups: (`nothink`, `shared`, null) with 100 records; (`cut0`, `shared`, null) with 25; (`cut`, `c004`, m) for m = 0 … 11 with 25 each; (`cut`, `e036`, m) for m = 0 … 7 with 25 each. 100 + 25 + 300 + 200 = 625. Appendix A of results v1 is incomplete on this point: it names only c004 and e036 as values of `trace_arm` and does not say that the two baselines carry `trace_arm` = `shared` and `block` = null.

Checks worth making before any counting: the 625 ids are unique; inside each group `seq` runs from 0 to n − 1 without repeats; inside each group every `prompt` is the same string, since all continuations of a cut share one prefix.

### (2/9) The answer of one continuation, by the registered rule

`letters` is a list. Exactly one element: that letter is the answer. No element, or two or more: the answer is "?", unresolved.

A "?" is never dropped. The denominator is always n, which is 25 for cut-0 and for every cut and 100 for the no-think baseline (pre-registration 3.6 and 3.7).

The trace's own answer a_T is C for c004 and E for e036. For the two baselines both P̂(C) and P̂(E) are reported.

Example: rb_c004_B01_006 has `letters` = ["D", "E"]. Its answer is "?", and it still counts among the 25 of cut C-B01.

### (3/9) Counts

For each of the 22 groups count the answers A, B, C, D, E, F and "?". The seven counts sum to n. As an example of the form, the row of C-B00 reads A 1, B 1, C 16, D 0, E 2, F 0, "?" 5.

When your table exists, compare it with pcut.csv (columns `count_A` to `count_F` and `count_unresolved`; its `count_other` is the number of single letters other than C and E). This comparison is a real test and not a formality: the registered tables took their counts from pcut.csv, which the sampling script wrote at run time, and only the bootstrap read continuations.jsonl. Counting from the records therefore checks pcut.csv as well.

### (4/9) P̂ and the Wilson interval

P̂ = k / n, with k the count of the letter in question.

The Wilson 95% interval uses z = 1.959964 (the value in the code; results v1 prints 1.96, and the difference shows only in the fourth decimal). With p = k / n:

- centre = (p + z² / 2n) / (1 + z² / n)
- half-width = z · √( p(1 − p)/n + z² / 4n² ) / (1 + z² / n)
- interval = [centre − half-width, centre + half-width], clipped to [0, 1].

Worked example, k = 16 and n = 25: p = 0.64; z² = 3.841459; 1 + z²/n = 1.153658; centre = 0.621353; half-width = 0.176168; interval [0.4452, 0.7975]. Second example, k = 25 and n = 25: centre 0.933404, half-width 0.066596, interval [0.8668, 1.0000]; this is why a P̂ of 1 is never reported bare. Third example for the baseline, k = 49 and n = 100: [0.3942, 0.5865].

Baselines: the no-think condition with n = 100 (P̂(C), P̂(E), and P̂(A) since A occurs) and cut-0 with n = 25.

### (5/9) Δ_m and the Newcombe interval

Δ_0 = P̂_0 − P̂(a_T | cut-0), where the cut-0 value is that of the same letter: C for the C-trace, E for the E-trace. For m ≥ 1, Δ_m = P̂_m − P̂_{m−1}. The shifts are signed and no absolute value is taken. A block whose Δ_m is exactly 0 is called trivial.

The interval is Newcombe's method 10, the hybrid score interval for the difference of two independent proportions. Let p1 = P̂_m with Wilson interval [l1, u1], p2 = P̂_{m−1} with Wilson interval [l2, u2], and d = p1 − p2. Then

- lower = d − √( (p1 − l1)² + (u2 − p2)² )
- upper = d + √( (u1 − p1)² + (p2 − l2)² ).

Worked example, C-B00 against cut-0: p1 = 16/25 = 0.64 with [0.4452, 0.7975]; p2 = 4/25 = 0.16 with [0.0640, 0.3465]; d = 0.48; lower = 0.48 − √(0.037953 + 0.034796) = 0.2103; upper = 0.48 + √(0.024813 + 0.009209) = 0.6645.

The formula assumes two independent samples, which holds here: every cut is its own sample of 25.

### (6/9) The stopping cut M

M is the first m at which all n continuations end in a_T, that is, k_m = n. Three checks: no cut before M has k = n; the file holds no cut after M for that trace; every cut from 0 to M is present, since the run was strictly sequential.

### (7/9) The largest shift, the gap, and the bootstrap interval of the gap

Rank the Δ_m of a trace from largest to smallest, signed: Δ_(1), Δ_(2), and so on. The top block is the m of Δ_(1). The gap is Δ_(1) − Δ_(2).

The bootstrap of pre-registration 5.3. One draw: resample, with replacement, n answers from the n answers of cut-0, and independently n answers from the n answers of each sampled cut of the trace; recompute every P̂ and every Δ, with Δ_0 against the resampled cut-0; take the largest Δ of that draw minus its second largest, whichever blocks they fall in. Make 10,000 draws. The interval runs from the 2.5th to the 97.5th percentile of the 10,000 gaps.

What agreement means here. Your random numbers differ from the registered ones (numpy's default generator with seed 0), so the draws differ. But every P̂ is a multiple of 0.04, hence every gap is too, and the two percentiles land on multiples of 0.04. The same two end points, or one step of 0.04 at one end, is agreement; more than that is a discrepancy.

Two properties of this statistic to keep in mind (audit item A3 of the STATE). It is non-negative by construction, so its interval can touch zero and can never cross it. The statistic that can cross zero is the signed difference between two named blocks, for example Δ(C-B09) − Δ(C-B00) with the four cuts involved resampled; it is exploratory and worth computing next to the registered one.

Optional, from the same data: the total movement P̂_M − P̂(a_T | cut-0); the share of it carried by the top one, two and three blocks, which is the sum of the k largest Δ divided by the total movement and can exceed 1 because negative shifts exist; the number of top-ranked blocks needed to reach half of the total; the number of trivial blocks; and Tk(B_m) = `usage.prompt_tokens` of cut m minus that of cut m − 1, with Tk(B_0) measured against cut-0. The token count is the same in all 25 records of a cut.

## 2. Pass B — the letters against the text

### (8/9) Checking the scorer

(8a/9) The text that holds the answer. If `think_closed` is true, the reply is the part of `cont_text` after the first `</think>`, and the answer is in the reply. If `think_closed` is false, the continuation hit the 16,000-token cap inside its thinking (`finish` = "length") and wrote no reply at all; the registered rule then scans the whole thinking text.

(8b/9) Your own reading rule, written down before you look at any disagreement. The item asks for a last line of the form "Answer: X". The registered scorer looks for "Answer:" followed directly by a letter, without regard to case, and takes the last such match. Two things to settle in your own rule: which forms of the answer line count ("Answer: C", "Answer: (C)", "**Answer:** C", "Answer: The question is not well posed"), and what an unfinished continuation is: always "?", or whatever answer line its thinking last drafted.

(8c/9) Apply your rule to all 625 records, compare with `letters`, and list every disagreement. Read each disagreeing record yourself. For a finished continuation the last 300 characters of the reply are usually enough; for an unfinished one, read the sentence around the last "Answer:".

(8d/9) Where Claude's audit says to look first: the 3 finished continuations with empty `letters` although `finish` = "stop"; the 33 unfinished continuations that nevertheless carry a single letter; the 9 unfinished ones with `letters` = ["D", "E"]. None of these occurs in the E-trace cuts or in the no-think baseline, where every continuation finished. scorer_audit_chat1.md lists each record with the matched text.

(8e/9) Redo steps (3/9) to (7/9) on your own reading. The two sets of numbers side by side are the result of the re-derivation.

## 3. What to bring back

### (9/9) The report

- The 22 count rows under `letters`, and the 22 under your own reading.
- For each trace and under both readings: M, the three largest Δ_m with their blocks, the gap and its interval.
- The list of records where your reading differs from `letters`, with your reading of each.
- Your decision on how the paper scores the answers (pending decision P6 of the STATE).

Claude then compares your numbers with stage1_summary.md and the mediation tables of the run folder, records the outcome in the next STATE, and drafts results v2.

## References for the two intervals (to be verified against the papers before they are cited)

- Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. Journal of the American Statistical Association 22(158), 209–212.
- Newcombe, R. G. (1998). Interval estimation for the difference between independent proportions: comparison of eleven methods. Statistics in Medicine 17(8), 873–890. The interval used is method 10.

## Changelog

- 2026-09-19 v1 (= chat1 of 2026-09-19) — First version: Appendix A of results v1 expanded into nine steps in two passes, with worked examples for both intervals, the bootstrap of the gap, the agreement criterion, and the scorer check added after Claude's audit of the same day.
