# resample_blocks_2026-09-17_1759_strict

Derived from `runs/experiments/resample_blocks_2026-09-17_1759` by `scripts/s5_rescore.py` on 2026-09-19. Nothing in the registered run folder was changed.

This folder holds the stage-one run read with the strict rule (decision P6, 2026-09-19; departure from
pre-registration 3.7, logged in the run's DEPARTURES.md; reasons in docs/shared/2026-09-19_scorer_audit_v1.md):
a continuation has an answer only if it finished, and the answer is the letter on the last line of its reply.

- `continuations.jsonl`: the run's records with `letters` and `answer` under the strict rule, the registered
  values kept as `letters_v1` and `answer_v1`. The continuation texts are not repeated here; `cont_text_sha256`
  ties each record to its text in the registered file.
- `pcut.csv`: the run's table with the counts, P-hat, its interval and `stopped` recomputed.
- `rescore_changes.csv`: the 36 records whose answer changed. `rescore_summary.json`: counts under both
  readings and the checks made.
- The remaining tables, `stage1_summary.md` and the figures `figures/resample_blocks_2026-09-17_1759_strict_*.png` are the registered analysis
  (`scripts/s4_analyze.py`, unchanged) run on this folder with the run's own judge folder. The transition tables
  use no letters and are identical to the registered ones.
