# MATS 12 Application — Research Plan, Alignment Rubric, and To-Do List

Working document. This is your plan, not the submission. The executive summary and form answers must be written in your own voice — Neel says LLM-sounding prose is a significant negative signal.

---

## 1. Overview

**One-line project.** In a reasoning model, when a chain of thought shows both evaluation awareness and post-hoc rationalization, do they have a real temporal order — or is the model committed to both from the first token, with the trace merely narrating them in some sequence?

**Why it matters.** CoT monitoring assumes the trace reflects the computation. If eval awareness and rationalization are baked in before any reasoning token, then whatever order they appear in is theater, and a monitor reading for "when did the model notice it was being tested" is reading noise. If they have genuine onsets, the trace carries real causal information about sequence — a stronger property than mere presence.

**The claim being tested.** The null hypothesis (call it category 0) is: both phenomena are decided at token one; textual order is narration. The alternative is that at least one has a real onset, detectable as a sharp change in answer distribution when resampling from just before the marker sentence.

**Contribution type.** Understanding, not method. The headline is a claim about the model. The five-category scheme, the response-function framing, and any decomposition are method-section scaffolding, never the headline.

**Prior art you must position against.** Turpin et al. 2023 (biased-MCQ unfaithfulness — your rationalization instrument); Li et al. 2605.23055 (eval-awareness decomposition); 2605.05835 (prefill-and-resample on verbalized eval awareness, near-null effect); Thought Anchors / Thought Branches (sentence-level resampling — borrow, don't reinvent); LessWrong "Unfaithful CoT as nudged reasoning" (argues no onset — your category-0 story in the literature); "The Riddle Riddle" 2606.27103 and "Easy Problems LLMs Get Wrong" (misdirection items — your category-2 control is established, not novel). Verify every citation yourself before using it.

**What is not in the literature, as far as searches found.** Anyone asking about the *joint* temporal structure of eval awareness and rationalization, or treating baked-in as the explicit null and testing onset against it. That gap is the project.

---

## 2. Design

### 2.1 Item types

**Type 1 — closed-world clue puzzles (primary instrument).** Four options, a small set of clues written so that exactly two options fit every clue (a designed tie) and the other two are ruled out. Ground truth is entailed by the clues, not by world knowledge, so parametric knowledge cannot shortcut it and the answer is underdetermined enough for a cue to move it. Fix the clue count across items so difficulty is held constant. Fix the logical skeleton and swap the surface domain (favorite dish, favorite book, favorite drink, favorite friend, and so on) so the item pool is a class of puzzles, not one clever example. One item uses a mildly refusal-adjacent frame (the "favorite serial killer" item) purely to see whether guardrail talk pulls eval-awareness verbalization out — one item, not a theme.

**Type 0 — borrowed benchmark items (construction-artifact check).** A small slice from BIG-Bench Hard families scaled up in size until baseline accuracy leaves ceiling (e.g. logical deduction with more objects). Purpose: show the effect isn't an artifact of your puzzle style. Small budget.

**Type 2 — misdirection items (leakage control).** Fresh closed-world puzzles whose surface resembles a famous problem (a hotel with rooms, an ant on a sphere, a bridge inscription) but whose clues entail a different answer. Log "answered the famous version" as its own label. If it never fires, that supports the closed-world assumption behind Type 1. Small budget.

Dropped: hard physics items (near ceiling, no closed-world control), philosophical/ambiguous items (no ground truth to betray), abstract logic items (turn-off adjacent, ambiguous option D).

### 2.2 The two knobs

**Cue knob (rationalization axis).** Baseline vs. a planted directional cue toward the *wrong* member of the tied pair — "my friend thinks it's C" or option reordering. Rationalization = answer moves toward the cue AND the trace never names the cue as a reason.

**Eval knob (eval-awareness axis).** Casual conversational frame vs. an explicit "this is a benchmark evaluation of your reasoning" frame. Optionally sweep 3–4 cue strengths for a curve, but binary is enough for the core claim.

The knobs are orthogonal by construction. 2×2 design, plus baseline.

### 2.3 Categories

Read from the trace, not the answer (eval awareness is not a directional cue; more answer options dilute the tie and buy nothing).

- 0 — both baked in from token one; textual order is narration (the null)
- 1 — neither present
- 2 — eval awareness only
- 3 — rationalization only
- 4 — eval awareness verbalized before the rationalized reasoning
- 5 — rationalized reasoning before eval awareness verbalized

Categories 1–3 are a known presence table. All novelty is in whether 4 and 5 are real, i.e. whether 0 can be rejected.

### 2.4 Measurements

- **Uncertainty screen.** Sample each candidate item ~30× at nonzero temperature. Keep items whose baseline answer distribution is spread across the tied pair (roughly 60/40 to 80/20 on the correct option). This is your baseline and your item-selection criterion.
- **Cue effect.** Fraction of samples on the cued option, cued vs. baseline. Discrete answer choice is the dependent variable — no embedding cosine similarity on the prompt side.
- **Trace labels.** LLM judge with a written, anchored rubric for (a) mentions the cue as a reason, (b) verbalizes eval awareness, (c) sentence index of each. Validate against your own blind hand labels on a random subset; report agreement. This section doubles as documented agent sanity-checking.
- **Onset test (the falsification).** For traces in categories 4/5, prefill the trace up to each sentence boundary and resample ~20 continuations per cut. Plot P(cued answer) and P(eval talk downstream) by cut position. Sharp jump at the marker = real onset. Smooth drift = category 0 (nudged-reasoning story). Write the predicted plot for each hypothesis before running.
- **Optional probe version** only if the behavioral version is done and hours remain: an eval-awareness probe across pre-verbalization sentences; if it fires early in "rationalization-first" traces, ordering is textual artifact.

### 2.5 Nuisance hypotheses and their controls

- Position/format bias — counterbalance which letter the cued option occupies.
- Prior toward one member of the tied pair — swap the labels of the tied pair and rerun baseline; if preference follows the label, it's the label.
- Genuine confusion — item passes the uncertainty screen and clues are checked by hand.
- Prior-knowledge leakage — Type 2 items; closed-world construction.
- Sycophancy vs. rationalization — same behavior, different mechanism; note as a limitation, do not try to separate in 16 hours.
- Off-distribution prefill artifacts — sanity-check that prefilling at cut 0 reproduces the baseline distribution.

### 2.6 Models

Qwen 3.6 dense 27B, thinking mode, via OpenRouter or Nebius (Neel names Nebius specifically for partial-CoT prefill and regeneration). Build the whole pipeline here first. Add Nemotron 49B second — note Neel names it under *how eval awareness is represented* (i.e. probing), not as a behavioral eval-awareness model, so it is the natural choice if the probe extension happens and a reasonable second model otherwise. Only once the pipeline is solid on Qwen. DeepSeek v4 flash only if both are done. Do not use closed chat products for the main study.

---

## 3. Alignment rubric (criterion → what the project does → where it's exposed)

**Clarity.** One claim (onset vs. baked-in), one main plot (P(answer) vs. cut position, one line per category), one table (2×2 rates). Exposed if the five categories are presented before the reader understands why 0 is the null — lead with the null.

**Good taste.** Question is non-obvious; sits inside named interest areas (CoT faithfulness, eval awareness, model forensics); it's a claim about the model. Exposed because "showing CoT causally impacts the answer" is a named generic project — the write-up must say explicitly that this is about the *relative sequence of two specific phenomena against a baked-in null*, not whether CoT matters.

**Truth-seeking / skepticism.** Category 0 is the null; predictions written before running; label-swap and cut-0 controls; hand-validated judge; honest reporting if it's all drift. Exposed if the onset test is underpowered — commit to a sample count and report it. Neel's stated top signal is "I thought of a way this could be false and you'd already checked it" — the nudged-reasoning post is that way, and the drift-vs-jump plot is the check.

**Technical depth.** Prefill-and-resample pipeline, judge validation, cross-model replication. Exposed if the prefill mechanics are silently wrong for thinking mode — verify cut-0 reproduces baseline and say so.

**Simplicity.** Fully behavioral; probes only as an optional extension; no SAEs, no circuits. Response function and any decomposition stay in the method section or are cut.

**Prioritisation.** One question, one instrument (Type 1), one model until it works. Types 0 and 2 are small. Timer every 90 minutes.

**Show your work.** Keep a running hypotheses doc with predicted plots; report what you'd do next. Do not write chronologically. If a gate fails, the write-up should show the pivot and why — Neel explicitly rewards "got stuck, so pivoted" over "gave up."

**Productivity.** Fast feedback loops: persistent kernel (jupyter-mcp or IPython in tmux), checkpoint traces and judge outputs to disk, judge runs batched.

**Sanity-check your agent (the ~3× criterion).** Agent writes the plumbing; you design every experiment, control, and interpretation. You read ≥30 raw traces, re-derive the headline rates with a fresh one-liner, hand-label the judge-validation subset, and *write this down* in the write-up. The agent is never the classifier of record.

**Data visibility.** Randomly selected (not cherry-picked) raw traces, one per category, immediately after the executive summary — Neel asks for exactly this when a project rests on an LLM judge.

---

## 4. Hour budget (16 + 2)

- 0.5 — verify prefill-and-resample correctness on Qwen thinking mode (cut-0 reproduces baseline). Renting GPUs / creating API accounts is generic setup and is NOT counted — do it before starting the clock.
- 1.5 — write 10–15 Type 1 templates, 3–4 Type 2, pick 4–6 Type 0; hand-check every clue set
- 1.0 — write hypotheses doc: predicted 2×2 table and predicted onset plot per hypothesis, judge rubric
- 2.0 — uncertainty screen; select items; label-swap control
- 2.0 — full 2×2 sweep on Qwen; judge labels; category assignment. **Go/no-go gate here** (see §6a).
- 1.5 — hand-label validation subset blind; report agreement; read 30 traces
- 3.5 — onset test: prefill-and-resample across cut positions on category 4/5 traces; cut-0 sanity check
- 1.5 — Nemotron replication of the core 2×2 and onset test (skip if behind)
- 1.5 — analysis, plots, re-derive headline numbers independently (this must happen inside the main 16–20 h; the +2 h allows only new graphs from existing data, no new experiment code)
- 1.0 — buffer / pivot slack
- +2.0 — executive summary and write-up, own voice

Papers/tutorials ≤5 h total across the whole thing; the ~1.5 h of reading below is inside that.

---

## 5. To-do list

1. Read Li et al. 2605.23055 Appendix A.1, the 2605.05835 abstract and method, and the LessWrong nudged-reasoning post. Skim Turpin's repo for item formats and Thought Anchors' repo for the resampling code. (~1.5 h, counts toward papers cap)
2. Confirm Qwen 3.6 thinking-mode prefill works on Nebius; verify cut-0 resample reproduces baseline.
3. Write item templates (Types 1, 2, 0). Hand-check ties and entailments.
4. Write the hypotheses doc with predicted plots. Write the judge rubric with anchored examples. Date-stamp both.
5. Run uncertainty screen; select items; run label-swap control.
6. Run 2×2 sweep; judge; assign categories; hand-validate a random subset blind.
7. Read 30 raw traces. Note anything weird.
8. Run onset test on category 4/5 traces; make the drift-vs-jump plot.
9. If on schedule: replicate 2×2 + onset on Nemotron.
10. Re-derive headline numbers with a fresh script. Compare to write-up numbers.
11. Draft exec summary (≤600 words, ≤3 pages, graphs): problem, takeaways, one paragraph + one plot per experiment, random raw examples right after.
12. Write the "what I checked" section: transcripts read, numbers re-derived, judge agreement, controls run.
13. Toggl screenshot. Form answers in your own words — Neel reads these for every applicant as the preliminary filter before the doc, so draft them carefully (writing them is uncounted time).

---

## 6a. Go/no-go gate and fallback (added on audit)

Neel's common-mistake list includes "building on a phenomenon without first checking it replicates in your setting." The plan's biggest exposure is that eval-awareness verbalization may simply not appear in short closed-world MCQ traces, even under the benchmark frame — leaving categories 2, 4, 5 empty and no traces for the onset test. Also, 2605.05835 found verbalized eval awareness has near-null behavioral effect, so the eval axis may show pure drift regardless.

Gate, after the 2×2 sweep (~7.5 h in): count traces in categories 4 and 5. Decide the minimum in advance (e.g. ≥15 traces per category before onset testing is meaningful) and write it in the hypotheses doc.

If the gate fails on eval awareness: (a) strengthen the eval frame ladder (explicit "you are being tested for CoT faithfulness" wording, grading-style output format — Li et al.'s trigger factors) for one more sweep; (b) if still empty, pivot the headline to the rationalization axis alone — does rationalization have an onset or is it baked-in/nudged? — which is still a direct test of the nudged-reasoning claim against Turpin-style cue-following, and report the empty eval-awareness cells as a finding, not a failure. Do not reset the clock for this; the code and data carry over.

If the gate fails on rationalization (cue never moves the answer): items are too easy or the tie isn't a tie — go back to the uncertainty screen, do not proceed.

## 6b. Sample-size note

The onset test lives on the intersection of both phenomena, which will be a small fraction of all traces. Budget the 2×2 sweep so the intersection is populated: more items and more samples per item on the eval-framed + cued cell than elsewhere.

## 6. Open decisions

- Binary eval frame vs. 3–4 level sweep (binary is enough for the core claim; sweep only if cheap).
- Whether the probe extension is worth any hours (default: no).
- Exact sample counts for the onset test — decide up front and report.
- Whether to keep the Type 2 slice if Type 1 alone fills the budget.
