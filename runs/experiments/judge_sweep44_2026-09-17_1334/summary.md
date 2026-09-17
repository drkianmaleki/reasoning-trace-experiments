# judge_sweep44_2026-09-17_1334 — summary

Collection `sweep44` (whole traces), mode batch, model `claude-sonnet-5`, prompt v3 (sha256 `e999f7081d5a285c4db1dcb4fb55f9eb5291b1ba536f770d1ad53a815e43f51a`), thinking low. 44 documents, 44 labeled, 0 failed. Cost $3.7481 at batch prices.

## Usage

| input | cache read | cache write | output (thinking included) | thinking | labeled sentences | thinking tokens per labeled sentence | cost |
|---|---|---|---|---|---|---|---|
| 439515 | 240352 | 180264 | 611843 | 485133 | 15295 of 15295 | 31.7 | $3.7481 |

## Batches

| batch id | attempt | entries | submitted | ended | request_counts |
|---|---|---|---|---|---|
| msgbatch_01MUUy5eBMgaVowLNk941dbW | 1 | 44 | 2026-09-17T13:34:09 | 2026-09-17T13:44:12 | {"processing": 0, "succeeded": 44, "errored": 0, "canceled": 0, "expired": 0} |
| msgbatch_01LKNbWDQa6fKyeV4S6wVRC8 | 2 | 5 | 2026-09-17T13:44:16 | 2026-09-17T13:49:18 | {"processing": 0, "succeeded": 5, "errored": 0, "canceled": 0, "expired": 0} |

### P_corpus at Level 1 (sweep44, judge labels under R4)

44 traces, 8561 nodes, 8517 consecutive node pairs; a combined node counts under its first path. Blocks per trace min / median / max: 20 / 29.0 / 178; nodes per trace 74 / 109.5 / 608.

Counts (row X = current node, column Y = next node):

| X \ Y | Pl | Re | Rf | Kn | Rs | As | Ex | Co | row total | nodes X |
|---|---|---|---|---|---|---|---|---|---|---|
| Planning | 76 | 1066 | 135 | 305 | 839 | 47 | 59 | 154 | 2681 | 2711 |
| Reasoning | 1006 | 1 | 149 | 211 | 176 | 78 | 45 | 554 | 2220 | 2220 |
| Reflection | 312 | 91 | 0 | 13 | 44 | 3 | 2 | 56 | 521 | 523 |
| Knowledge | 165 | 307 | 19 | 1 | 34 | 10 | 3 | 68 | 607 | 607 |
| Restatement | 402 | 423 | 130 | 35 | 8 | 16 | 10 | 148 | 1172 | 1172 |
| Assumption | 24 | 115 | 0 | 10 | 5 | 0 | 3 | 7 | 164 | 164 |
| Example | 31 | 47 | 1 | 0 | 3 | 0 | 0 | 40 | 122 | 122 |
| Conclusion | 651 | 170 | 89 | 32 | 63 | 10 | 0 | 15 | 1030 | 1042 |

Row-normalized, P_corpus(Y | X):

| X \ Y | Pl | Re | Rf | Kn | Rs | As | Ex | Co |
|---|---|---|---|---|---|---|---|---|
| Planning | 0.028 | 0.398 | 0.050 | 0.114 | 0.313 | 0.018 | 0.022 | 0.057 |
| Reasoning | 0.453 | 0.000 | 0.067 | 0.095 | 0.079 | 0.035 | 0.020 | 0.250 |
| Reflection | 0.599 | 0.175 | 0.000 | 0.025 | 0.084 | 0.006 | 0.004 | 0.107 |
| Knowledge | 0.272 | 0.506 | 0.031 | 0.002 | 0.056 | 0.016 | 0.005 | 0.112 |
| Restatement | 0.343 | 0.361 | 0.111 | 0.030 | 0.007 | 0.014 | 0.009 | 0.126 |
| Assumption | 0.146 | 0.701 | 0.000 | 0.061 | 0.030 | 0.000 | 0.018 | 0.043 |
| Example | 0.254 | 0.385 | 0.008 | 0.000 | 0.025 | 0.000 | 0.000 | 0.328 |
| Conclusion | 0.632 | 0.165 | 0.086 | 0.031 | 0.061 | 0.010 | 0.000 | 0.015 |

Marginal node counts: Planning 2711, Reasoning 2220, Reflection 523, Knowledge 607, Restatement 1172, Assumption 164, Example 122, Conclusion 1042.

