# To-do — wrap-up (2026-08-26 → submission)

Scope decision on record (08/26): judge/labeling phase → future work. This is a
proof-of-idea artifact: pre-registered test, honest verdicts, one designed next step.
Deadline: submit Wed Sept 3 (hard: Fri Sept 4, 11:59pm PT).

## TONIGHT (≈15 min of your attention, then the machine works while you sleep)

1. Place the two updated files:
   - plan_amendment.md → docs/   (now contains Amendment 2: bisection cuts s15/s29/s44)
   - resample_cuts_v3.py → scripts/resample_cuts.py   (adds the 3 cuts; pins model slug)
2. Commit BEFORE the run — the timestamp is the pre-specification:
       git add docs/plan_amendment.md scripts/resample_cuts.py runs/
       git commit -m "Amendment 2 (s0-s58 bisection cuts, pre-run) + Phase-1 run outputs"
       git push
3. Sanity: python scripts/resample_cuts.py --dry   → must print 20 prefixes / 500 calls.
4. Launch and go to sleep:
       python scripts/resample_cuts.py --yes --resume runs/resample_cuts_2026-08-25_1503
   What it will do: reuse the on-disk gate, fire ONLY the 79 missing calls
   (3 new cuts x 25 + 4 cut-67 top-ups), append to the same jsonl, rewrite the
   summary CSV. Expect ~1–1.5 h runtime, ~$3–4. Early cuts produce very long
   continuations — lengths of 30–60k chars are normal, not a malfunction.

## TOMORROW — analysis close-out (target ≤ 2.5 h counted)

5. Morning check (5 min): tail of console or _log.txt; summary CSV should show
   succeeded=25 for all 20 prefixes. If any short: rerun the same --resume command.
6. YOUR re-derivation (~30 min, Neel criterion, my tallies do not count):
   fresh one-liners from the raw jsonl(s) reproducing: the 194-sweep cell counts,
   the resampling P(C)/P(E) per cut, and the new s15/s29/s44 points. Record the
   commands + outputs in the day's log.
7. Pre-registered hand-check (~30 min): 20 random continuations (seed recorded)
   read against the regex scoring. Ask Claude for the seeded, blinded sheet
   (thinking-only, opaque IDs) — then verify letters yourself. Any regex revision:
   once at most, per §5.
8. Premise-import provenance (5 min): one log sentence on how 194/194 was counted
   (hand vs script); if script, spot-check 5 seeded traces.
9. Read the bisection result with Amendment-2 rules (regions, not sentences);
   update the curve plot (ask Claude); write the day's log entry: verdicts
   (3.1a fail, 3.1b fail, category 0 rejected, drift), the two headline findings
   (default/minority asymmetry; post-saturation token redundancy ~84%), bisection
   localization, ?-counts disclosed (25/425, clustered at 058/059), cut-67 ERR:4
   disclosed. ANALYSIS FREEZE after this — no new numbers past this point.

## WRITE-UP (write-up window: ≤ 2 h, graphs from existing data only)

10. Figures: final two-panel curve (+ bisection points), maybe the length-asymmetry
    plot. Random seed-drawn raw examples to place right after the exec summary.
11. Exec summary ≤600 words / ≤3 pages — YOUR voice only (Claude: spelling only).
    Claim ladder to respect: demonstrated (distributed commitment; E prompt-
    determined vs C trace-constructed; ~84% post-saturation; ambiguity-zone
    pathology; C-length effect) / hypothesized-with-designed-test (register/"likely"
    mediation via cut058-059 labeling + minimal-pair rewrite) / future work
    (labeling, 3.2b, more items, models). "Largest located causal effect," never
    "decides." Cite: Thought Anchors (sentence-level counterfactuals), Thought
    Branches (resampling trees, diffuse influence), Riddle Riddle (VERIFY 2606.27103
    before citing), AmbiEnt (ambiguity recognition backdrop).
12. "What I checked" section from logs + temp-log A/E: gate, re-derivations,
    hand-check, disclosed losses (six sweep samples; four cut-67 errs), harness
    probes.
13. Form answers (uncounted, your voice), Toggl screenshot, final commit.
    Temp-log disposition: promote A/B/D/E items into the final dated log, then
    archive the temp file to junk/.

## Standing rules
- Nothing new gets measured after step 9 except by written amendment (there is no
  budget or calendar for one — default: no).
- Every citation verified before it enters a draft.
- Claude drafts nothing in the exec summary or forms; asymmetric division of labor
  is itself evidence and is documented in the log.
