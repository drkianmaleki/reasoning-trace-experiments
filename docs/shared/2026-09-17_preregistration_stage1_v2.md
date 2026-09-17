# Pre-registration — stage one of the block-boundary resampling run — reasoning-trace-experiments — 2026-09-17 v2

File: 2026-09-17_preregistration_stage1_v2.md (local version 2 = chat version 2 of the chat begun 2026-09-15 for this document). Supersedes 2026-09-17_preregistration_stage1_v1.md (registered in commit b5f4a5a, 2026-09-17 14:52; → archive/). Claude drafts, Kian confirms and owns the design. Status: CONFIRMED by Kian on 2026-09-17, before any registered sampling. v2 makes three pre-run amendments found by the smoke tests (changelog); no analysis or hypothesis changed. The commit that adds this file is the registration timestamp of the amended design. The run is executed exactly as written here; every departure is recorded in the run folder and in the STATE file, and reported. Companion documents: 2026-09-17_pipeline_v2.md (the machinery), 2026-09-17_labeling_scheme_v6.md (labels, blocks, notation 0d/0e), 2026-09-17_source_traces_labeled_v4.md (the reviewed labels and the blocks that define the cuts), 2026-09-17_action_summary_v6.md (design, motivation, the judge as a named uncertainty).

## 1. What is being tested

1. Object. Two reasoning traces of Qwen 3.6-27B on one item — the bat-and-ball problem with "$1.00 more" deleted, six options (A)–(F) — the C-trace (c004, final answer C) and the E-trace (e036, final answer E), typed sentence by sentence with the labeling scheme and cut into blocks (47 and 38) by its opener rules.
2. Two quantities at every block-end cut, from n resampled continuations of the prefix: the answer distribution P(answer | cut(B_m)) — the mediation tree — and the Level 1 label of the first new node after the cut, P(next = Y | cut(B_m)) — the transition tree. Definitions: scheme Sections 0d and 0e.
3. Questions, in the order they are answered. (Q1, descriptive) How does the probability of the trace's own answer move across its blocks, and how concentrated is the movement (which blocks, how many tokens)? (Q2, a null to be tested) Does the label of the next node depend only on the label of the last node before the cut — the Markov, type-only reading — or on more of the prefix? (Q3, descriptive) How does the resampled transition structure compare with the corpus-counted matrix P_corpus and with the source trace's own path P_source?
4. Hypotheses stated by Kian before the run (scheme 0e; summary Section 2): the whole process matters, not only the current block type — so the type-only null of Q2 is expected to fail, and the movement of Q1 is expected to be spread over several blocks rather than one. Both are hypotheses under test; neither is assumed by the analysis.
5. Not tested here: stage two (node-level cuts inside the top block), interventions of any kind, transfer to other items or models.

## 2. Data and provenance

1. Source traces: archive/decided-mid-thought/runs/sweep_items_batball_2026-08-19_1623.jsonl, condition eval0_multi0, sample 2 (c004) and sample 40 (e036); field `trace`. Sentence spans: scripts/s0_split.py (gate runs/tests/t2_split_2026-09-16_2224, PASS 8/8); labels and blocks: listing v4, derived with scripts/derivation.py under rules R1–R4 (gate runs/tests/t4d_r4_2026-09-17_1324: 47/193 and 38/147 exact).
2. Item prompt and prefill template: verbatim in action summary v6 Section 4 and pipeline v2 Section 5 (`<|im_start|>user\n{p}<|im_end|>\n<|im_start|>assistant\n<think>\n{pre}`); the exact prompt string is stored in every record.
3. Model and endpoint: `Qwen/Qwen3.6-27B` on DeepInfra raw completions (base URL https://api.deepinfra.com/v1/openai, endpoint /completions); the slug is re-verified with a one-token call at run start (test t0 pattern); temperature 1.0, max_tokens 16000, 4 workers, timeout 600 s, stop sequence `<|im_end|>` — the archived study's settings (v1 wrote "no stop sequence" in error; the archived script sent the stop and no archived completion contains the marker).
4. Reference matrices. P_corpus: runs/experiments/judge_sweep44_2026-09-17_1334/pcorpus_L1.csv (44 traces of the same condition labeled by the judge; 8,517 node pairs; committed in 5e87210), used as the row-normalized 8×8 matrix. P_source: psource_c004.csv and psource_e036.csv in runs/experiments/judge_archived500_2026-09-17_1334 (the source's own next label after every block-end cut under R4).

## 3. The sampled conditions (in this order; one shared no-think baseline, one shared cut-0, then the two traces)

1. No-think baseline, n_0 = 100 samples: the item prompt with the prefill `<think>\n\n</think>\n\n` (pipeline v2, Section 5 item 8); max_tokens 8000 (v1 said 2000; in the ten-sample smoke test seven replies were cut off before their answer line, mean 1,664 tokens at the cap, because the model writes its explanation before "Answer:"). The smoke test showed no reopened `<think>`. A reply still without a letter at 8000 tokens is "?".
2. cut-0, n = 25: the empty prefix `<think>\n`.
3. C-trace, cuts in order m = 0, 1, …: cut(B_m) = the raw text from character 0 to the end of the last sentence of block B_m (listing v4, R4 blocks). The 46 block-end sentence indices, in order: s7, s12, s14, s22, s30, s35, s41, s42, s57, s78, s97, s106, s113, s115, s119, s131, s136, s143, s147, s159, s165, s170, s186, s189, s192, s198, s201, s208, s215, s226, s228, s253, s262, s265, s276, s287, s301, s324, s329, s339, s341, s343, s351, s355, s361, s373 (cut(B_46) is the whole trace and is not sampled).
4. E-trace, cuts in order: the 37 block-end indices s11, s15, s18, s19, s41, s52, s70, s74, s76, s92, s95, s99, s104, s116, s119, s133, s143, s151, s153, s165, s167, s173, s176, s178, s181, s186, s192, s198, s203, s206, s212, s214, s219, s227, s244, s246, s250.
5. n = 25 continuations per cut (Kian, 2026-09-17), sampled in parallel within a cut; cuts strictly sequential within a trace; the two traces may run in parallel.
6. Stopping rule (scheme 0e; Kian): after the n continuations of cut(B_m) are scored, P̂_m = (number ending in a_T) / n with "?" in the denominator; if P̂_m = 1, M := m and no later cut of that trace is sampled; blocks with m > M are trivial by this assumption, not by measurement. Binomial facts to be quoted with the result: at n = 25, P̂ = 1 bounds the true P at 0.887 (one-sided 95%) and occurs with probability 0.28 when the true P is 0.95.
7. Scoring: the archived `extract_letters` on the reply after `</think>` (or on the whole text if the tag is absent); one letter → that answer; no letter or several → "?", kept in the denominator. a_T = C for the C-trace, E for the E-trace.
8. Tk(B_m) = prompt_tokens of cut(B_m) − prompt_tokens of cut(B_{m−1}) from the API's usage (Tk(B_0) against cut-0); Tk(trace) from the sweep record's reasoning_tokens (4,740 C; 2,890 E).

## 4. The judge on the continuations (pipeline v2, decision 12; step 8/9)

1. Every sampled continuation is split by s0_split (thinking part only, decision 19) and labeled in batch mode by Claude Sonnet 5 with prompt v3 (prompts/judge_prompt_v3.md, sha256 e999f7081d5a285c4db1dcb4fb55f9eb5291b1ba536f770d1ad53a815e43f51a), adaptive thinking at low effort, the prefix shown with its reviewed labels, one retry plus one formatted retry; the derivation with R1–R4 gives the first new node after the cut and the continuation's block sequence. Continuations that still fail to parse are reported as unlabeled and excluded from the transition quantities only.
2. Judge noise on continuations: the continuations of two cuts — the cut with the largest Δ_m of the C-trace and cut(E-B06) — are labeled a second time (about 50 documents); the two labelings' agreement (Level 1 kappa, first-node agreement) is reported next to every transition result as the label noise floor. Reference floor from the source traces: Level 1 kappa 0.90 (pipeline v2, decision 17).
3. The judge configuration, prompt version and both noise floors accompany every judge-dependent number; the mediation quantities (Section 5) do not depend on the judge.

## 5. Analysis of the mediation tree (Q1) — descriptive, no thresholds

1. For the baselines and every sampled cut: the counts of every answer letter and of "?", P̂ of a_T, and a Wilson 95% interval; P̂(C) and P̂(E) reported for both traces.
2. Δ_m = P̂_m − P̂_{m−1} (Δ_0 against cut-0), signed, with a Newcombe 95% interval for the difference of two proportions.
3. The block B_top with the largest Δ_m; Tk(B_top) and Tk(trace); the gap Δ_(1) − Δ_(2) between the two largest Δ_m with a 95% bootstrap interval (resampling continuations within each cut, 10,000 draws); the fraction of the total movement P̂_M − P̂(cut-0) carried by the top one, two and three blocks, and the number of blocks needed to reach half of it.
4. Plots: P̂_m against m with the two baselines as reference lines and intervals; Δ_m against m with intervals; both per trace. Trivial blocks (Δ̂_m = 0) marked.
5. Wording rule: results are described ("the largest shift, +0.31, sits in B_09, 420 tokens, 9% of the trace"); "localized" and "diffuse" are not verdicts and no threshold is applied.

## 6. Analysis of the transition tree (Q2, Q3) at Level 1

1. For every sampled cut m: p̂_m, the distribution over the eight Level 1 labels of the first new node after the cut (combined nodes counted under their first path); the fraction of continuations whose first new node opens a block (R1–R4); the fraction whose first sentence is an R4 "Wait" sentence; X_m, the Level 1 label of the last node before the cut.
2. Q2, the type-only null. H0: the distribution of the next label depends only on X_m. Test: pool the cuts by X; the statistic S = mean over cuts of the total-variation distance between p̂_m and the pooled distribution p̂_X of all continuations of cuts sharing X; permutation null by reassigning continuations at random among the cuts sharing X (keeping n per cut), 10,000 permutations; report the observed S, the permutation p-value, and every cut's own TV_m with a bootstrap interval. Cuts whose X occurs once are excluded from the test and listed. The test is run per trace and pooled.
3. Q3, observational versus resampled. For each X: the total-variation distance between p̂_X (resampled, pooled) and the P_corpus row for X, with a bootstrap interval; the per-cut distances TV(p̂_m, P_corpus row X_m). Against P_source: for each cut, p̂_m(Y_source), the probability the continuations reproduce the source's own next label, and the fraction that open a new block where the source did.
4. History forms (scheme 0e): for each ordered pair of labels (W, X) with at least three cuts on each side, P̂(next = Y | W --> X) against P̂(next = Y | X) over cuts whose prefix contains a W node before the last X node versus those that do not; and the order comparison P̂(next | W --> X) against P̂(next | X --> W) where both orders occur. Reported as tables with counts; no test beyond Q2.
5. Everything above is repeated on the second labeling of the two relabeled cuts (Section 4.2) to show the label-noise effect on p̂_m.

## 7. What is reported, in what form

1. A run folder runs/experiments/resample_blocks_<date>_<hhmm>/ with continuations.jsonl (archived record format plus block and prompt), pcut.csv, the judge run folder, config.json, _log.txt; the large files local, indexed (runs/LARGE_FILES_INDEX.md).
2. A results document docs/shared/[date]_stage1_results_v1.md written by Claude from scripts/s4_analyze.py's output, confirmed by Kian after he re-derives P̂_m, Δ_m and the gap independently from continuations.jsonl (pipeline v2, Section 6 item 6).
3. Figures in figures/.

## 8. Stopping, ceilings and departures

1. Cost ceilings: DeepInfra $45 for all sampling (the worst case, no stop, is about $44 at n = 25); Claude $80 for the judge (about $45–55 expected if the stopping rule fires around C-B09 and E-B06, plus the noise subset and retries; several times that if it never fires). Sampling runs to completion within its ceiling regardless of the judge. Labeling proceeds in the order cut-0, then the two traces' cuts interleaved by m (C-B00, E-B00, C-B01, E-B01, …), so that if the Claude ceiling is reached the unlabeled continuations are the latest blocks; every unlabeled cut is listed in the results, and the mediation analysis (Section 5), which needs no labels, covers every sampled cut.
2. Any departure from this document during the run — a changed cap, a retried cut, a failed slug check — is written to the run folder's DEPARTURES.md and reported.
3. Stage two is decided after reading Section 5's plot and registered separately; the near-tie rule of scheme 0e applies then.

## 9. Sign-off

Design owner: Kian Maleki. Drafted by Claude on 2026-09-17 from the confirmed scheme v6, pipeline v2 and summary v6. Confirmed by Kian on 2026-09-17 (status line above); the commit that adds this file to docs/shared is the registration timestamp.

## Changelog

- 2026-09-17 v2 (= chat2 of the chat begun 2026-09-15 for this document; confirmed by Kian 2026-09-17, before any registered sampling) — Three pre-run amendments from the smoke tests (runs/tests/t7_resample_2026-09-17_1532): the archived stop sequence `<|im_end|>` stated correctly (2.3); the no-think baseline's cap raised from 2000 to 8000 tokens after seven of ten smoke replies were cut off before their answer line (3.1); the judge ceiling made operational — labeling order cut-0 then interleaved by m, sampling independent of the judge ceiling, unlabeled cuts listed (8.1). No hypothesis, condition list, n, stopping rule or analysis changed.
- 2026-09-17 v1 (= chat1 of the chat begun 2026-09-15 for this document; confirmed by Kian 2026-09-17) — First pre-registration of stage one: questions and hypotheses, data and provenance, the 84 sampled prefixes with their block-end indices under R4, n = 25 and n_0 = 100, the stopping rule, scoring, Tk, the judge configuration and the two noise floors, the mediation and transition analyses with the permutation test of the type-only null, reporting, ceilings.
