# log_temp_2026-08-23_session-notes.md — TEMPORARY
(Holding file. Items here are unresolved notes from the 08/23 session-start verification.
Each item is to be resolved or promoted into a dated permanent log entry later, once more
results are in. This file is not part of the append-only log series and may be deleted
after its contents are dispositioned. Do not cite it in the write-up.)

## A. Verified this session (no action needed, recorded for the "what I checked" section)
- A1. Pre-registration integrity: repo `docs/log_2026-08-22.md` is byte-identical to the
  copy in project knowledge (checked by diff). One authority, no divergence.
- A2. Project knowledge upload: `log_2026-08-22.md` IS present in project knowledge —
  resolves the open verification item in log_2026-08-23.md ("as of this session it was
  not findable there").
- A3. Sweep numbers re-tallied independently from
  `runs/sweep_items_batball_2026-08-19_1623.jsonl` (raw jsonl, fresh script, not the
  summary CSV). All match the recorded numbers:
  - Records: 194 total; per cell 50 (eval1_multi1) / 50 (eval1_multi0) / 50 (eval0_multi1)
    / 44 (eval0_multi0).
  - Per-cell answer distributions:
    - eval0_multi0: E 39, C 4, unparsed 1
    - eval1_multi0: E 46, C 4
    - eval0_multi1: E 36, C 5, "C,E" 7, unparsed 2
    - eval1_multi1: E 45, "C,E" 5
  - Derived: C-involving 25/194; multi-cell eval effect C-involving 12/48 usable
    (eval0) vs 5/50 (eval1). Matches log_2026-08-22.md and the repo README.
  - NOTE: this re-tally was done by Claude, not the user. It does NOT count as the
    user's own re-derivation of headline numbers required by Neel's sanity-check
    criterion. User re-derivation with a fresh one-liner still owed before write-up.
- A4. C-trace supply gate (log_2026-08-22.md §5): PASSES. Single-select cells contain
  8 C-traces (4 in eval0_multi0, 4 in eval1_multi0) >= 2 required. Trace selection can
  proceed from single-select cells; no fallback to multi-select needed.

## B. Discrepancies to fix later (before write-up; none block the resampling step)
- B1. Filename mismatch, project instructions vs repo: instructions cite
  `docs/preregistration_2026-08-22.md` and `docs/plan_amendment.md`. Neither filename
  exists. The frozen pre-registration lives at `docs/log_2026-08-22.md` (per the 08/23
  naming decision). Fix direction to decide later: update the project instructions
  wording, OR add a pointer file in the repo. Do not rename the frozen file.
- B2. [RESOLVED 2026-08-25: docs/plan_amendment.md written (Amendment 1) and committed pre-run.] Plan amendment file missing entirely: `plan_amendment.md` is in the repo neither
  under docs/ nor anywhere else, and log_2026-08-23.md already lists "plan amendment
  possibly not appended" as a debt. Still outstanding. The amendment template exists
  outside the repo (see memory/handoff); needs to be filled and committed.
- B3. runs/README wording error: the sweep note says the six failed eval0_multi0 calls
  "left no trace." Not exactly true — the jsonl has no records for them, but
  `sweep_items_batball_2026-08-19_1623_summary.csv` tallies them as ERR: 6. Correct
  statement: failures were counted in the summary tally but produced no jsonl records
  and no log file. One-sentence correction to runs/README later; also fold into the
  next permanent log since logs feed the report.
- B4. Standing debt reconfirmed: `sweep_2x2.py` writes records only on success and
  keeps no file log. Patch (write `_log.txt`, attempted AND succeeded counts per cell)
  required before ANY rerun of the sweep. The new resampling script must have this
  logging from the start (already in its requirements list, log_2026-08-23.md item 2).
- B5. log_2026-08-23.md exists in project knowledge but not in repo docs/. Decide later
  whether the repo docs/ should carry all dated logs or only the frozen
  pre-registration; commit accordingly.

## E. Harness findings and run stubs (added 2026-08-25, pre-run)
- E1. Thinking-prefill probes (scripts/probe_prefill.py .. 4): OpenRouter chat prefill
  discarded (restarts); OpenRouter /completions chat-emulated (mid-word prefix restarted;
  channel-split responses); DashScope Partial Mode excludes thinking mode; DeepInfra
  DIRECT /v1/openai/completions verified as true raw continuation. Full detail in
  docs/plan_amendment.md Amendment 1 §3.
- E2. Continuation proof artifact: at T=0 a prefix cut mid-word ("...accurate desc")
  continued with a near-miss completion ("rtiption of the situ...") — off-token-boundary
  seam artifact; impossible under a restart. Real cuts are at sentence boundaries where
  this artifact does not arise.
- E3. Incidental contamination observation (OpenRouter probes): with the truncated trace
  visible as context text but NOT continued, 2/2 samples answered C (cell baseline ~0.09).
  Suggestive that visible-prefix conditioning moves answers; not part of the experiment.
- E4. Run stubs in runs/ from 2026-08-25: resample_cuts_2026-08-25_1323.jsonl (+prefixes)
  and resample_cuts_2026-08-25_1440_prefixes.json (no jsonl). Contents to be verified and
  dispositioned in the next dated log: expected = smoke-only records (seq 900) in 1323 and
  an aborted launch for 1440. If 1323 contains seq<900 records, disclose in the run log.
- E5. Smoke mechanism assertion loosened (2026-08-25) from exact-string ("ription") to
  continuation-vs-restart (lowercase continuation, no restart markers) after E2 showed
  exact spelling is not guaranteed at off-token seams. Change made BEFORE any budgeted run.

## C. Disposition rule
When each item is resolved, note the resolution in the next dated permanent log
(log_2026-08-XX.md) with a reference to this temp file, then delete or archive this
file to junk/.
