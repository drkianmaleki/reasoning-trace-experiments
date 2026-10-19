# reasoning-trace-experiments

Where in a reasoning model's chain of thought does the answer it will give take shape, and does
the model's next move depend on more than its last one? This repository is the complete record of
one study of those questions: the instrument, the pre-registration, every sampled continuation,
every label the judge produced, the analysis code, the results document, and the manuscript
*A Probabilistic Instrument for Studying Reasoning Traces and Testing the Ordering and Markovian
Assumption Behind Them* (Kian Maleki, 2026), whose numbers and figures all come from the files here.

Author: Kian Maleki. Model under study: Qwen 3.6-27B in thinking mode. License: MIT (`LICENSE`).
Everything below is reproducible offline from the committed files; the API calls that produced
the raw data are described in the run records and need keys only if you want to sample afresh.

## The study in brief

The item is the bat-and-ball riddle with its key clause deleted ("A bat and a ball cost $1.10 in
total. The bat costs more than the ball. How much does the ball cost?") and six options, among
them (C) "there is not enough information, but the answer is most likely $0.05" and (E) "the
question is not well posed".
Two of the model's own thinking traces are studied: the C-trace (c004, 375 sentences, ends at C)
and the E-trace (e036, 254 sentences, ends at E). Every sentence carries a hierarchical label
(eight Level 1 types after ReasoningFlow, Lee et al. 2026, with Level 2 and item-specific Level 3
leaves); consecutive same-label sentences form a node, and fixed opener rules group the nodes into
blocks, 47 in the C-trace and 38 in the E-trace.

The instrument is resampling at block boundaries. The trace up to the end of block m is fed back
to the model as its own unfinished thinking and completed 25 times. At every cut two things are
measured: how often the continuations finish with the trace's own answer, and what kind of move
they make first. The sampled run holds 625 continuations (a 100-sample no-think baseline, 25 from
the empty prefix, 12 C-trace cuts and 8 E-trace cuts at 25 each); each continuation was then split
into sentences and labeled by an LLM judge (Claude Sonnet 5, prompt v3, low thinking effort).

What stage one found, in the words of the results document
(`docs/shared/2026-09-24_stage1_results_v3.md`):

- Reasoning changes the answer. Without thinking the model answers C 49 times in 100; thinking
  from an empty prefix it answers E 18 times in 25.
- In the C-trace the completed-C frequency rises from 0.12 to 1.00, and the largest shift, +0.60,
  occurs across the one block in which the model scores the options and reads their hedge words
  (block 9). Two further shifts of +0.36 sit at blocks 0 and 6; the one at block 6 does not survive
  the most adverse assumption about continuations that never finished.
- The kind of the last move does not determine the next one. The registered permutation test
  rejects the reading in which the next label depends only on the last Level 1 label (C-trace
  p ≤ 0.0001, E-trace p = 0.0033), and three cuts ending on the identical full label path still
  give different next-move distributions.
- Exploratory: in 69 traces written with no prefix, those that do the algebra before naming the
  classic riddle end at C in 4 of 13 against 2 of 52 (+0.27 [0.07, 0.54], Fisher p = 0.012). The
  model chose both the order and the answer, so this is an association.

Section 11 of the results document lists how each reading could be wrong, and Section 3.1
explains the scoring rule and its departure from the pre-registration.

## Layout

- `manuscript/` — the manuscript as a PDF, in two forms: the paper, drafted with an AI assistant
  and polished (file name ending `AI_polished`), and a note on the same work written by the author
  alone (file name ending `No_AI-assisted`). The note is the author's own account of the problem,
  the instrument and the findings, in his own words.
- `docs/shared/` — the confirmed documents, each dated and versioned, with its changelog inside:
  the action summary (design, motivation, item prompt, decisions), the labeling scheme (labels,
  node and block rules, notation), the sentence-indexed source traces, the reviewed labels of both
  traces in review layout, the pipeline specification, the stage-one pre-registration, the scorer
  audit, the re-derivation procedure, and the stage-one results.
- `docs/kian/` — the author's own logs and block definitions.
- `docs/claude/` — the dated state files of the AI assistant that drafted and coded under the
  author's direction; the latest is authoritative, and together they record what was decided when.
- `scripts/` — the pipeline (`s0_split.py` to `s6_order.py`), the figure scripts, the archived
  scorer, the statistics, and `tests/` (unit tests and the dated gate scripts t0 to t9).
- `prompts/` — the three judge prompts, their label inventories and provenance files.
- `runs/experiments/` — every run, each in a dated folder with its `config.json` and log:
  the registered stage-one run, its strict-scoring reading, the judge runs on the source traces,
  the judge comparisons, the corpus labeling of 44 traces (sweep44), the order analysis, and the
  re-derivation. `runs/tests/` holds the gate runs; `runs/LARGE_FILES_INDEX.md` lists the four
  data files kept out of git (sizes, hashes, provenance).
- `figures/` — the manuscript's figures with their data, and the analysis plots of every run.
- `archive/` — superseded files, never deleted: earlier document versions, earlier state files,
  the previous README, and `archive/decided-mid-thought/`, a frozen copy of the earlier
  sentence-level study (see below).

The paper's LaTeX working folder, `rte-paper/`, is ignored by git and is not in the repository.

## Where the raw data are

- The 625 continuations, with the exact prompt string sent for each, the model's full thinking
  and reply, token usage and timing: `runs/experiments/resample_blocks_2026-09-17_1759/continuations.jsonl`
  (the registered run, scored with the registered scorer). The same records read with the strict
  rule, the registered values kept alongside: `runs/experiments/resample_blocks_2026-09-17_1759_strict/continuations.jsonl`.
- The judge's labels of every continuation, its raw requests and replies, and the batch logs:
  `runs/experiments/resample_blocks_2026-09-17_1759/judge_2026-09-17_2229/` (six waves plus the two
  relabeled cuts under `noise_*`).
- The author-reviewed labels of the two source traces, machine-readable:
  `runs/experiments/judge_archived500_2026-09-17_1334/labels_source_reviewed_v4.jsonl`; in review
  layout: `docs/shared/2026-09-17_source_traces_labeled_v4.md`.
- The judge's labels of the 44 prefix-free traces and the corpus transition matrix:
  `runs/experiments/judge_sweep44_2026-09-17_1334/`.
- The two source traces and the 44 traces they were chosen from:
  `archive/decided-mid-thought/runs/sweep_items_batball_2026-08-19_1623.jsonl` (condition
  `eval0_multi0`, samples 2 and 40).
- Not in git, listed in `runs/LARGE_FILES_INDEX.md` with hashes: the judge's labels of the
  archived 500 sentence-level continuations (two files, 116 MB) and two regenerable sentence
  files. Available from the author on request.

## Reproducing the tables and figures

Python 3 with the pinned packages (`pip install -r requirements.txt`; the commands below were
checked on a fresh clone with Python 3.13). No API key is needed for anything in this section.
The scripts write their outputs with CRLF line endings and the committed copies are LF, so
compare with `diff --strip-trailing-cr`; the outputs also carry a timestamp line.

The unit tests:

```
python -m pytest scripts/tests
```

The registered analysis of the stage-one run (mediation and transition tables, the permutation
test, the plots), written to a folder of your choice so the committed run folder stays untouched:

```
python scripts/s4_analyze.py --run runs/experiments/resample_blocks_2026-09-17_1759 --out /tmp/registered
```

The strict reading, which the manuscript and the results document use: rescore the registered
run and rerun the same analysis on it. This reproduces every table of
`runs/experiments/resample_blocks_2026-09-17_1759_strict/`, among them the answer tables of
Sections 4 and 5 and the permutation test of Section 6 of the results document:

```
python scripts/s5_rescore.py --run runs/experiments/resample_blocks_2026-09-17_1759 --out /tmp/strict
```

The order analysis on the 69 prefix-free texts (Section 8 of the results document), from the
judge's labels:

```
python scripts/s6_order.py --run runs/experiments/resample_blocks_2026-09-17_1759 --prefix-free runs/experiments/judge_sweep44_2026-09-17_1334 --out /tmp/order
```

The judge comparison (agreement of every judge configuration with the reviewed labels, the
reasoning curve, the structural metrics; Section 3.3 of the results document and the
manuscript's Appendix B):

```
python scripts/compare_judge_runs.py --out /tmp/cmp
```

The figures. Figure 1's content (one block of the C-trace with its labels) is set inside the
script; Figures 2 and 3 read `figures/fig23_data.csv`, the per-cut answer counts of the strict
reading written from the committed tables. Both scripts write SVG; the PNG and PDF need cairosvg,
Inkscape or ImageMagick on the path.

```
python scripts/fig1_instrument.py
python scripts/fig23_cluster.py --pair --side-by-side
```

Sampling and labeling afresh needs the keys of `.env.example` in a local `.env`
(`scripts/s2_resample.py` for the continuations on DeepInfra, `scripts/s3_judge_continuations.py`
for the judge on the Claude API). Both scripts have a `--dry-run` that builds every prompt and
estimates the cost without a call. A new judge run is a new labeling, not a reproduction of the
committed one.

## Pre-registration and departures

The design was registered before any sampling in
`docs/shared/2026-09-17_preregistration_stage1_v2.md`, whose commit is the registration
timestamp; the hypotheses, the 84 prefixes, n = 25, the stopping rule, the judge
configuration and the analyses are all stated there. Every departure is logged in the run folder's
`DEPARTURES.md`:

- Two continuations of 525 remained unlabeled after three judge attempts and are excluded from
  the transition tables only.
- The registered scorer misread 36 of the 625 continuations (an answer written "Answer: (C)"
  missed; letters read out of unfinished thinking text). The strict reading, under which a
  continuation has an answer only if it finished, was adopted after the run and is canonical;
  the registered numbers are reported alongside it everywhere. The audit is
  `docs/shared/2026-09-19_scorer_audit_v1.md`.

The headline numbers were derived three times by separate code from the same records: the
pipeline, an independent script written by a second AI system from the written procedure
(`docs/shared/2026-09-19_rederivation_steps_v1.md`), and the author's own
`scripts/result_verification.py`. All three agree; the record is
`runs/experiments/rederivation_2026-09-19/`.

## The earlier study

`archive/decided-mid-thought/` is a frozen copy of the project's first stage, a sentence-level
truncation-and-resampling study of the same two traces (500 continuations over 20 prefixes),
submitted to the MATS 12.0 application round. Its own repository is
[github.com/drkianmaleki/decided-mid-thought](https://github.com/drkianmaleki/decided-mid-thought),
and its runs are the source of the traces studied here. The block-level design of this repository
was built to answer the question that study left open: which stretches of the trace carry the
movement of the answer.

## AI use

An AI assistant (Claude) drafted the documents in `docs/shared/` and `docs/claude/`, wrote the
code in `scripts/` and the provisional sentence labels, all under the author's direction; the
author confirmed every document, reviewed the labels, owns the design and every decision recorded
in the changelogs, and re-derived the headline numbers. The sentence labels of the continuations
were produced by Claude Sonnet 5 as the judge, and the judge is treated throughout as a named
source of uncertainty, with its agreement against the reviewed labels reported next to every
judge-dependent number. A second AI system (ChatGPT) produced one of the three re-derivations.
Of the two documents in `manuscript/`, the paper was drafted section by section with the assistant
under the author's direction and approved by him section by section; the note was written by the
author in his own words, and the assistant only checked its numbers against the record and changed
no text.

## Citing

See `CITATION.cff`. Please cite the manuscript in `manuscript/`; cite the repository for the data
and code.
