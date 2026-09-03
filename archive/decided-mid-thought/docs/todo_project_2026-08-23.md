# To-do — rest of project (as of 2026-08-23)

Budget: ~11 h experiment/analysis time + 2 h write-up window. Clock via Toggl.
Submission target: Wed Sept 3 (deadline Fri Sept 4, 11:59pm PT; extension to Sept 11 exists
but is not the plan). Uncounted time: form answers, generic setup, repo hygiene.
Authority for all thresholds and gates: docs/log_2026-08-22.md (frozen). Do not restate
hypotheses from memory — read that file before each work session.

## Phase 1 — Resampling for hyp 3.1 (the core experiment) — ~4.5 h

1. [0.5 h] Trace selection BY HAND (user only). 1 C-trace + 1 E-trace from the
   single-select cells (gate passed: 8 C-traces available). Read candidates in full,
   pick, identify s* (the "likely"-interpretation sentence). Fill the §5 blanks in
   log_2026-08-22.md: run file / condition / sample / s* index. This is the one
   permitted edit to the frozen file. MUST precede any resampling call.
2. [0.25 h, mostly uncounted] Check OpenRouter balance. If < $16, switch to the 5-cut
   fallback (~$10) per prereg §4. Verify DeepInfra accepts thinking-channel prefill
   with a 2–3 call smoke test BEFORE spending budget.
3. [1.25 h] Write resampling script. Requirements (log_2026-08-23 item 2):
   - prefill inside the thinking channel; trim the "Ready/Proceed" tail before
     sentence splitting;
   - cuts = cut-0 + 3 sentence boundaries before s* + 3 after; n = 25 per cut;
   - writes _log.txt; records attempted AND succeeded counts per cut (the sweep_2x2
     logging debt must not recur);
   - per-record prompt field authoritative, as in the sweep files.
4. [1.0 h] Run: 2 traces x 7 cuts x 25 = 350 calls ≈ $14 (or 5-cut fallback ≈ $10).
   Monitor the log for silent failures.
5. [1.5 h] Analysis. P(answer | cut) per trace against §5 thresholds:
   cut-0 gate ±0.15 on P(E) (if it fails, nothing downstream is interpreted — stop
   and debug the prefill); jump = Δ ≥ 0.4 between adjacent cuts; drift; flat.
   Hand-check 20 randomly selected continuations (seed recorded) against the regex.
   Make the drift-vs-jump plot. Write the reading in the day's log.

DECISION POINT after Phase 1: jump confirmed → more items only if hours allow;
drift/flat → category 0 is the finding, title flips to the hedged alternative,
proceed straight to validation and write-up. Either result is reportable.

## Phase 2 — Judge, validation, sanity-check evidence — ~3 h

6. [0.75 h] Judge rubric, user-authored, with anchored examples: (a) premise import,
   (b) interpretation-of-"likely" sentence and its index, (c) eval-awareness talk.
   Date-stamp it.
7. [0.75 h] Run the judge over the relevant trace pool; batch the calls.
8. [1.0 h] Blind hand-labeling by user of a random subset (~30 traces, seed recorded);
   compute agreement; read raw traces beyond the subset toward the ≥30-traces
   criterion (much of this already done informally — count and record what's left).
9. [0.5 h] User re-derives headline numbers with a fresh one-liner (sweep numbers AND
   resampling numbers). Claude's 08/23 re-tally does not count. Record in log.

## Phase 3 — Optional extensions, only if ≥2 h remain after Phase 2 — 0–2 h

10. hyp 3.2b resampling (same pre-s* prefix, eval sentence on/off) — prereg'd as
    optional; cheapest meaningful extension.
11. Additional item (second underspecified famous problem) only if 3.1 jumped and
    both 9 and 10 are done. No new item types, no second model, no probes.

## Phase 4 — Analysis freeze and write-up — ~1.5 h counted + 2 h window

12. [0.5 h] Final plots and numbers inside counted time (write-up window allows new
    graphs from existing data only, no new experiment code).
13. [1.0 h] "What I checked" section from logs + temp-log section A: traces read,
    numbers re-derived, judge agreement, controls (cut-0 gate, elicitation-dependence
    reported as a result), the six lost samples disclosed.
14. [+2 h window] Executive summary ≤600 words, ≤3 pages, graphs; random (seed-recorded,
    not cherry-picked) raw examples immediately after the summary; honesty framing per
    project instructions (Riddle Riddle owns misdirection items — verify 2606.27103
    before citing; Thought Branches + nudged reasoning own "hints are diffuse";
    resampling shows "this sentence mattered," not "when the model first knew").
    USER'S VOICE ONLY. Claude may spell-check, never draft.

## Parallel track — uncounted, spread across days

15. Form answers, user's voice, drafts from ~Aug 30. These are Neel's preliminary
    filter — treat with the same care as the doc.
16. Verify every citation before it enters any draft (Riddle Riddle top of list;
    ≤5 h paper cap applies, ~most already spent).
17. Repo/docs hygiene from temp log section B: plan_amendment.md written and
    committed (B2); project-instructions filename fix (B1); runs/README ERR-tally
    correction (B3); decide docs/ log policy (B5); patch sweep_2x2.py logging before
    any rerun (B4).
18. Toggl screenshot saved before submission.

## Hour ledger check

Phases 1+2+4(counted) ≈ 9 h against ~11 h remaining → ~2 h true slack, which is
what Phase 3 may consume. If Phase 1 overruns by more than 1 h, cut Phase 3
entirely and protect Phase 2 — validation evidence is worth more to the
application than an extra experiment.
