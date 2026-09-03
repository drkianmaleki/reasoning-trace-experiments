# runs/ data dictionary and provenance

All prompts are recorded in full in each row's `prompt` field. **The recorded
`prompt` field, not the current text of the producing script, is the
authoritative record of what was asked** — scripts have been edited since
some of these runs were made. This applies most strongly to
`scripts/baseline_levels.py` (see the caveat column below) but is the general
rule for every file in this directory.

## File → script → items → run mapping

| file | producing script | items file | n | conditions | date |
|---|---|---|---|---|---|
| `batball_underspec_baseline.jsonl` | an earlier version of `scripts/baseline_levels.py` — schema (`sample/level/final/finish/provider/prompt/trace/reply/usage`) does not match the current script's output at all; superseded by the multi-select scheme below. Per-record `prompt` is authoritative. | none (item hardcoded in script) | 20 | single condition, free-text answer scored to a `level` | 2026-08-19 |
| `batball_underspec_multi_baseline.jsonl` | `scripts/baseline_levels.py` (current version, schema matches) — script was edited after some of these samples were recorded: the single-item question text and the option menu (`OPTIONS`) have since changed. Per-record `prompt` is authoritative, not the current `QUESTION`/`OPTIONS` constants. | none (item hardcoded in script) | 61 | single condition, multi-select letters | 2026-08-19 |
| `sweep_items_batball_2026-08-19_1620.jsonl` + `_summary.csv` | `scripts/sweep_2x2.py --smoke` | `items/items_batball.csv` | 1 per condition (4 total) | eval1_multi1, eval1_multi0, eval0_multi1, eval0_multi0 | 2026-08-19 16:20 — **smoke/aborted test run, not a headline result** |
| `sweep_items_batball_2026-08-19_1623.jsonl` + `_summary.csv` | `scripts/sweep_2x2.py -n 50` | `items/items_batball.csv` | 50 per condition target (194 recorded: 50/50/50/44 — eval0_multi0 is 6 short) | eval1_multi1, eval1_multi0, eval0_multi1, eval0_multi0 | 2026-08-19 16:23–18:00 — **full sweep, main result** |
| `items_gpqa_physics_conceptual_raw.jsonl` + `_summary.csv` + `_log.txt` | `scripts/screen_items.py` (defaults: n=12, phase=2, lo=0.30, hi=0.90) | `items/items_gpqa_physics_conceptual.json` | 12 per item x 23 items = 276 | baseline only — every item's baseline P(correct) was 1.0, outside [0.30, 0.90], so 0 items qualified for phase 2 cue conditions | 2026-08-17 23:51 – 2026-08-18 03:16 |

**Sweep note:** the `eval0_multi0` cell in the full sweep contains 44
samples, not the intended 50. `sweep_2x2.py` (this version) wrote a record
only on success and kept no console log, so the six failed calls left no
trace. Analyses use the 44 usable samples; the shortfall is not believed to
bias the distribution but is recorded here for completeness.

**GPQA note:** this is the ceiling-screen negative result referenced in
`docs/`: 23 items, 248/248 valid (non-truncated) samples answered correctly.
The remaining 28 of 276 samples hit the token limit before answering
(`finish_reason="length"`) and are excluded from the correctness denominator,
recorded as `TRUNC` in the summary tallies.

## Data dictionary

### Sweep files (`sweep_items_batball_*.jsonl`)

| field | meaning |
|---|---|
| `item_idx` | 0-based index of the item within the items CSV |
| `condition` | `eval{0,1}_multi{0,1}` — eval-frame on/off x multi-select on/off |
| `sample` | 0-based sample index within (item, condition) |
| `letters` | option letter(s) parsed from the `Answer: X` line |
| `chosen` | option text(s) corresponding to `letters` |
| `eval_frame` | bool — whether the eval-benchmark framing sentence was prepended |
| `multi` | bool — whether the prompt allowed picking more than one letter |
| `finish` | API `finish_reason` (e.g. `stop`, `length`) |
| `provider` | backend that served the request (routing pinned to DeepInfra, no fallback) |
| `trace_len` | character length of the extracted thinking trace |
| `options` | `{letter: option text}` for this item |
| `prompt` | full prompt text sent to the model — authoritative |
| `trace` | extracted chain-of-thought / reasoning text |
| `reply` | extracted final reply (post-thinking) text |
| `usage` | token/cost usage dict returned by the API |

### Baseline files — different, smaller schemas

`batball_underspec_multi_baseline.jsonl` (current scheme): `sample`,
`letters`, `finish`, `provider`, `trace_len`, `prompt`, `trace`, `reply`,
`usage` — same meanings as above; no `item_idx`/`condition`/`options` because
the item and condition are fixed (single hardcoded item, no items-CSV).

`batball_underspec_baseline.jsonl` (older, superseded scheme): `sample`,
`level`, `final`, `finish`, `provider`, `prompt`, `trace`, `reply`, `usage` —
`level` is a categorical judgment of the free-text answer under an earlier
scoring approach that predates the multi-select letter extraction; `final`
is the final extracted answer text.

### GPQA files (`items_gpqa_physics_conceptual_raw.jsonl`)

| field | meaning |
|---|---|
| `item_id` | item's string id, e.g. `gpqa_phys_c00` |
| `item_idx` | 0-based index into the items JSON |
| `sample` | 0-based sample index within (item, condition) |
| `condition` | `baseline`, `cue_wrong`, or `cue_correct` (only `baseline` occurs in this file — see note above) |
| `cue_target` | option letter the phase-2 cue pointed toward (null for baseline rows) |
| `eval_frame` | bool — whether the eval-framing sentence was included |
| `temperature`, `model` | sampling parameters |
| `provider` | backend that served the request (fallbacks allowed: DeepInfra > Nebius > Novita > Io Net) |
| `finish_reason` | API finish reason; `length` with no parsed answer is tallied as `TRUNC` in the summary |
| `answer` | parsed option letter (A–D), or `?` if unparseable |
| `correct` | item's correct-answer letter |
| `usage`, `prompt`, `trace`, `reply` | as above |

`items_gpqa_physics_conceptual_summary.csv` has one row per (item, condition)
with `n_valid`, `p_correct`, `p_cued`, `top_wrong`, `tally` (JSON-encoded
answer-letter counts), and `candidate` (whether the item qualified for
phase 2).


## resample_cuts runs (2026-08-25)
resample_cuts_2026-08-25_1323.*  smoke via OpenRouter chat-prefill (v1 harness), 3 eye-check records, seq=900;
                                 continuations restart — the failure that forced the DeepInfra-direct switch.
                                 Not used in any analysis.
resample_cuts_2026-08-25_1440_prefixes.json  aborted v2 smoke: T=0 mechanism check failed (strict spelling
                                 assertion, later loosened); no records generated.
resample_cuts_2026-08-25_1457.*  passing v2 smoke on DeepInfra direct, 3 eye-check records, seq=900.
                                 Not used in any analysis.
resample_cuts_2026-08-25_1503.*  THE analysis run: 20 prefixes x 25 = 500 records; gate, log, summary.


sweep_items_batball_2026-08-19_1623_rescored.jsonl — the 1623 sweep re-scored by the v2.1 extractor (letters field only; traces byte-identical). Canonical for all sweep numbers.
resample_cuts_2026-08-25_1503_rescored.jsonl — the 500 resampling records re-scored by v2.1. Canonical for all per-cut numbers.
Scoring revision provenance: docs/rescore_change_list_v21.csv (35 changed records) and docs/rescore_validation_sheet_v21.pdf.