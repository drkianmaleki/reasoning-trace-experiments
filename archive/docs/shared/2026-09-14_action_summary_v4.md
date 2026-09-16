# Action summary — reasoning-trace-experiments — 2026-09-14 v4

File: 2026-09-14_action_summary_v4.md (local version 4 = chat version 3 of the 2026-09-14 evening chat). Supersedes 2026-09-14_action_summary_v3.md (→ archive/). Claude drafts, Kian confirms. Status: content release, confirmed by Kian on 2026-09-14. New content relative to v3: the design decisions of the 2026-09-14 evening chat (Section 2), the motivation (2a), positioning notes (2b), the stage-one cost estimate (2c), the decisions log, glossary entries, and two corrections ("six" → "five" real combined sentences; stale pointer to the labeling scheme in the glossary).

Versioning convention (Option A, decided by Kian 2026-09-14): files Claude produces in a chat are named <name>_chatN.md, N counting from 1 within the chat. When Kian confirms a chat version and saves it to the repo, it becomes [date]_<name>_v<K>.md with K the next consecutive local version; local versions are always consecutive, chat numbers never appear in the repo, and the changelog inside the file records the pairing. Superseded local versions move to archive/. STATE files in docs/claude/ stay dated and are never overwritten.

## 1. Where the project stands

Decided Mid-Thought is submitted to MATS 12.0 and frozen (tag mats12-submission); decision pending. BlueDot application submitted. The active workspace is this repository. No new API run has been made since the freeze and no new pre-registration exists. Between 2026-09-09 and 2026-09-14 the work was conceptual: choosing the direction (Section 2), building the labeling scheme, relabeling the two source traces under it, and settling notation and conventions. The next concrete steps are Kian's review of the labeled traces, the pending decisions in the labeling scheme's Section 12, and then the judge script and the zero-cost pilot on archived continuations.

## 2. Current design: block-level map by resampling (path 10)

The submitted study cut the C-trace at sentence boundaries and found no sentence-level jump: commitment to C is distributed, with one region [s30, s44] (run numbering) carrying +0.48 and the "likely" sentence carrying +0.28. Path 10 moves the unit from the sentence to the block. Sentences receive labels from a fixed scheme (Section 3, file 2); nodes are runs of same-label sentences; blocks run from one opener to the next. Resampling from block boundaries then gives, for each position in the source trace, the distribution of the next block type and of the final answer.

Three questions the design answers, in the notation of the labeling scheme's Section 0d:
- Does the block type alone predict what comes next, or does history matter? Compare P(next = Y | X_m^k) across positions with the corpus-counted P_corpus(Y | X) and with the history form P(next = Y | W_m^j → X_m^k). Kian's hypothesis (2026-09-14) is that the whole process matters; this is the test of it.
- Which blocks carry the answer? Within a fixed prefix, split continuations by their next block and compare final-answer rates; and P(answer = C | ⟨ pattern ⟩) for named patterns.
- Does the discourse structure of a trace predict where resampling moves the answer distribution? ReasoningFlow reports that the discourse graph and the mechanistic graph do not align; the behavioral graph measured here is the third.

Design decisions of 2026-09-14 (evening chat, voice; the formal definitions are in the labeling scheme, Section 0e):
- Two trees over one spine. From the same block-end cuts, a mediation tree (how the final-answer distribution moves across each block: P_m, Δ_m) and a transition tree (which block type comes next: P(next = Y | …)). They are complementary: late blocks are trivial for the answer (Δ_m = 0) yet still branch in the transition tree.
- Two stages. Stage one, the registered run: resample at every block-end cut, in order, under the stopping rule (stop at the first cut where all n continuations end in the trace's own answer a_T; later blocks are trivial by assumption). Kian accepted on 2026-09-14 that this leaves no resampled transitions after M and that the E-arm may stop at its first or second cut; the submitted study learned nothing new from the E resampling. Stage two, optional and separately registered: node-level cuts inside the single block with the largest Δ_m — or inside both of the two top blocks when the gap between their Δ_m has a 95% interval that includes zero (the near-tie rule) — decided after the stage-one plot, budget and time permitting. Blocks are always the first unit; finer is a later choice, never the start.
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

## 2c. Cost of stage one, estimated from the archived run's usage records (2026-09-14)

The resampling run resample_cuts_2026-08-25_1503.jsonl (500 calls) cost $11.53; the recorded per-call estimated_cost fits input at $0.32 and output at $3.20 per million tokens exactly (DeepInfra, Qwen 3.6-27B, August 2026 — re-check the current rate before registering). Per-call means: cut-0 $0.0143 (4,450 completion tokens on average), E-arm $0.0080 (2,391), C-arm $0.0307 (9,490; the 16,000-token cap was hit by 68 of the 500 continuations). Stage one at every block-end cut needs 82 prefixes: cut-0, 45 C-trace cuts (cut(C-B45) is the whole trace and is not resampled) and 36 E-trace cuts. At the archived per-call means, n = 25 costs about $42 and n = 50 about $84; both are upper estimates, since late cuts produce shorter continuations. Under the stopping rule, if the new cuts behave as the old ones did — the C-arm first read 25/25 at old cut-62, inside C-B08 = [s58, s78]; the E-arm at old cut-62, inside E-B06 = [s53, s70], whose block-end cut(E-B06) = old cut-64 also read 25/25 — the run stops around C-B08 to C-B10 and at E-B06 or earlier: about $9 at n = 25, $15 at n = 40 and $19 at n = 50. Kian (2026-09-14): the budget can go to about $100 and n = 40 is the candidate; at n = 40 the full 82 cuts cost about $67 without the stopping rule. Precision, not cost, is the constraint: the standard error of P̂ at P = 0.5 is 0.10 at n = 25, 0.079 at n = 40 and 0.07 at n = 50, so a Δ_m of 0.1 is within noise at any of them. n is fixed in the pre-registration (5/5).

## 3. Documents and files (docs/shared unless stated)

| file | role | version | supersedes |
|---|---|---|---|
| 2026-09-14_action_summary_v4.md | this document: state, design, motivation, positioning notes, cost estimate, background of the submitted study, decisions, glossary | v4 = chat3 of the evening chat (confirmed 2026-09-14) | 2026-09-14_action_summary_v3.md → archive/; earlier: v2 (confirmed), v1 (unconfirmed) and findings_summary.md (2026-09-04), all in archive/ |
| 2026-09-14_labeling_scheme_v3.md | the labeling scheme: Levels 1–3, applicability tests, nodes, openers, blocks, probability notation (0d), block-level quantities of the resampling design (0e), open items (Section 12) | v3 = chat3 of the evening chat (typed arrows, cut(B_m), Section 0e, items 9 and 12–16 decided; confirmed 2026-09-14) | 2026-09-14_labeling_scheme_v2.md (= chat8) → archive/; v1 (= chat7, confirmed) in archive/ |
| 2026-09-14_source_traces_labeled_v1.md | Claude's complete provisional labeling of both source traces, with nodes and blocks; the object of Kian's review | v1 = chat3 | labeled_sentences_nodes_blocks_c004_e036_2026-09-14_v3.md (same content) |
| 2026-09-14_source_traces_sentences_v1.md | the two source traces one sentence per line under the current numbering, with the old index next to each sentence and the old cut positions marked | v1 | source_traces_c004_e036_sentence_indexed_2026-09-09.md → archive/ (keeps the run's numbering, verified against prefix hashes) |
| docs/claude/STATE_2026-09-14_7.md | Claude's authoritative state file; read first in any new chat | dated | STATE_2026-09-14_4.md → archive/, with the never-committed STATE_2026-09-14_5 and _6 (STATE_2026-09-14_3, _2, STATE_2026-09-14, STATE_2026-09-04 and STATE_2026-09-03 already there) |
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
- Pending (labeling scheme Section 12): combined sentences (keep all / keep the five real ones / drop); check-question scope threshold (none, 3, 5); E-trace tail (announce-output opens blocks or not; 37 vs 33 blocks); first intermediate conclusion, one decision for both traces (Reading A: C s113 and E s41 answer in substance; Reading B: C s159 and E s99 name an option); transition counts (scheme item 10). Probability notation confirmed with scheme v3.

## 6. Next steps

(1/5) Kian reviews 2026-09-14_source_traces_labeled_v1.md and returns disagreements as sentence index plus his label; Claude re-derives nodes, blocks and tables from the corrected labels, never by hand.
(2/5) Kian settles the pending decisions; each gets a changelog line in the labeling scheme.
(3/5) Claude writes the judge prompt from the labeling scheme and a script (API with a pinned model string at temperature 0, or `claude -p` under the Agent SDK credit); test on the two source traces; report judge-versus-Claude agreement per label (kappa, Jaccard) and the residue.
(4/5) Zero-cost pilot: the judge labels the archived continuations (13 C cuts × 25, 6 E cuts × 25, cut-0 × 25) and, optionally, the 44 sweep traces of eval0_multi0 for the corpus matrix.
(5/5) Pre-registration for stage one of the block-boundary resampling run (n per cut, the stopping rule stated as an assumption, the null of no type dependence, the sequence test, the descriptive localization report, cost within $100; stage two, if any, registered separately), then the run.

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
- 2026-09-14 v4 (= chat3 of the 2026-09-14 evening chat; confirmed by Kian 2026-09-14) — Kian's text decisions recorded (arrows confirmed and --> inclusive, ⟨ ⟩ kept, stopping rule accepted, near-tie rule by the interval of the gap, "?" always in the denominator n, budget ≈ $100, n = 40 candidate). Design decisions of the evening chat added to Section 2 (two trees, two stages, stopping rule, Tk, no thresholds, Level 1 default, paper-one scope); new Sections 2a (motivation), 2b (positioning notes from the 2026-09-14 web searches, to be verified) and 2c (stage-one cost from the archived usage records: $0.32/M in, $3.20/M out; ≈ $42 at n = 25 without the stopping rule, ≈ $9 with it); file table updated for scheme v3, summary v4 and STATE_2026-09-14_7; decisions log extended and its pending list updated (cut placement decided; five new pending items); (5/5) restated for stage one; glossary: block pointer fixed, block-level entries added; "six real ones" corrected to five.
- 2026-09-14 v3 (= chat3) — Bookkeeping: file table updated to labeling scheme v2 and STATE_2026-09-14_4; decisions log records the repo audit closure (commit aeefb86) and the scheme's correction release; pending item on the first intermediate conclusion restated for both traces. No other content changed.
- 2026-09-14 v2 (= chat2; confirmed by Kian 2026-09-14) — Background section restored to full: verbatim prompt, model and instrument, infrastructure, pre-registration and scorer, source-trace coordinates, registered verdicts with their numbers, scope limits, and the numbering mapping for the cited positions. Chat1 had compressed these too far; the verbatim prompt in particular exists nowhere else in project knowledge.
- 2026-09-14 v1 (chat1) — Created from findings_summary.md: restructured around the current design (path 10), file inventory under the Option A convention, decisions log, next steps; submitted-study findings compressed into a background section; glossary carried over with the 2026-09-14 numbering and block-level entries.
- Inherited from findings_summary.md: 2026-09-04 — first confirmed version (submitted-project summary, follow-on directions, glossary seeded).
