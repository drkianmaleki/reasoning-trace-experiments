# TEST_REPORT — t7_resample — 2026-09-17 15:32

Test of pipeline step (7/9), the sampling script (`scripts/s2_resample.py`, `scripts/scorer.py`), per pipeline v2 Section 9 item 9. Git commit `b5f4a5a9b0526a7bfe2f5b7da65ace8db0066d11`. Part (i) offline on the archived run; part (ii) API smoke in `runs/tests/t7_resample_2026-09-17_1532/smoke` (model Qwen/Qwen3.6-27B, stop ['<|im_end|>']). API cost $0.1687.

## Result: PASS (8/8 checks passed)

## Checks

- PASS — check 1, the scorer reproduces the archived per-prefix table — 20 prefixes recomputed from cont_text; mismatches 0 []
- PASS — check 2, the stopping rule replayed on the archived table stops both arms at old cut-62 — c004: cut15 0.36, cut29 0.16, cut44 0.64, cut58 0.48, cut59 0.56, cut60 0.84, cut61 0.84, cut62 1.00, cut63 0.92, cut64 0.84, cut67 0.96, cut68 1.00, cut69 0.92 -> stop at cut 62; e036: cut60 0.96, cut61 0.96, cut62 1.00, cut63 1.00, cut64 1.00, cut65 0.92 -> stop at cut 62
- PASS — check 3, Tk by prompt_tokens on the archived prefixes: positive differences summing to the recorded prefix length in tokens — prompt_tokens constant within every prefix: True; c004: differences [246, 183, 278, 200, 15, 33, 25, 8, 22, 20, 29, 33, 11] (all positive True), sum 1103 = prompt_tokens(cut 69) - prompt_tokens(cut-0) = 1103; last prefix 3490 characters (3.16 characters per token); e036: differences [871, 20, 24, 13, 31, 17] (all positive True), sum 976 = prompt_tokens(cut 65) - prompt_tokens(cut-0) = 976; last prefix 3279 characters (3.36 characters per token)
- PASS — check 4, slug check — status 200, model echoed 'Qwen/Qwen3.6-27B'
- PASS — check 5, no-think baseline, 10 samples: none reopens <think>, every reply resolves to a letter or ? — 10 records; reopened 0; answers {"A": 1, "B": 0, "C": 1, "D": 0, "E": 1, "F": 0, "?": 7}; mean completion tokens 1664; finish ['length', 'stop']
- PASS — check 6, three continuations from cut(C-B00) in the record format — 3 records; rb_c004_B00_001: letters ['E'], answer E, closed True, finish stop, tokens 279+8940, $0.0287; rb_c004_B00_000: letters ['C'], answer C, closed True, finish stop, tokens 279+10925, $0.0350; rb_c004_B00_002: letters ['B'], answer B, closed False, finish length, tokens 279+16000, $0.0513
- PASS — check 7, _log.txt and pcut.csv written — log lines 3; pcut rows 2; DEPARTURES.md lines 1; cost $0.1687
- PASS — check 8, pytest on scripts/tests — exit code 0; last line: 194 passed in 6.01s

## Smoke: no-think replies (first 120 characters)

- rb_nothink_003: A — 'This is a classic cognitive psychology problem, often referred to as the "Bat and Ball problem," designed to test System'
- rb_nothink_001: ? — 'This is a classic cognitive psychology problem known as the "Bat and Ball problem," often used to demonstrate the System'
- rb_nothink_002: ? — 'This is a classic cognitive psychology problem, often associated with the Cognitive Reflection Test (CRT) developed by S'
- rb_nothink_000: ? — 'This is a classic cognitive psychology puzzle, often used to test intuition vs. logical reasoning (specifically associat'
- rb_nothink_004: ? — "This is a classic cognitive puzzle often used to test intuitive vs. analytical thinking. Let's break it down mathematica"
- rb_nothink_005: C — 'This is a classic cognitive psychology problem often used to test intuitive vs. reflective thinking (the Cognitive Refle'
- rb_nothink_008: E — "To determine the correct answer, let's analyze the problem mathematically.\n\n**1. Set up the equations:**\nLet $B$ be the "
- rb_nothink_007: ? — 'To determine the cost of the ball, we can set up a system of linear equations based on the information provided.\n\nLet $b'
- rb_nothink_006: ? — 'This is a classic problem from cognitive psychology, often used to illustrate the difference between System 1 (fast, int'
- rb_nothink_009: ? — "To determine the correct option, let's solve the problem mathematically and then analyze the nature of the question and "
## Smoke: cut(C-B00) continuations (first 200 characters)

- rb_c004_B00_001: E — '\n\n2.  **Analyze the Problem Statement:**\n    *   Constraint 1: Bat ($B$) + Ball ($b$) = 1.10.\n    *   Constraint 2: Bat ($B$) > Ball ($b$).\n    *   Implicit constraint (usually): Prices are non-negati'
- rb_c004_B00_000: C — "\n\n2.  **Analyze the Math Problem:**\n    *   Let $b$ be the cost of the bat.\n    *   Let $s$ be the cost of the ball (using 's' for 'sphere' or just to distinguish from 'b').\n    *   Equation 1: $b + s"
- rb_c004_B00_002: B — '\n\n2.  **Analyze the Problem Statement:**\n    *   Let $B$ be the cost of the bat.\n    *   Let $b$ be the cost of the ball.\n    *   Given equation 1: $B + b = 1.10$.\n    *   Given inequality: $B > b$.\n '
## DEPARTURES.md of the smoke

```
- 2026-09-17T15:37:30 rb_c004_B00: prompt_tokens of the previous cut (rb_cut0) unknown in this folder; Tk(B_m) left empty
```

## pytest output

```
........................................................................ [ 37%]
........................................................................ [ 74%]
..................................................                       [100%]
194 passed in 6.01s
```
