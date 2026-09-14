# Action summary — reasoning-trace-experiments — 2026-09-14 v1

File: 2026-09-14_action_summary_v1.md (local version 1 = chat version 1 of 2026-09-14). Supersedes docs/shared/findings_summary.md (last confirmed 2026-09-04), which moves to archive/. Claude drafts, Kian confirms. Status of this version: draft; confirmation pending.

Versioning convention (Option A, decided by Kian 2026-09-14): files Claude produces in a chat are named <name>_chatN.md, N counting from 1 within the chat. When Kian confirms a chat version and saves it to the repo, it becomes [date]_<name>_v<K>.md with K the next consecutive local version; local versions are always consecutive, chat numbers never appear in the repo, and the changelog inside the file records the pairing. Superseded local versions move to archive/. STATE files in docs/claude/ stay dated and are never overwritten.

## 1. Where the project stands

Decided Mid-Thought is submitted to MATS 12.0 and frozen (tag mats12-submission); decision pending. BlueDot application submitted. The active workspace is this repository. No new API run has been made since the freeze and no new pre-registration exists. Between 2026-09-09 and 2026-09-14 the work was conceptual: choosing the direction (Section 2), building the labeling scheme, relabeling the two source traces under it, and settling notation and conventions. The next concrete steps are Kian's review of the labeled traces, the pending decisions in the labeling scheme's Section 12, and then the judge script and the zero-cost pilot on archived continuations.

## 2. Current design: block-level map by resampling (path 10)

The submitted study cut the C-trace at sentence boundaries and found no sentence-level jump: commitment to C is distributed, with one region [s30, s44] (run numbering) carrying +0.48 and the "likely" sentence carrying +0.28. Path 10 moves the unit from the sentence to the block. Sentences receive labels from a fixed scheme (Section 3, file 2); nodes are runs of same-label sentences; blocks run from one opener to the next. Resampling from block boundaries then gives, for each position in the source trace, the distribution of the next block type and of the final answer.

Three questions the design answers, in the notation of the labeling scheme's Section 0d:
- Does the block type alone predict what comes next, or does history matter? Compare P(next = Y | X_m^k) across positions with the corpus-counted P_corpus(Y | X) and with the history form P(next = Y | W_m^j → X_m^k). Kian's hypothesis (2026-09-14) is that the whole process matters; this is the test of it.
- Which blocks carry the answer? Within a fixed prefix, split continuations by their next block and compare final-answer rates; and P(answer = C | ⟨ pattern ⟩) for named patterns.
- Does the discourse structure of a trace predict where resampling moves the answer distribution? ReasoningFlow reports that the discourse graph and the mechanistic graph do not align; the behavioral graph measured here is the third.

Scope and constraints: one item (bat-and-ball with the "$1.00 more" premise deleted), one model (Qwen 3.6-27B via DeepInfra raw completions), budget $100 for new resampling, judge costs separate and small. Publishable at workshop or MATS scale if framed as the resampled-versus-observational test plus mediation. The nearest papers are dated May–July 2026; speed matters.

## 3. Documents and files (docs/shared unless stated)

| file | role | version | supersedes |
|---|---|---|---|
| 2026-09-14_action_summary_v1.md | this document: state, design, decisions, glossary | v1 = chat1 | findings_summary.md (2026-09-04) → archive/ |
| 2026-09-14_labeling_scheme_v1.md | the labeling scheme: Levels 1–3, applicability tests, nodes, openers, blocks, probability notation, open items (its Section 12) | v1 = chat7 | labeling_structure_reasoningflow_working_2026-09-14_v7.md (same content) |
| 2026-09-14_source_traces_labeled_v1.md | Claude's complete provisional labeling of both source traces, with nodes and blocks; the object of Kian's review | v1 = chat3 | labeled_sentences_nodes_blocks_c004_e036_2026-09-14_v3.md (same content) |
| 2026-09-14_source_traces_sentences_v1.md | the two source traces one sentence per line under the current numbering, with the old index next to each sentence and the old cut positions marked | v1 | source_traces_c004_e036_sentence_indexed_2026-09-09.md → archive/ (keeps the run's numbering, verified against prefix hashes) |
| docs/claude/STATE_2026-09-14_2.md | Claude's authoritative state file; read first in any new chat | dated | STATE_2026-09-14.md and STATE_2026-09-04.md → archive/ |
| archive/decided-mid-thought/ | the frozen submitted project, its runs, logs, and the raw sweep and resampling files (sweep_items_batball_2026-08-19_1623.jsonl, resample_cuts_2026-08-25_1503.jsonl) | frozen | — |

## 4. Background: results of the submitted study (frozen; details in the submitted repo)

Item and design: a famous problem with one premise deleted and an option menu that turns the two readings of "most likely" into answer letters; C ("not enough information, but most likely $0.05") versus E ("not well posed"). Instrument: truncate the thinking at sentence k, prefill the prefix into the model's thinking channel, sample 25 continuations at temperature 1.0, score the final letter (scorer v2.1, blind hand-check). Source traces: C-trace = sweep condition eval0_multi0, sample 2 (row 4 → c004); E-trace = same condition, sample 40 (row 36 → e036). Sentence numbers below are the run's.

- Finding 1, distributed commitment: P(C) rises from 0.12 (cut-0) to 0.60 at cut-44, 1.00 at cut-62, then 0.88–0.96; the largest single-sentence step is +0.28 (s60); a region [s30, s44] carries +0.48. Hypotheses 3.1a/3.1b (a localized jump ≥ 0.4 at the registered s*) failed. This has the same shape as Thought Branches' nudged reasoning in a different regime (no hint; underspecified item); it is a replication in a new setting, not a discovery.
- Finding 2, E is preset: P(E) ≥ 0.96 at every cut, including cut-0; the E answer is fixed before any thinking token and the E-trace's 247 sentences change nothing.
- Finding 3, post-saturation elaboration: 84.6% of the C-trace's characters are generated after P(C) has saturated (≥ 0.88 from s60 on). Neighbors: 41–52% of tokens after the "golden step" across five models (2605.17672); up to 87% after a "commitment boundary" found with early exit (2606.13603). Ours is distributional (resampled P(C)), theirs is read off the text.
- Finding 4, elicitation: the eval frame and the option menu shift the sweep's answer distribution (recorded as a finding, not a direction).
- Not tested: whether the reading of "likely" predicts the final answer with the prefix held fixed (the mediation question). The block-level design answers it.

## 5. Decisions log

- 2026-09-04 — Path 10 chosen (block-level map); directions (1/3) hedge readings and (3/3) early prediction absorbed into it.
- 2026-09-12 — Literature check done; ReasoningFlow adopted as the base scheme; other schemes crosswalked into it.
- 2026-09-13 — Combined labels allowed inside a sentence, no precedence order (assumption A1: narration and process agree at the coarse level, not necessarily the fine level). Edges not used.
- 2026-09-14 — Equation-end splitting rule approved; current numbering adopted (C 375 sentences, E 254); s* = C s67, E s69. Level 1 label "Fact" renamed "Knowledge" (Recall rejected: no precedent as a top-level label). Self-as-AI statements → Knowledge > self-knowledge. Node names X_m^k(n). Blind human labeling skipped for time; validation is Kian's face-validity review of the labeled traces. Option A versioning adopted; findings_summary.md renamed and restructured as this action summary.
- Pending (labeling scheme Section 12): combined sentences (keep all / keep the six real ones / drop); check-question scope threshold (none, 3, 5); E-trace tail (announce-output opens blocks or not; 37 vs 33 blocks); first intermediate conclusion of the E-trace (s41 or s99); cut placement (blocks, nodes, both); probability notation confirmation; transition counts.

## 6. Next steps

(1/5) Kian reviews 2026-09-14_source_traces_labeled_v1.md and returns disagreements as sentence index plus his label; Claude re-derives nodes, blocks and tables from the corrected labels, never by hand.
(2/5) Kian settles the pending decisions; each gets a changelog line in the labeling scheme.
(3/5) Claude writes the judge prompt from the labeling scheme and a script (API with a pinned model string at temperature 0, or `claude -p` under the Agent SDK credit); test on the two source traces; report judge-versus-Claude agreement per label (kappa, Jaccard) and the residue.
(4/5) Zero-cost pilot: the judge labels the archived continuations (13 C cuts × 25, 6 E cuts × 25, cut-0 × 25) and, optionally, the 44 sweep traces of eval0_multi0 for the corpus matrix.
(5/5) Pre-registration for the block-boundary resampling run (n per cut, thresholds, the null of no type dependence, the sequence test, cost within $100), then the run.

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
- block — the unit of the block-level design, defined precisely in
  docs/shared labeling_structure_reasoningflow (working version v7,
  2026-09-14), which supersedes the earlier phrase "hand-annotated logical
  unit". In short: sentences receive labels (Level 1 > Level 2 > Level 3,
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
- 2026-09-14 v1 (chat1) — Created from findings_summary.md: restructured around the current design (path 10), file inventory under the Option A convention, decisions log, next steps; submitted-study findings compressed into a background section; glossary carried over with the 2026-09-14 numbering and block-level entries.
- Inherited from findings_summary.md: 2026-09-04 — first confirmed version (submitted-project summary, follow-on directions, glossary seeded).
