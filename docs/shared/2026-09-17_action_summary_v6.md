# Action summary — reasoning-trace-experiments — 2026-09-17 v6

File: 2026-09-17_action_summary_v6.md (local version 6 = chat version 2 of the chat begun 2026-09-15 for this document). Supersedes 2026-09-16_action_summary_v5.md (→ archive/). Claude drafts, Kian confirms. Status: content release, confirmed by Kian on 2026-09-17. New content relative to v5: the judge decision and its record, the judge as a named source of uncertainty (Section 2d), the splitter and judge code milestones, rule R4 and prompt v3, costs, file table, decisions log, glossary.

Versioning convention (Option A, decided by Kian 2026-09-14): files Claude produces in a chat are named <name>_chatN.md, N counting from 1 within the chat. When Kian confirms a chat version and saves it to the repo, it becomes [date]_<name>_v<K>.md with K the next consecutive local version; local versions are always consecutive, chat numbers never appear in the repo, and the changelog inside the file records the pairing. Superseded local versions move to archive/. STATE files in docs/claude/ stay dated and are never overwritten.

## 1. Where the project stands

Decided Mid-Thought is submitted to MATS 12.0 and frozen (tag mats12-submission); decision pending. BlueDot application submitted. The active workspace is this repository. No new API run has been made since the freeze and no new pre-registration exists. Between 2026-09-09 and 2026-09-14 the work was conceptual: choosing the direction (Section 2), building the labeling scheme, relabeling the two source traces under it, and settling notation and conventions. The next concrete steps are Kian's review of the labeled traces, the pending decisions in the labeling scheme's Section 12, and then the judge script and the zero-cost pilot on archived continuations.
As of 2026-09-17: the labels are Kian-reviewed; the labeling scheme is at v6 (rule R4, the "Wait" opener); the pipeline is specified (v2) and its first four steps are built and gated — splitter, judge prompt and codes, judge on the source traces — with a test report per step; the judge is chosen (Claude Sonnet 5, prompt v2 → v3, adaptive thinking low) from measured comparisons; funds are loaded on DeepInfra and a top-up of about $70 is due on the Claude side. Next: step (5/9), the zero-cost pilot in batch mode.

## 2. Current design: block-level map by resampling (path 10)

The submitted study cut the C-trace at sentence boundaries and found no sentence-level jump: commitment to C is distributed, with one region [s30, s44] (run numbering) carrying +0.48 and the "likely" sentence carrying +0.28. Path 10 moves the unit from the sentence to the block. Sentences receive labels from a fixed scheme (Section 3, file 2); nodes are runs of same-label sentences; blocks run from one opener to the next. Resampling from block boundaries then gives, for each position in the source trace, the distribution of the next block type and of the final answer.

Three questions the design answers, in the notation of the labeling scheme's Section 0d:
- Does the block type alone predict what comes next, or does history matter? Compare P(next = Y | X_m^k) across positions with the corpus-counted P_corpus(Y | X) and with the history form P(next = Y | W_m^j → X_m^k). Kian's hypothesis (2026-09-14) is that the whole process matters; this is the test of it.
- Which blocks carry the answer? Within a fixed prefix, split continuations by their next block and compare final-answer rates; and P(answer = C | ⟨ pattern ⟩) for named patterns.
- Does the discourse structure of a trace predict where resampling moves the answer distribution? ReasoningFlow reports that the discourse graph and the mechanistic graph do not align; the behavioral graph measured here is the third.

Design decisions of 2026-09-14 (evening chat, voice; the formal definitions are in the labeling scheme, Section 0e):
- Two trees over one spine. From the same block-end cuts, a mediation tree (how the final-answer distribution moves across each block: P_m, Δ_m) and a transition tree (which block type comes next: P(next = Y | …)). They are complementary: late blocks are trivial for the answer (Δ_m = 0) yet still branch in the transition tree.
- Two stages. Stage one, the registered run: resample at every block-end cut, in order, under the stopping rule (stop at the first cut where all n continuations end in the trace's own answer a_T; later blocks are trivial by assumption). Kian accepted on 2026-09-14 that this leaves no resampled transitions after M and that the E-arm may stop at its first or second cut; the submitted study learned nothing new from the E resampling. Stage two, optional and separately registered: node-level cuts inside the single block with the largest Δ_m — or inside both of the two top blocks when the gap between their Δ_m has a 95% interval that includes zero (the near-tie rule) — decided after the stage-one plot, budget and time permitting. Blocks are always the first unit; finer is a later choice, never the start.
- Three reference points, then the blocks (2026-09-16). Below the first block the run records two baselines: P(a | nothink), the answer with no reasoning tokens at all (an empty, closed thinking block prefilled — the System-1 answer for this item, never measured in the submitted study; n_0 = 100), and P(a | cut-0), thinking from an empty prefix (archived: P(E) = 0.80, P(C) = 0.12). Both are reported for every letter with intervals and sit outside the Δ_m sequence.
- Implementation is specified in 2026-09-16_pipeline_v1.md (confirmed 2026-09-16): JSONL per collection; a splitter that must reproduce the confirmed listing; a judge — Claude Haiku 4.5, pinned id, temperature 0, one call per whole trace, run-length code output, Sonnet 5 as fallback — validated against Kian's reviewed labels before it is trusted on continuations; block-end cuts sampled strictly in order under the stopping rule; the continuations judged in batch; one test per step with a report Kian reads before the next step runs.
- The judge (2026-09-17, Kian's decision after a 2×2 of prompts v1/v2 × Claude Haiku 4.5 / Sonnet 5 and a reasoning curve none/low/medium): Claude Sonnet 5 with prompt v2 and adaptive thinking at low effort, no sampling parameters, one retry. Against Kian's reviewed labels it reaches Level 1 kappa 0.73–0.74, reproduces block boundaries with F1 0.91–0.93 and the first node after a cut 90–91% of the time; its own test-retest is Level 1 kappa 0.90. Haiku 4.5 is not viable (the C-trace's blocks collapse from 46 to 14). Prompt v2 was tuned on the E-trace only; the C-trace was held out. Rule R4 (a sentence whose first word is "Wait" opens a block; labeling scheme v6) is enforced in code, so the most important boundary in these traces does not depend on the judge; the judge prompt is extended to v3 with the rule for the label and is reported in the paper's appendix.
- Localization is measured in tokens: Tk(x), the studied model's own token count of a block, node or cluster of blocks, from one tokenization of the whole trace. Stage one reports P_m and Δ_m with intervals, the block with the largest Δ_m and its Tk, the gap between the largest and the second-largest Δ_m, and the plot of Δ_m against position. No threshold defines "localized" or "diffuse"; the numbers are the description (the submitted study's Δ_jump = 0.4 is the cautionary case).
- Transitions at Level 1 by default (eight labels), finer only where the mass concentrates. History conditions are written with the typed arrow --> ("followed later by"), including Kian's order comparison P(next = Y | W --> X) against P(next = Y | X --> W).
- Paper one is the instrument: a principled typing of the trace, the two trees, and the localization numbers. Intervention is the stated next step (Section 2a), not part of paper one.

Scope and constraints: one item (bat-and-ball with the "$1.00 more" premise deleted), one model (Qwen 3.6-27B via DeepInfra raw completions), budget $100 for new resampling, judge costs separate and small. Publishable at workshop or MATS scale if framed as the resampled-versus-observational test plus mediation. The nearest papers are dated May–July 2026; speed matters.

## 2a. Motivation: why localize (recorded 2026-09-14 at Kian's request)

Read C and E as stand-ins for a wanted and an unwanted behaviour. The reason to localize is stated as a hypothesis, not a premise: when the unwanted answer occurs in one or two percent of samples, whole-trace training sees almost no signal (forty-nine good traces for every bad one), whereas a localized block or cluster of blocks names a dense, targeted training or steering signal. Localization in a wider region is still localization; the numbers of Section 0e say how wide. The intervention ladder, for paper two: prompt-level steering away from the pattern; decoding-time detection of the block type with resampling of that block (the instrument itself is the detector); weight-level suppression of the pattern, with a capability check afterwards. Paper one does none of these; it builds the map they need. Caveat carried from the discussion: a block that moves the answer is behavioural evidence and may be downstream of the cause, which limits what any intervention result can claim about mechanism.

## 2b. Positioning notes from the web searches of 2026-09-14 (notes, not a review; verify every item before it enters a paper)

- Localization by resampling exists and is close: Thought Anchors (2506.19143; counterfactual importance by resampling a sentence 100 times; planning and backtracking sentences act as anchors — a type-level result reached by sentence resampling, not by typing first; the paper frames itself as a foundation for interpretability) and Thought Branches (2510.27484; resampling with a resilience metric; states that it gives principled guidance for chain-of-thought interventions — guidance, not a demonstrated intervention). Thought Anchors is listed among Neel Nanda's own works (80,000 Hours episode page); Thought Branches shares authors with it — verify before stating any affiliation.
- Intervention during generation exists and is close: SafeThink (a safety reward model monitors the chain of thought during generation and steers intermediate steps; intervening in the first one to three steps is reported to suffice) and ReasoningGuard (critical decision points located via attention, brief safety reflections inserted there). Both trigger on a safety score or on attention, not on a typed discourse block. arXiv identifiers not captured in the search notes; verify before citing.
- Not found in these searches: the closed loop — localize by resampling, act on what was localized, show that the unwanted rate drops — and any trigger defined by a typed, content-independent block. That is the shape of the two-paper contribution. The typed trigger's selling point, transfer across items, cannot be shown with one item and one model and is not claimed.
- Neel Nanda's published MATS directions ask whether the chain of thought is faithful to the underlying computation, what happens if seemingly key steps are edited, and whether reasoning can be steered; his framing is pragmatic (what stands between today's models and AGI, studied tractably now). A descriptive instrument paper must therefore say what it buys for safety; Section 2a is that statement.
- The notation (node names X_m^k, cut(·), the history and pattern conditions of Sections 0d and 0e) is itself a contribution: none of the papers above can state a history-conditioned transition, which the anti-Markov test needs.

## 2c. Cost, estimated from the archived run's usage records and the current rate cards (revised 2026-09-16)

Sampling (DeepInfra, Qwen 3.6-27B): the archived resampling run (500 calls) cost $11.53, and its per-call estimated_cost fits input at $0.32 and output at $3.20 per million tokens exactly (August 2026; re-check before registering). Per-call means: cut-0 $0.0143, E-arm $0.0080, C-arm $0.0307 (9,490 completion tokens; the 16,000-token cap was hit by 68 of 500). Stage one at n = 40 costs about $15 with the stopping rule if the new cuts behave as the old ones (C stop around C-B08 to C-B10, E at E-B06 or earlier), about $67 if all 82 block-end cuts were sampled; the no-think baseline adds under a dollar. Judge (Claude Haiku 4.5, $1/$5 per million input/output tokens, batch half price, cached prompt reads 10%; run-length code output at about 4 tokens per sentence): source traces cents, the 44 sweep traces about $0.60, the 500 archived continuations (3.55M tokens of text) about $5, the new continuations at n = 40 about $7.50 — about $13 in all. Whole pipeline at n = 40: about $28; at n = 80 about $56; with Sonnet 5 ($2/$10) as judge about $42; without the stopping rule about $100. Budget set by Kian on 2026-09-15: $160. Funds loaded 2026-09-16: about $60 on DeepInfra, about $30 on the Claude API. Precision at P = 0.5: standard error of P̂ 0.079 at n = 40, 0.056 at n = 80; n is fixed in the pre-registration. GPT-5.4/5.5 ($2.50/$15, $5/$30) are not cheaper than the Claude options; GPT-5.6 Luna ($0.20/$1.20) is, but unproven on a three-level scheme. Full breakdown in 2026-09-16_pipeline_v1.md, Section 8. 
Revised 2026-09-17 from measured token rates (pipeline v2, Section 8): the judge is Sonnet 5 with thinking low, about $80–95 for the whole judge side in batch mode (thinking tokens are three quarters of it); pipeline total about $95–110 at n = 40 with the stopping rule; judge selection cost about $1.90; a top-up of about $70 on the Claude side is due before the pilot.

## 2d. The judge as a source of uncertainty (Kian, 2026-09-17; to be stated in the paper, with the judge prompt in the appendix)

What was done. The two reviewed traces (629 sentences) were labeled by four configurations in a 2×2 — prompt v1 and prompt v2 × Claude Haiku 4.5 and Claude Sonnet 5 — and the best cell, Sonnet 5 × prompt v2, was then measured along a reasoning curve: no thinking with a labels-only instruction, adaptive thinking at low effort twice, adaptive thinking at medium effort. Nine judge runs in all, about $1.90. Prompt v2 was written from the E-trace residue only, with the C-trace held out at the sentence level. Agreement was read at three levels — sentence labels, block boundaries, and the first node after each reviewed cut — and Kian read a blind four-column table of his own labeling and three Sonnet configurations.

What was found. Haiku 4.5 is not viable on either prompt: pooled Level 1 kappa 0.29 and 0.34, and the C-trace's 46 blocks collapse to 14 and 5. Prompt v2 removed the largest systematic errors (headings read as local plans, restatements read as reasoning) and raised Sonnet 5 from kappa 0.71 to 0.80 in a two-attempt mode that cannot be run cleanly. On the clean curve, agreement rises with reasoning and cost rises faster: Level 1 kappa 0.70 / 0.73–0.74 / 0.79 for none / low / medium, block-boundary F1 0.84 / 0.91–0.93 / 0.93, first-node-after-cut agreement 0.85 / 0.90–0.91 / 0.95, projected judge-side cost about $47 / $80–95 / $140. The judge's own test-retest at low effort is Level 1 kappa 0.90 and full-path kappa 0.83: about one sentence in twelve changes label between two identical runs. The disagreements sit mostly at Level 1, not at the fine levels, but largely inside blocks; the block openers the judge misses recur at the same eight sentences in every Sonnet cell and are scheme-level ambiguities. In the blind comparison Kian ranked his own labeling first.

The decision. Claude Sonnet 5, prompt v2 extended to v3 with the rule for "Wait" (rule R4, whose boundary is enforced in code regardless of the judge), adaptive thinking at low effort, no sampling parameters, one retry — the point of the curve where the money buys block structure; the gain from medium effort is of the size of the run-to-run swing and costs 1.6 times as much.

The statement. The choice of judge affects the results. Within this budget the judge's behaviour cannot be quantified, studied or refined beyond the measurements above — every further comparison costs money that the resampling needs, and every further prompt revision on these two traces would only fit them. A stronger model may become available within months and could relabel the same traces. The judge therefore remains a named source of uncertainty in this research. Every reported number that depends on judge labels carries the judge configuration, the prompt version and the noise floor; the judge prompt itself (prompts/judge_prompt_v3.md, with its sha256) is reported in the paper's appendix; the mediation quantities (P_m, Δ_m, the baselines) do not depend on the judge at all.

## 3. Documents and files (docs/shared unless stated)

| file | role | version | supersedes |
|---|---|---|---|
| 2026-09-17_action_summary_v6.md | this document: state, design, motivation, positioning notes, cost, background of the submitted study, files, decisions, next steps, glossary | v6 = chat2 of the chat begun 2026-09-15 (confirmed 2026-09-17) | 2026-09-16_action_summary_v5.md → archive/; v4 and earlier versions and findings_summary.md in archive/ |
| 2026-09-17_labeling_scheme_v6.md | the labeling scheme: Levels 1–3, applicability tests, nodes, openers R1–R4, blocks, notation (0d), block-level quantities and baselines (0e), Section 12 all decided | v6 = chat3 of the chat begun 2026-09-15 (R4 and the Wait doubt-marker leaf; 47/38 blocks) | v5 (2026-09-16; splitting rule as implemented, leaf logical reasoning > algebra) → archive/; v4, v3, v2, v1 in archive/ |
| 2026-09-17_pipeline_v2.md | the pipeline specification: decisions 1–21 (judge, noise floor, </think> rule, R4, uncertainty statement), layout, records, nine steps with done markers, Sonnet request settings, gates, costs, tests | v2 = chat6 of the chat begun 2026-09-15 | 2026-09-16_pipeline_v1.md → archive/ |
| 2026-09-17_source_traces_labeled_v4.md | the Kian-reviewed labels in review layout under rule R4 (ten sentences with the Wait doubt marker; C 47 blocks, E 38) | v4 = chat2 of the chat begun 2026-09-15 for this document | 2026-09-16_source_traces_labeled_v3.md → archive/; v2, v1 in archive/ |
| 2026-09-14_source_traces_sentences_v1.md | the two source traces one sentence per line under the current numbering, with the old index next to each sentence and the old cut positions marked | v1 | source_traces_c004_e036_sentence_indexed_2026-09-09.md → archive/ (keeps the run's numbering, verified against prefix hashes) |
| docs/claude/STATE_2026-09-17.md | Claude's authoritative state file; read first in any new chat | dated | STATE_2026-09-16_4 → archive/ (all earlier STATE files already there) |
| archive/decided-mid-thought/ | the frozen submitted project, its runs, logs, and the raw sweep and resampling files (sweep_items_batball_2026-08-19_1623.jsonl, resample_cuts_2026-08-25_1503.jsonl) | frozen | — |

## 4. Background: the submitted study (frozen; full detail in the submitted repo)

Question. Where does a reasoning model commit to its final answer inside its chain of thought: at an identifiable point mid-trace, or before any thinking token (the pre-registered null)? The submitted study tested the single-sentence version; the block-level version is the current design.

Item and prompt. A famous problem with one premise deleted and an option menu that turns the two readings of "most likely" into answer letters. The exact prompt used for every resampling call (single-select, eval frame off; the `prompt` field of each record is authoritative):

```
A bat and a ball cost $1.10 in total. The bat costs more than the ball. How much does the ball cost?

Choose the single best option:
(A) It is $0.05
(B) It is probably $0.05
(C) There is not enough information, but the answer is most likely $0.05
(D) I am not sure
(E) The question is not well posed
(F) None of the above

Explain your reasoning, then end your reply with a single line of the form "Answer: X" where X is exactly one option letter.
```

Model and instrument. Qwen 3.6-27B, thinking mode, temperature 1.0; single model, single item. Truncation-and-resampling: cut the recorded thinking at a sentence boundary, prefill the prefix into the thinking channel (user turn = the prompt; assistant turn = "<think>\n" + prefix), sample n = 25 continuations per cut, score the final letter. Sweeps ran via OpenRouter (DeepInfra pinned, fallbacks off); resampling ran via DeepInfra's raw completions endpoint directly, because OpenRouter discards thinking-channel prefills. Pre-registration was frozen before any resampling (docs/mats12_research_plan.md + plan_amendment.md in the submitted repo); s* values committed blind (C-trace s60, E-trace s63, run numbering); one pre-authorized scorer revision (v2.1) was triggered by a blinded 20-record hand-check and applied programmatically, with all 35 changed records human-validated; canonical numbers come from the rescored tables; analysis frozen 2026-08-30.

Source traces. Both from sweep condition eval0_multi0 (this prompt) in sweep_items_batball_2026-08-19_1623.jsonl: C-trace = sample 2 (row 4 → c004; 18,690 characters), E-trace = sample 40 (row 36 → e036; 11,401 characters). Look up by the `sample` field; see "record IDs" in the glossary.

Registered verdicts (run numbering).
- Null (flat within ±δ_base = 0.15 of cut-0): REJECTED in both arms. C-trace 3/25 at cut-0 rising to 25/25 at cut-62 (Fisher p < 1e-8, post-hoc support). E-trace formally exceeds the band but had only 0.20 headroom; read as ceiling drift; it functions as the control arm.
- Hyp 3.1a (localized jump in the C-trace at s* = s60): FAILS. P(C) after s* clears 0.7 (0.88), but cut-59 is already 0.60 (not ≤ 0.35) and the step is +0.28 < Δ_jump = 0.4.
- Hyp 3.1b (symmetric jump in the E-trace at s* = s63): FAILS. P(E) ≥ 0.96 at every cut.
- Jump-anywhere check: the largest adjacent single-sentence change in either arm is +0.28 (C-trace, s60). No sentence-level jump ≥ Δ_jump exists.
- Amendment-2 region contrast (pre-specified bisection), C-trace only: the region [s30, s44] carries Δ = +0.48 (P(C) = 0.12 at cut-29 → 0.60 at cut-44; Fisher p ≈ 8e-4, post-hoc support), the only change in the study clearing Δ_jump; attributed to the region, never to a sentence.
- Hyp 3.2a (eval frame, answer level): directionally consistent on sweep data (C-involving 12/48 eval-off vs 5/50 eval-on, multi-select conditions), underpowered, one item; no confirmatory claim. 3.2b (mechanism) not run.

Headline findings.
- Finding 1, distributed commitment: P(C) is constructed in-trace from 0.12 to 1.00 with no localized jump, one threshold-clearing pre-specified region ([s30, s44]), and saturation from s60 (P(C) ≥ 0.88 thereafter). Same shape as Thought Branches' nudged reasoning in a different regime (no hint; underspecified item): a replication in a new setting, not a discovery.
- Finding 2, default/minority asymmetry: the default answer E is about 80% set before any thinking token, prompt-determined; C is built in the trace. P(E) ≥ 0.96 at every E-arm cut.
- Finding 3, post-saturation elaboration: 84.6% of the C-trace's characters are generated after s* (s60), by which point P(C) ≥ 0.88 and never falls. Neighbors: 41–52% of tokens after the "golden step" across five models (arXiv 2605.17672); up to 87% after a "commitment boundary" found with early exit (2606.13603). Ours is distributional (resampled P(C)); theirs is read off the text.
- Finding 4, elicitation: identical reasoning under three prompt formats yields three different answer distributions, while trace-level behavior is invariant across conditions. Recorded finding, not a direction.

Scope limits. One model, one item; all evidence behavioral, no claim about internal mechanisms. The one positive result concerns the C-trace only and is attributed to the whole region [s30, s44]. Not tested: whether the reading of "likely" that a continuation adopts predicts its final answer with the prefix held fixed (the mediation question); the block-level design answers it.

Sentence numbering. Every number above uses the run's numbering. Under the current numbering (2026-09-14 equation rule), s60 → s67, cut-29 → [s0, s32], cut-44 → [s0, s47], cut-62 → [s0, s69]; the full mapping is in 2026-09-14_source_traces_sentences_v1.md.

## 5. Decisions log

- 2026-09-04 — Path 10 chosen (block-level map); directions (1/3) hedge readings and (3/3) early prediction absorbed into it.
- 2026-09-12 — Literature check done; ReasoningFlow adopted as the base scheme; other schemes crosswalked into it.
- 2026-09-13 — Combined labels allowed inside a sentence, no precedence order (assumption A1: narration and process agree at the coarse level, not necessarily the fine level). Edges not used.
- 2026-09-14 — Equation-end splitting rule approved; current numbering adopted (C 375 sentences, E 254); s* = C s67, E s69. Level 1 label "Fact" renamed "Knowledge" (Recall rejected: no precedent as a top-level label). Self-as-AI statements → Knowledge > self-knowledge. Node names X_m^k(n). Blind human labeling skipped for time; validation is Kian's face-validity review of the labeled traces. Option A versioning adopted; findings_summary.md renamed and restructured as this action summary.
- 2026-09-14 (later) — Repo audit items closed in commit aeefb86: findings_summary.md recovered into archive/docs/shared/, superseded STATE files and action summary v1 moved to archive/, the 2026-09-09 sentence listing added to archive/docs/shared/. Labeling scheme v2 issued as a correction release (node counts 220 and 148 under the block-boundary rule; Section 8 regenerated; stale pointers fixed); no rule changed.
- 2026-09-14 (evening, voice chat) — Design settled at the level of definitions (labeling scheme Section 0e): two trees over one spine; stage one at every block-end cut under the stopping rule; stage two optional, inside the block with the largest Δ_m, registered separately; localization measured in tokens (Tk); no thresholds — descriptive numbers and the plot; trivial block := Δ_m = 0; typed arrows -> and -->; transitions at Level 1 by default; paper one = the instrument, intervention deferred to paper two; motivation recorded (Section 2a); positioning notes from web searches (Section 2b); stage-one cost estimated from the archived usage records (Section 2c). Cut placement (Section 12, item 9) thereby decided.
- 2026-09-14 (evening, text) — Kian: arrows -> and --> confirmed, pattern brackets ⟨ ⟩ kept (scheme item 16 closed); stopping rule accepted with its consequences for the tail transitions and the E-arm (item 13 decided: option a); budget raised to about $100, n = 40 the candidate for the pre-registration.
- 2026-09-14 (evening, text, later) — Kian: --> inclusive, -> a special case of --> (scheme item 12); near-tie rule = the 95% interval of the gap between the two largest Δ_m excludes zero → top block alone, otherwise both (item 14); unresolved continuations ("?") stay in the denominator, which is always n, and are reported per cut (item 15).
- 2026-09-15 — Kian's face-validity review of the labels: complete. One rule change, the self-question rule — a question the model puts to itself about the content is Reasoning, with Level 2/3 by content; steering questions (headings, announced verifications or backtracks) stay Planning — applied to 21 C and 4 E sentences (listing v2); nodes 220 → 193 and 148 → 146, blocks unchanged, combined sentences 9 → 8 in C. Scheme item 6 (check-question threshold) thereby moot. Section 12 items decided the same day: 2 — all thirteen combined sentences stay; 7 — announce-output sentences keep opening blocks (37 E-blocks); 8 — Reading A (first intermediate conclusion C s113, E s41; C s159 and E s99 unchanged). Section 12 has no pending decision left; item 10 (transition counts) is a pipeline computation.
- 2026-09-15/16 — Pipeline specified and confirmed (2026-09-16_pipeline_v1.md): JSONL per collection; one judge call per trace with the full trace, Level 3 collected, run-length code output, blocks derived never judged; prompt generated from scheme v4 with trace-quoted examples paraphrased or removed; cuts from the reviewed blocks, strictly sequential under the stopping rule; "?" in the denominator n; P_source and P_corpus per the scheme's definitions; judge Claude Haiku 4.5 (Sonnet 5 fallback after the agreement test); batch mode for the collections not needed at once; budget $160; no-think baseline (n_0 = 100) below cut-0; Tk from the API's prompt_tokens; a test per step, no step runs before its report reads PASS and Kian has read it. Funds loaded: about $60 DeepInfra, about $30 Claude API; `.env` holds DEEPINFRA_API_KEY and CLAUDE_API_KEY.
- 2026-09-16 (evening) — Splitter built and gated (PASS 8/8 against the confirmed listing); the E-trace numbering fact (the archived run's own splitter yields 253 base sentences, the listing 247, agreeing through old s150; archived cuts unaffected); rules b′ (option labels) and the tag exclusion; the 37 MB archived500 sentence file kept out of git.
- 2026-09-16 (night) — Judge prompt v1 and 75 label codes generated from scheme v5 (leaf logical reasoning > algebra added for 18 reviewed uses); reply parser; tests t3 and t0 PASS; keys and both model ids verified.
- 2026-09-17 — Judge selection: Haiku 4.5 on prompt v1 reached Level 1 kappa 0.29 and collapsed the C-trace's blocks; prompt v2 (headings, restatement test, branching, option-evaluation limits, Reflection/announce-output split, conclusion rule, labeling order) written from the E-trace residue only; 2×2 and reasoning curve measured; Kian chose, blind among four labelings (his own and three Sonnet configurations), his own labeling first and then Sonnet 5 × v2 × thinking low as the judge; the `</think>` rule for continuations; rule R4 and the Level 3 leaf Wait (doubt marker) (scheme v6, listing v4: 47 and 38 blocks); the judge recorded as a named source of uncertainty for the paper (Section 2d).

- Pending: prompt v3 (v2 plus the R4 label rule) generated from scheme v6, gated, confirmed by one Sonnet run; n per cut (40 candidate) and n_0 — fixed in the pre-registration; the Claude-side top-up (about $70) before the pilot; batch mode implementation (step 5/9).

## 6. Next steps

(1/5) DONE 2026-09-15 — Kian's review of the labels; result in 2026-09-15_source_traces_labeled_v2.md.
(2/5) DONE 2026-09-16 — decisions taken 2026-09-15; labeling scheme v4 and this v5 confirmed 2026-09-16. The judge prompt is generated from scheme v4.
(3/5) DONE 2026-09-17 — splitter, prompt v1/v2 and codes, judge on the source traces; Sonnet 5 × v2 × thinking low chosen (Level 1 kappa 0.73–0.74; block F1 0.91–0.93; test-retest 0.90); pipeline steps (2/9)–(4/9) with tests t0, t2, t3, t4.
(4/5) NEXT — the pilot, pipeline step (5/9), test t5: R4 in the derivation with its gate; prompt v3 gated and confirmed; batch mode implemented in s1_judge; Sonnet 5 × v2 × thinking low in batch on the 44 sweep traces (P_corpus, about $2.5) and the 500 archived continuations (first P(next | cut), about $35–40); requires the Claude-side top-up.
(5/5) Pre-registration — pipeline step (6/9), test t6 — then the run, steps (7/9) to (9/9), tests t7–t9: no-think baseline, cut-0, block-end cuts strictly in order under the stopping rule with n fixed in the registration, continuations judged in batch, analysis (P_m, Δ_m, top block, Tk, gap, transitions against P_corpus and P_source); stage two decided afterwards and registered separately if taken.

## 7. Working rules that bite (full rules in the project instructions)

- Nothing is overwritten; superseded files go to archive/ with their dates. Commit and push after every session; Claude lists the files produced at the end of each chat as a reminder.
- Every run writes _log.txt with attempted/succeeded counts per cell; the `prompt` field in each record is authoritative; resampling uses DeepInfra raw completions (OpenRouter drops thinking-channel prefills); API keys live in .env only.
- Labels in the labeled traces are Claude's provisional labels; say so wherever they are used. Nothing is a finding until Kian has reviewed and the judge has run. When reviewing, look for how a result could be false.
- Cut notation for new designs: cut-k = [s0, s_k), exactly k sentences, cut-0 empty.

## Glossary
Canonical terms. Extend here; split into its own file when it outgrows
this document.

Objects
- item — one question together with its answer options; this study used
  one item. The prompt in the Method section (second bullet) is the item as
  presented in the eval-off, single-select condition.
- condition — one prompt format for the item in the 2×2 sweep (eval frame
  on/off × single/multi select), e.g. eval0_multi0 = eval frame off,
  single-select. (Say "condition", not "cell".)
- elicitation — how the final answer is requested: option wording, single
  vs. multi select, the required answer-line format.
- thinking — the model's thinking channel: the text it generates between
  <think> and </think> before writing its reply. A technical term for a
  channel, not a claim about cognition.
- reasoning — what the thinking text narrates (its arguments, derivations,
  interpretations). The study measures thinking text; it does not assume
  the narration is the model's actual computation.
- trace — the full recorded thinking text of one generation. Example: the
  C-trace is the thinking text of sample 2 in condition eval0_multi0 of the
  08/19 sweep, ending in "Answer: C"; full raw examples are in
  docs/raw_examples_seed20260902_final.md of the old repo.
- source trace — the recorded trace an arm is built from (here: the C-trace
  and the E-trace).
- arm — everything built from one source trace: all its cuts and all their
  continuations. Example: the C-arm = the 13 cuts of the C-trace and the
  25 continuations sampled at each. Arms are named for the source trace's
  final answer (C-arm, E-arm).

Positions in a trace
- s_k (written s0, s1, …, s60) — the k-th sentence of a source trace,
  counting from s0 = the first sentence. Sentence boundaries come from the
  splitter used in the run; the "Ready/Proceed" tail is trimmed first.
  NUMBERING NOTE (2026-09-14): two numberings now exist. The results in
  this document use the run's numbering (reconstructed and verified
  against the resampling prefix hashes; listing file
  source_traces_c004_e036_sentence_indexed_2026-09-09.md). From 2026-09-14
  the splitter also ends a sentence at the end of each equation (a comma
  closing a segment that contains = < > acts as a period; commas inside
  parentheses do not split; a parenthesis after an equation starts a new
  sentence only if it opens a capitalized clause). This adds 9 boundaries
  to the C-trace (366 → 375) and 7 to the E-trace (247 → 254). Every old
  boundary is preserved, so every archived cut still ends on a sentence
  boundary; only the indices shift. The mapping is printed sentence by
  sentence in source_traces_c004_e036_sentence_indexed_v2_2026-09-14.md.
  Intervals of sentences are written [s30, s44] (both ends included) or
  [s30, s45) (right end excluded); the older form s30–s44 means [s30, s44].
- cut-k — the prefix consisting of sentences s0 through s_k, i.e. the trace
  truncated after sentence s_k (k+1 sentences). Exception by definition:
  cut-0 is the EMPTY prefix (no thinking text at all), not "s0 alone". This
  irregularity is a lesson for future designs: define cut-k as exactly k
  sentences so that cut-0 = empty falls out naturally. Adopted 2026-09-14
  for all new designs: cut-k = [s0, s_k), exactly k sentences, cut-0 =
  [s0, s0) = empty. The old run's cut-k = [s0, s_k] (k+1 sentences); the
  old cut positions map to the v2 numbering as, for example, old C cut-60
  = v2 [s0, s67] = v2 cut-68 in the half-open form.
- prefix — the trace text up to and including the cut sentence (the content
  of cut-k).
- prefill — the same prefix placed inside the model's thinking channel so
  that generation resumes from that point. Concretely, the request template
  is: user turn = the prompt (item); assistant turn = "<think>\n" + prefix.
  The prompt goes in the user turn; the prefix goes inside <think>.
- continuation — one sampled completion from a prefill (n = 25 per cut),
  including the rest of the thinking and the final reply.
- s* — the pre-registered sentence where the trace interprets "likely"
  (C-trace s60, E-trace s63 in the run's numbering), fixed by hand before
  any resampling. Under the v2 numbering of 2026-09-14 the same two
  sentences are C s67 and E s69; their wording is unchanged, and every
  result in this document keeps the run's numbers. The asterisk is
  standard notation for a distinguished value ("the special sentence").
  It is the notation of the submitted study; under the block-level design
  the analog is a distinguished node or block (see the labeling structure
  document). In the block-level labeling, C s67 carries two labels:
  Reasoning > hedge word analysis > everyday reading and Reflection >
  meta-evaluation of a step > option (B).
- region — a pre-specified span of consecutive sentences tested as a unit,
  written s30–s44 (= sentences s30 through s44, the sentences added between
  cut-29 and cut-44). Results are attributed to the whole region, never to
  a sentence inside it.
- block — the unit of the block-level design, defined precisely in the
  labeling scheme (docs/shared/[date]_labeling_scheme_v*.md, Section 6),
  which supersedes the earlier phrase "hand-annotated logical
  unit".
  In short: sentences receive labels (Level 1 > Level 2 > Level 3,
  ReasoningFlow-based); a node is a maximal run of consecutive sentences
  with the same label at a given level; an opener is a sentence that
  satisfies the opener rules (first sentence of a Planning node that is
  not all local plans; an Assumption > branching sentence; a Conclusion >
  final answer sentence); a block runs from one opener to just before the
  next. Nodes are named X_m^k(n): abbreviation, block subscript, running
  superscript when needed, sentence count in parentheses. Attribution at
  block or node resolution, never finer than a node.

Measurements and thresholds
- P(answer | cut) — the fraction of a cut's continuations whose final reply
  scores as that answer, e.g. P(C | cut-44) = 15/25 = 0.60.
- baseline — the answer distribution at cut-0. Reproduction requirement:
  it must match the source condition's sweep distribution within δ_base;
  in this project δ_base = 0.15.
- gate — a pre-registered pass/fail check that must pass before the next
  step runs. Gates in this study: (i) the baseline reproduction check
  above; (ii) at least two C-answering traces in the single-select
  conditions, otherwise fall back to multi-select conditions for trace
  selection.
- Δ (delta) — a change in P(answer) between two cuts, e.g. Δ = +0.48 from
  cut-29 to cut-44.
- jump — an adjacent-cut change with Δ ≥ Δ_jump; in this project
  Δ_jump = 0.4 (registered). No jump exists in either arm.
- drift — a sustained change across cuts without any single step reaching
  Δ_jump.
- flat (category 0, the null) — all cuts within ±δ_base of cut-0.
- saturation — the point after which P(answer) stays at or above its final
  level; C-arm: from s60 on, P(C) ≥ 0.88.

Block-level design (2026-09-14; definitions in the labeling scheme, Section 0e)
- a_T — the source trace's own final answer (C for the C-trace, E for the
  E-trace).
- cut(B_m) — the prefix ending with the last sentence of block B_m; blocks
  are numbered from 0, like the block subscripts of node names.
- P_m, Δ_m — P_m = P(answer = a_T | cut(B_m)), the answer rate from the end
  of block B_m; Δ_m = P_m − P_{m−1} (Δ_0 against cut-0), the signed shift
  across block B_m. No absolute values.
- trivial block — a block with Δ_m = 0: it does not move the answer; it may
  still branch in the transition tree.
- stopping rule, M — cuts are resampled in order and stop at the first cut
  where all n continuations end in a_T; that block is B_M; later blocks are
  trivial by assumption, not by measurement.
- Tk(x) — the token count of x (block, node, cluster of blocks, chain of
  nodes) in the studied model's tokenizer, from one tokenization of the whole
  trace; the unit of localization.
- cluster of blocks — several blocks read as one unit when the shift is
  spread over neighbours.
- stage one / stage two — block-end cuts everywhere (registered) / node-level
  cuts inside the block with the largest Δ_m (optional, separately
  registered).
- -> and --> — typed arrows: "immediately followed by" and "followed later
  by" (zero or more nodes between, so -> is a special case of -->).
  Rendered as → and ⇢ in tables and figures.
- near-tie — the two largest Δ_m are a near-tie when the 95% interval of
  their gap includes zero; stage two then targets both blocks.
- "?" — a continuation that ends without an answer letter (mostly at the
  token cap); it stays in the denominator of P̂, which is always n, and its
  count is reported per cut.
- nothink, P(a | nothink) — the no-think baseline: the model's answer with an empty, closed thinking block prefilled, hence no reasoning tokens; the System-1 answer for the item; reported next to P(a | cut-0), outside the Δ_m sequence.
- self-question rule — a question the model asks itself about the problem's content is Reasoning (Level 2/3 by content); a question that steers the process (heading, announced verification or backtrack) stays Planning. Kian, 2026-09-15.
- Kian-reviewed — the status of the labels after Kian's face-validity review of 2026-09-15; the judge is the second check.
- judge (LJ) — the LLM that labels sentences by the scheme in the pipeline: Claude Haiku 4.5, pinned id, temperature 0, one call per whole trace, run-length code output (`15-22 Re.ca.al`); its agreement with the reviewed labels is measured before it labels anything else.
- run-length code output — the judge's reply format: one line per run of consecutive sentences with the same label, `<first>-<last> <code>`, codes from `labels_v1.json`; expanded and validated by the script as a gapless partition.
- collection — a set of traces handled as one JSONL file with a `trace_id` per record: source (c004, e036), sweep44, archived500, and each resampling run.
- batch mode — the Claude API's asynchronous Message Batches: many requests submitted as one job, half price, results within 24 hours; used for collections not needed at once.
- test report — `TEST_REPORT.md` in `runs/tests/t<k>_<step>_<date>_<hhmm>/`: one line per check, PASS or FAIL with the numbers; no step runs before its report reads PASS and Kian has read it.
- R4, Wait (doubt marker) — opener rule R4 (Kian, 2026-09-17): a sentence whose first word is "Wait" opens a block and carries the Level 3 leaf Wait (doubt marker) under Planning > initiate verification or > initiate backtracking; applied to the sentence text by the derivation code.
- judge noise floor — the agreement of two identical judge runs with each other (Sonnet 5 × v2 × thinking low: Level 1 kappa 0.90, full path 0.83); the ceiling for any reviewed-vs-judge agreement and the label noise carried into every judge-dependent number.
- reasoning curve — agreement and structural metrics of the judge as a function of its thinking effort (none / low / medium), measured 2026-09-17 on the two source traces.
- structural metrics — block-boundary hits/misses/extras and F1, next-node-after-cut agreement, node F1, and the sentence-level decomposition of disagreements by level (scripts/structural_agreement.py).
- blind comparison — the four-column table (Kian's reviewed labeling and three judge configurations, identities withheld) on which the judge was chosen; Kian ranked his own labeling first.

Bookkeeping
- record IDs — resampling records carry IDs like rs0823_c004_cut015_007
  and a source_id like s0819_eval0multi0_004. The trailing number (004,
  036) is the ROW POSITION of the source trace within its condition in the
  sweep file (4th row, 36th row), NOT the value of the `sample` field. So:
  C-trace = condition eval0_multi0, sample 2, row 4 → "c004";
  E-trace = condition eval0_multi0, sample 40, row 36 → "e036". Both
  coordinates are written in log_2026-08-22.md §5. When looking a trace up
  in the sweep file, use the sample number, not the ID number.

## Changelog
- 2026-09-17 v6 (= chat2 of the chat begun 2026-09-15 for this document; confirmed by Kian 2026-09-17) — Status paragraph; the judge decision and record in Section 2; new Section 2d, the judge as a named source of uncertainty; cost revision; file table (scheme v6, pipeline v2, listing v4, STATE_2026-09-17); decisions log for 2026-09-16 evening/night and 2026-09-17; pending list; next steps (3/5 done, 4/5 next); glossary (R4, judge noise floor, reasoning curve, structural metrics, blind comparison).
- 2026-09-16 v5 (= chat1 of the chat begun 2026-09-15; confirmed by Kian 2026-09-16) — Status paragraph in Section 1; Section 2: the two baselines and the pipeline pointer; Section 2c rewritten with the judge and batch pricing, the $160 budget, the funds loaded and the whole-pipeline totals; file table: scheme v4, pipeline v1, listing v2, STATE_2026-09-16; decisions log: the review, the self-question rule, Section 12 items 2, 6, 7, 8, the pipeline decisions of 2026-09-15/16; pending list reduced to n, n_0, the judge confirmation and the failure policy; next steps restated against the pipeline's step numbers; glossary entries added (nothink, self-question rule, Kian-reviewed, judge, run-length code output, collection, batch mode, test report).
- 2026-09-14 v4 (= chat3 of the 2026-09-14 evening chat; confirmed by Kian 2026-09-14) — Kian's text decisions recorded (arrows confirmed and --> inclusive, ⟨ ⟩ kept, stopping rule accepted, near-tie rule by the interval of the gap, "?" always in the denominator n, budget ≈ $100, n = 40 candidate). Design decisions of the evening chat added to Section 2 (two trees, two stages, stopping rule, Tk, no thresholds, Level 1 default, paper-one scope); new Sections 2a (motivation), 2b (positioning notes from the 2026-09-14 web searches, to be verified) and 2c (stage-one cost from the archived usage records: $0.32/M in, $3.20/M out; ≈ $42 at n = 25 without the stopping rule, ≈ $9 with it); file table updated for scheme v3, summary v4 and STATE_2026-09-14_7; decisions log extended and its pending list updated (cut placement decided; five new pending items); (5/5) restated for stage one; glossary: block pointer fixed, block-level entries added; "six real ones" corrected to five.
- 2026-09-14 v3 (= chat3) — Bookkeeping: file table updated to labeling scheme v2 and STATE_2026-09-14_4; decisions log records the repo audit closure (commit aeefb86) and the scheme's correction release; pending item on the first intermediate conclusion restated for both traces. No other content changed.
- 2026-09-14 v2 (= chat2; confirmed by Kian 2026-09-14) — Background section restored to full: verbatim prompt, model and instrument, infrastructure, pre-registration and scorer, source-trace coordinates, registered verdicts with their numbers, scope limits, and the numbering mapping for the cited positions. Chat1 had compressed these too far; the verbatim prompt in particular exists nowhere else in project knowledge.
- 2026-09-14 v1 (chat1) — Created from findings_summary.md: restructured around the current design (path 10), file inventory under the Option A convention, decisions log, next steps; submitted-study findings compressed into a background section; glossary carried over with the 2026-09-14 numbering and block-level entries.
- Inherited from findings_summary.md: 2026-09-04 — first confirmed version (submitted-project summary, follow-on directions, glossary seeded).
