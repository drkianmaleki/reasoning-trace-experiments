# judge_source_v3low_2026-09-24_1239 — summary

Collection `source` (whole traces), mode ordinary, model `claude-sonnet-5`, prompt v3 (sha256 `e999f7081d5a285c4db1dcb4fb55f9eb5291b1ba536f770d1ad53a815e43f51a`), thinking low. 2 documents, 2 labeled, 0 failed. Cost $0.2515 at ordinary prices.

## Usage

| input | cache read | cache write | output (thinking included) | thinking | labeled sentences | thinking tokens per labeled sentence | cost |
|---|---|---|---|---|---|---|---|
| 15038 | 8584 | 8584 | 19828 | 0 | 629 of 629 | nan | $0.2515 |

### P_corpus at Level 1 (source, judge labels under R4)

2 traces, 329 nodes, 327 consecutive node pairs; a combined node counts under its first path. Blocks per trace min / median / max: 35 / 39.0 / 43; nodes per trace 137 / 164.5 / 192.

Counts (row X = current node, column Y = next node):

| X \ Y | Pl | Re | Rf | Kn | Rs | As | Ex | Co | row total | nodes X |
|---|---|---|---|---|---|---|---|---|---|---|
| Planning | 2 | 41 | 7 | 9 | 30 | 1 | 2 | 10 | 102 | 103 |
| Reasoning | 44 | 0 | 3 | 8 | 8 | 0 | 4 | 18 | 85 | 85 |
| Reflection | 11 | 3 | 0 | 0 | 3 | 0 | 0 | 4 | 21 | 21 |
| Knowledge | 7 | 11 | 0 | 0 | 0 | 0 | 0 | 3 | 21 | 21 |
| Restatement | 8 | 19 | 8 | 1 | 0 | 0 | 0 | 7 | 43 | 43 |
| Assumption | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 3 |
| Example | 2 | 3 | 0 | 0 | 0 | 0 | 0 | 2 | 7 | 7 |
| Conclusion | 27 | 5 | 3 | 3 | 2 | 2 | 1 | 2 | 45 | 46 |

Row-normalized, P_corpus(Y | X):

| X \ Y | Pl | Re | Rf | Kn | Rs | As | Ex | Co |
|---|---|---|---|---|---|---|---|---|
| Planning | 0.020 | 0.402 | 0.069 | 0.088 | 0.294 | 0.010 | 0.020 | 0.098 |
| Reasoning | 0.518 | 0.000 | 0.035 | 0.094 | 0.094 | 0.000 | 0.047 | 0.212 |
| Reflection | 0.524 | 0.143 | 0.000 | 0.000 | 0.143 | 0.000 | 0.000 | 0.190 |
| Knowledge | 0.333 | 0.524 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.143 |
| Restatement | 0.186 | 0.442 | 0.186 | 0.023 | 0.000 | 0.000 | 0.000 | 0.163 |
| Assumption | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Example | 0.286 | 0.429 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.286 |
| Conclusion | 0.600 | 0.111 | 0.067 | 0.067 | 0.044 | 0.044 | 0.022 | 0.044 |

Marginal node counts: Planning 103, Reasoning 85, Reflection 21, Knowledge 21, Restatement 43, Assumption 3, Example 7, Conclusion 46.

