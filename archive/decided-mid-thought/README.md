# decided-mid-thought

**Write-up (MATS 12.0 submission): https://docs.google.com/document/d/16NsVaiIhVVeNqh0aBQ1OnvAvrGNd1HIZO-gY11OAR_s/edit?usp=sharing**

**Where does a reasoning model commit to its answer?**
Prefill-and-resample experiments on chain-of-thought traces from
underspecified famous problems. Model under study: Qwen 3.6 27B (thinking)
— sweep via OpenRouter (DeepInfra pinned, fallbacks disabled); resampling via
DeepInfra's raw completions endpoint directly, because OpenRouter discards
thinking-channel prefills.

Given a mangled version of a famous puzzle — a bat-and-ball problem with one
premise deleted — the model recalls the famous version in its chain of thought
on essentially every sample, yet its final answer is governed almost entirely
by how the multiple-choice options are phrased. This repo tests, with
resampling on the thinking trace, whether the answer is committed at an
identifiable point mid-trace or is fixed from the first token (the
pre-registered null).

Pre-registration, scripts, and all raw runs are here. Findings are final —
see the write-up. The pre-registration was frozen before the resampling runs;
verdicts and the analysis freeze are in `docs/log_2026-08-30.md`.

## Repository layout

- `docs/` — dated pre-registration and planning documents (content-frozen; the
  dates are part of the record).
- `scripts/` — experiment code. Everything needed to reproduce a committed run
  is committed alongside it.
- `items/` — the question/option inputs consumed by the scripts.
- `runs/` — recorded results (one JSONL row per sample, plus summaries). See
  [`runs/README.md`](runs/README.md) for the schema and the run-to-script map.

## Setup

- Python 3.12
- `pip install -r requirements.txt`
- Copy `.env.example` to `.env` and fill in `OpenRouter_API_KEY`,
  `DEEPINFRA_API_KEY` (needed for the resampling runs), and `NEBIUS_API_KEY`.

## Reproduction

Main 2x2 sweep (eval-frame x selection-format, the 194-sample result in
`runs/`):

```
python scripts/sweep_2x2.py items/items_batball.csv -n 50
```

Resampling (the 500-record causal result in `runs/`; DeepInfra direct):

```
python scripts/resample_cuts.py
```

(Cut set and per-run parameters are recorded in
`runs/resample_cuts_2026-08-25_1503_log.txt` and the `_prefixes.json`
sidecar; the recorded files, not the current script constants, are the
authoritative record.)

Single-item baselines:

```
python scripts/baseline_levels.py -n 20 --workers 5
```

GPQA ceiling screen (negative result: 23 conceptual-physics items, 248/248
valid answers correct — the reason the project moved to underspecified famous
problems):

```
python scripts/screen_items.py items/items_gpqa_physics_conceptual.json -n 12 --phase 1
```

### What the results depend on

- **Model:** `qwen/qwen3.6-27b`, thinking enabled.
- **Provider:** DeepInfra pinned, fallbacks disabled, for `sweep_2x2.py` and
  `baseline_levels.py`; `resample_cuts.py` calls DeepInfra's raw completions
  endpoint directly (OpenRouter cannot prefill the thinking channel). `screen_items.py` allows fallback to Nebius/Novita/Io
  Net and is not used for the headline result.
- **Sampling:** `temperature=1.0`. Results are inherently non-deterministic —
  exact counts will not reproduce, only the qualitative pattern.
- **Cost:** roughly $0.04-0.05 per sample; a full sweep makes real paid API
  calls. Reproducing the findings needs budget and tolerance for sampling
  variance, not just the code.
- **Drift:** a backend's behavior can change over time even under a pinned
  name, and the `openai` client version is pinned in `requirements.txt` for the
  same reason.

## Data

See [`runs/README.md`](runs/README.md) for the JSONL/CSV data dictionary and
which script and item file produced each run. The `prompt` field inside each
JSONL record is the authoritative record of what was asked — some scripts were
edited between runs, so the recorded prompt, not the current script constant,
is the source of truth for a given file.

## Status

Pre-registration frozen 2026-08-22 (`docs/`). Resampling experiments next.
Single model, single item family; treated as a limitation, not a general
claim.