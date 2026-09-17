# TEST_REPORT — t2_split — 2026-09-16 22:24

Gate test of pipeline step (2/9), the splitter (`scripts/s0_split.py`), per pipeline v1 Section 9 item 4. Git commit at run time: `26ee14aa1acf5e3099bec71c83eab71858595ee7` (working tree dirty: True; the script under test is identified by its sha256 `6c8a735427240172ce9ca8bb4a3d08562125e006bc48aa9b7b181b0cb832313c` in config.json). Python 3.12.10. Offline; API cost $0.

Inputs: `archive/decided-mid-thought/runs/sweep_items_batball_2026-08-19_1623.jsonl` sha256 `372b22e5d5a0871a3c1e52180250daf9e62ed4ac0e9ce6312b027c523bdb530e`; listing `docs/shared/2026-09-15_source_traces_labeled_v2.md`.

## Result: PASS (8/8 checks passed)

## Checks

- PASS — check 1, sentence counts — c004: equation rule 375 (expected 375), base rule 366 (expected 366); e036: equation rule 254 (expected 254), base rule 247 (expected 247)
- PASS — check 2, boundary-by-boundary match with the listing — c004: 375 listing rows, 375 sentences; exact 362, prefix 13, mismatches 0; e036: 254 listing rows, 254 sentences; exact 248, prefix 6, mismatches 0; mismatches listed in mismatches.txt (0 entries)
- PASS — check 3, old_s and part against the listing's Item column — 629 rows; c004: 375/375 rows agree, 9 equation-rule parts (part > 1); e036: 254/254 rows agree, 7 equation-rule parts (part > 1)
- PASS — check 4, every base-rule boundary is an equation-rule boundary — c004: 366 base boundaries, 366 kept, 0 lost, 9 added by the equation rule; e036: 247 base boundaries, 247 kept, 0 lost, 7 added by the equation rule
- PASS — check 4b, base rule against the archived splitter (independent oracle) — c004: archived splitter 366 sentences, base rule 366; boundaries added 0, dropped 0; e036: archived splitter 253 sentences, base rule 247; boundaries added 0, dropped 6 (all single newlines preceded by a space; they form old s150, s193, s200, s212, s227, s240)
- PASS — check 5, sentences_source.jsonl partition properties and text field — 629 records (c004: 375, e036: 254); first start 0, last end = len(text), contiguous, no empty span, text == sentence_text: all hold
- PASS — check 6, splitter on the first five archived continuations — rs0823_cut000_003: 8724 chars, 204 sentences; rs0823_cut000_000: 8694 chars, 192 sentences; rs0823_cut000_001: 11371 chars, 242 sentences; rs0823_cut000_005: 8171 chars, 181 sentences; rs0823_cut000_006: 8782 chars, 178 sentences (files sentences_archived5_sample.jsonl and .md)
- PASS — pytest, scripts/tests/test_s0_split.py — exit code 0; last line: 38 passed in 0.17s

## Clarifications applied beyond the quoted rule (labeling scheme v4, Section 0c)

See the module docstring of `scripts/s0_split.py`, items 1–6. In short: (1) a rule-(a) comma, like a period, must be followed by whitespace or the end of the text; (2) segment state and parenthesis depth reset at every sentence start; (3) a capitalized clause = the character right after `(` is an uppercase letter; (4) rule (b) only at parenthesis depth 0; (5) the display form drops the text's trailing whitespace from the last sentence; (6) a line break is a boundary when the newline directly follows a non-whitespace character or belongs to a blank line; a single newline preceded by a space is not — forced by E s157 (`ball." ⏎   Mathematically, ...`), where the confirmed listing keeps one sentence; the archived script's splitter (split on every newline) gives 253 base sentences for e036, the listing 247 (six merges forming old s150, s193, s200, s212, s227, s240; the numberings agree up to archived s150, so the archived E cuts 60–65 are unaffected; see check 4b).

## Files produced

- `runs/tests/t2_split_2026-09-16_2224/TEST_REPORT.md` (this file)
- `sentences_source.jsonl` — 629 records with old_s and part; `config.json`, `_log.txt` (written by s0_split.run_collection)
- `mismatches.txt` — 0 entries
- `sentences_archived5_sample.jsonl`, `sentences_archived5_sample.md` — 997 sentences of five archived continuations
- `pytest_output.txt`

## pytest output

```
......................................                                   [100%]
38 passed in 0.17s
```

### Base-rule boundaries dropped relative to the archived splitter (check 4b)

```
e036 raw offset 7507 (old s150): ' states that "the bat costs *more* than the ball."' || ' \n   Mathematically, we have t'
e036 raw offset 9142 (old s193): 'Output Generation. \n   [Output] -> *See response.*' || ' \n   *(Self-Correction/Note du'
e036 raw offset 9398 (old s200): '✅\n   Output matches the refined draft. \n   [Done.]' || ' \n   *Self-Correction/Refineme'
e036 raw offset 9806 (old s212): 'e reflection test version..." etc. \n   "Answer: E"' || ' \n   Done. \n   [Output] -> *Pr'
e036 raw offset 10568 (old s227): 'only says: "The bat costs **more** than the ball."' || ' \n   This gives us:\n   1. Bat '
e036 raw offset 11136 (old s240): 'the most accurate choice.\n\n   Answer: E\n   [Done.]' || ' \n   *Self-Correction/Verifica'
```
