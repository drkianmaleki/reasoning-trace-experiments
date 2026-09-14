# Findings summary — Decided Mid-Thought (as submitted to MATS 12.0)
Status: LIVING DOCUMENT, updated in place. Last updated 2026-09-04 (confirmed by Kian). Git history is the archive; see Changelog at the end.
Sources: docs/log_2026-08-30.md (freeze log), canonical rescored tables,
the run files, the write-up. Nothing here goes beyond those.

## Question
Where does a reasoning model commit to its final answer inside its chain of
thought — at an identifiable point mid-trace, or is it fixed before any
thinking token (the pre-registered null)? The "point" may be a single
sentence or a block of sentences (a logical block, such as a complete
derivation or argument); the submitted study tested the single-sentence
version, and sharpening the block-level version is future work.

## Method
- Model: Qwen 3.6-27B, thinking mode, temperature 1.0. Single model, single
  item (a bat-and-ball problem with one premise deleted — underspecified so
  no answer is overdetermined by model weights).
- The exact prompt used for all resampling calls (single-select,
  eval-frame off; verbatim from the run's prefixes file):

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

  Both source traces come from the same condition of the 08/19 sweep
  (condition eval0_multi0, i.e. this prompt): the C-trace is sample 2, the
  E-trace is sample 40, both from sweep_items_batball_2026-08-19_1623.jsonl.
  See "record IDs" in the glossary for the ID numbers attached to them.
- Instrument: truncation-and-resampling. Record thinking traces, cut at
  sentence boundaries, prefill the prefix into the thinking channel, sample
  n = 25 continuations per cut, measure the answer distribution.
- Infrastructure: sweeps via OpenRouter (DeepInfra pinned, fallbacks off);
  resampling via DeepInfra's raw completions endpoint directly, because
  OpenRouter discards thinking-channel prefills.
- Pre-registration frozen before any resampling run (docs/
  mats12_research_plan.md + plan_amendment.md); s* values committed blind
  (C-trace s60, E-trace s63); one pre-authorized scorer revision (v2.1) was
  triggered by a blinded 20-record hand-check and applied programmatically;
  all 35 changed records human-validated. Canonical numbers come from the
  rescored tables. Analysis frozen 2026-08-30.

## Registered verdicts
- Null (category 0, "flat within ±δ_base of cut-0", δ_base = 0.15): REJECTED
  in both arms. C-trace: 3/25 at cut-0 rising to 25/25 at cut-62 (Fisher
  p < 1e-8, post-hoc support). E-trace: formally exceeds the band but had
  only 0.20 headroom; read as ceiling drift, functioning as the control arm.
- Hyp 3.1a (localized jump in the C-trace at registered s* = s60): FAILS.
  P(C) after s* clears 0.7 (0.88), but cut-59 is 0.60 (not ≤ 0.35) and the
  step is +0.28 (< Δ_jump = 0.4).
- Hyp 3.1b (symmetric jump in the E-trace at s* = s63): FAILS. P(E) ≥ 0.96 at
  every cut; no reversion toward the 0.80 baseline was possible.
- Jump-anywhere check: maximum adjacent single-sentence change anywhere in
  either arm is +0.28 (C-trace, s60). No sentence-level jump ≥ Δ_jump exists.
- Amendment-2 region contrast (pre-specified bisection), C-trace only: the
  region s30–s44 — sentences 30 through 44 of the C-trace — carries
  Δ = +0.48 (P(C) = 0.12 at cut-29 → 0.60 at cut-44; Fisher p ≈ 8e-4,
  post-hoc support). It is the only change in the study clearing Δ_jump.
  Attributed to the region, never to a sentence, per the amendment's fixed
  rule.
- Hyp 3.2a (eval-frame, answer level): directionally consistent on sweep data
  (C-involving 12/48 eval-off vs 5/50 eval-on, multi-select conditions),
  underpowered, one item — no confirmatory claim. 3.2b (mechanism) not run;
  cut for time.

## Headline findings
1. Commitment to the minority answer (C) is DISTRIBUTED and NON-MONOTONIC:
   constructed in-trace from 0.12 to 1.00, with no localized jump, one
   threshold-clearing pre-specified region (C-trace s30–s44), and saturation
   from s60.
2. Default/minority asymmetry: the default answer (E) is ~80% set before any
   thinking token — prompt-determined — while C is built in the trace.
3. Post-saturation elaboration: 84.6% of the C-trace's characters are
   generated after the registered s* (s60), by which point P(C) ≥ 0.88 and
   never falls; the model keeps thinking for five sixths of the trace without
   changing where it lands.
4. From the wider sweep: answers are elicitation-governed — identical
   reasoning under three prompt formats yields three different answer
   distributions, while trace-level behavior (premise import, catch rate,
   import position) is invariant across conditions. (Recorded finding; not a
   current research direction.)

## Scope limits
The study covers a single model and a single item, so nothing here
establishes generality across models or problems. All evidence is
behavioral: it comes from the text of traces and continuations, and no
claim is made about internal mechanisms. The one positive result concerns
the C-trace only and is attributed to the whole span of sentences 30
through 44 of that trace: the answer distribution changes across that span,
and the design cannot say at which sentence within it. The mediation
question — whether the reading of "likely" that a continuation adopts
predicts its final answer, with the prefix held fixed — was not tested and
remains open. Both localization hypotheses failed as registered; the
positive result of the study is the pre-specified Amendment-2 region
contrast.

## Follow-on directions (updated 2026-09-03; supersedes the freeze-log list)
Near-term, in working priority order:
1. Rewriting the answer options as controlled pairs. Build two versions of
   the item that are identical except for the wording of option C: in one,
   "most likely" can only carry the everyday meaning (the intended answer is
   $0.05); in the other, only the mathematical meaning (no single value has
   the highest probability). Same arithmetic, same missing premise. If the
   answer distributions or trace lengths change with the wording, the
   ambiguity of "likely" is doing causal work; if nothing changes, the
   missing premise alone explains the behavior. The same pairs test whether
   the +0.28 step at the "likely" sentence recurs or was specific to this
   item.
2. A proper definition of "localized" at the block level (logical blocks:
   complete derivations or argument units, hand-annotated blind before any
   resampling), replacing the single-sentence jump criterion; this also gives
   the box toy model its natural statement unit, testable by shuffled
   resampling (primacy prediction: rearranging early statements should move
   answer distributions far more than rearranging late ones).
3. Early-trace predictability: Kian predicts each trace's final answer blind
   from only the first k sentences; scored against actuals. Motivated by the
   exploratory observation that E-traces share a near-identical opening
   template while C-traces open in three modes.
4. Terminology: maintain the glossary below as the single canonical
   vocabulary; extend it with each new design before running anything.

Deferred (much later): 3.2b eval-frame resampling; a second underspecified
item; a second model; activation probes for the pre-token disposition.

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
- cut-k — the prefix consisting of sentences s0 through s_k, i.e. the trace
  truncated after sentence s_k (k+1 sentences). Exception by definition:
  cut-0 is the EMPTY prefix (no thinking text at all), not "s0 alone". This
  irregularity is a lesson for future designs: define cut-k as exactly k
  sentences so that cut-0 = empty falls out naturally.
- prefix — the trace text up to and including the cut sentence (the content
  of cut-k).
- prefill — the same prefix placed inside the model's thinking channel so
  that generation resumes from that point. Concretely, the request template
  is: user turn = the prompt (item); assistant turn = "<think>\n" + prefix.
  The prompt goes in the user turn; the prefix goes inside <think>.
- continuation — one sampled completion from a prefill (n = 25 per cut),
  including the rest of the thinking and the final reply.
- s* — the pre-registered sentence where the trace interprets "likely"
  (C-trace s60, E-trace s63), fixed by hand before any resampling. The
  asterisk is standard notation for a distinguished value ("the special
  sentence"). It is the notation of the submitted study; under a
  block-level design the analog would be a distinguished block, b*.
- region — a pre-specified span of consecutive sentences tested as a unit,
  written s30–s44 (= sentences s30 through s44, the sentences added between
  cut-29 and cut-44). Results are attributed to the whole region, never to
  a sentence inside it.
- block — proposed future unit: a hand-annotated logical unit of a trace
  (a complete derivation, a complete argument). Attribution at block
  resolution, never finer.

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
- 2026-09-04 — First confirmed version: submitted-project summary, updated follow-on directions, glossary seeded.
