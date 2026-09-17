# judge_archived500_2026-09-17_1334 — summary

Collection `archived500` (continuations), mode batch, model `claude-sonnet-5`, prompt v3 (sha256 `e999f7081d5a285c4db1dcb4fb55f9eb5291b1ba536f770d1ad53a815e43f51a`), thinking low. 500 documents, 496 labeled, 4 failed. Cost $61.0671 at batch prices.

Retry of the failed traces on 2026-09-17T14:28:29 (attempt 3, one batch, the format-check line appended): 7 parsed, 4 still failed, cost $2.1397; tables below recomputed from the files.

## Usage

| input | cache read | cache write | output (thinking included) | thinking | labeled sentences | thinking tokens per labeled sentence | cost |
|---|---|---|---|---|---|---|---|
| 9786693 | 5425088 | 0 | 10147589 | 7801849 | 221929 of 225173 | 35.2 | $61.0671 |

## Batches

| batch id | attempt | entries | submitted | ended | request_counts |
|---|---|---|---|---|---|
| msgbatch_01YVinBkyvvuJaCJGTWjmF5d | 1 | 500 | 2026-09-17T13:35:08 | 2026-09-17T13:47:12 | {"processing": 0, "succeeded": 500, "errored": 0, "canceled": 0, "expired": 0} |
| msgbatch_01U9VnKZUdFdrNDWNFM415vQ | 2 | 121 | 2026-09-17T13:48:17 | 2026-09-17T14:00:22 | {"processing": 0, "succeeded": 121, "errored": 0, "canceled": 0, "expired": 0} |
| msgbatch_019Ly4igKHxc8JQeyKxZVXyt | 3 | 11 | 2026-09-17T14:22:24 | 2026-09-17T14:28:26 | {"processing": 0, "succeeded": 11, "errored": 0, "canceled": 0, "expired": 0} |

## Failures

| trace | attempts | error |
|---|---|---|
| rs0823_c004_cut060_022 | 3 | overlap: sentences 876..876 are covered twice at line 713: 876 Rf.meo.E |
| rs0823_c004_cut067_001 | 3 | unparsable: a combined sentence needs a single index, not a run at line 44: 56-57 Pl.iv.wdm+Kn.wk.fpc |
| rs0823_c004_cut015_021 | 3 | overlap: sentences 462..462 are covered twice at line 358: 462 Re.oe.C |
| rs0823_c004_cut029_005 | 3 | overlap: sentences 1..1 are covered twice at line 2: 1 Re.lr.al |

### P(next | cut) after the archived cuts (archived500; first new node after the cut, judge labels under R4)

| prefix_id | arm | cut | last node label | n | labeled | failed | Pl | Re | Rf | Kn | Rs | As | Ex | Co | opens block | first is Wait |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rs0823_cut000 | shared | 0 | None | 25 | 25 | 0 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | 0 |
| rs0823_c004_cut015 | c004 | 15 | Reasoning | 25 | 24 | 1 | 5 | 19 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rs0823_c004_cut029 | c004 | 29 | Reasoning | 25 | 24 | 1 | 0 | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rs0823_c004_cut044 | c004 | 44 | Reasoning | 25 | 25 | 0 | 21 | 3 | 0 | 0 | 0 | 0 | 1 | 0 | 15 | 2 |
| rs0823_c004_cut058 | c004 | 58 | Reasoning | 25 | 25 | 0 | 0 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rs0823_c004_cut059 | c004 | 59 | Reasoning | 25 | 25 | 0 | 5 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rs0823_c004_cut060 | c004 | 60 | Reasoning | 25 | 24 | 1 | 18 | 1 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 |
| rs0823_c004_cut061 | c004 | 61 | Planning | 25 | 25 | 0 | 0 | 7 | 18 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rs0823_c004_cut062 | c004 | 62 | Reflection | 25 | 25 | 0 | 3 | 15 | 2 | 0 | 3 | 0 | 0 | 2 | 0 | 0 |
| rs0823_c004_cut063 | c004 | 63 | Reasoning | 25 | 25 | 0 | 0 | 22 | 0 | 1 | 0 | 0 | 0 | 2 | 0 | 0 |
| rs0823_c004_cut064 | c004 | 64 | Reasoning | 25 | 25 | 0 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rs0823_c004_cut067 | c004 | 67 | Planning | 25 | 24 | 1 | 0 | 9 | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rs0823_c004_cut068 | c004 | 68 | Reasoning | 25 | 25 | 0 | 4 | 13 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rs0823_c004_cut069 | c004 | 69 | Reasoning | 25 | 25 | 0 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| rs0823_e036_cut060 | e036 | 60 | Conclusion | 25 | 25 | 0 | 0 | 24 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rs0823_e036_cut061 | e036 | 61 | Reasoning | 25 | 25 | 0 | 0 | 9 | 0 | 6 | 10 | 0 | 0 | 0 | 0 | 0 |
| rs0823_e036_cut062 | e036 | 62 | Restatement | 25 | 25 | 0 | 0 | 23 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rs0823_e036_cut063 | e036 | 63 | Reasoning | 25 | 25 | 0 | 0 | 17 | 7 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| rs0823_e036_cut064 | e036 | 64 | Reasoning | 25 | 25 | 0 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | 25 |
| rs0823_e036_cut065 | e036 | 65 | Planning | 25 | 25 | 0 | 0 | 23 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |

### P_source for c004 (reviewed labels under R4; 46 block-end cuts)

| m | cut after s | last node (label) | source next node (label) | opener rule |
|---|---|---|---|---|
| 0 | s7 | Rs₀(5) (Restatement) | Pl₁(2) (Planning) | R1 |
| 1 | s12 | Rs₁ (Restatement) | Pl₂(2) (Planning) | R1 |
| 2 | s14 | Pl₂(2) (Planning) | As₃ (Assumption) | R2 |
| 3 | s22 | Re₃(7) (Reasoning) | As₄ (Assumption) | R2 |
| 4 | s30 | Re₄(7) (Reasoning) | As₅ (Assumption) | R2 |
| 5 | s35 | Re₅(4) (Reasoning) | Pl₆(2) (Planning) | R1 |
| 6 | s41 | Re₆(2) (Reasoning) | [Pl+Kn]₇ (Planning) | R4 |
| 7 | s42 | [Pl+Kn]₇ (Planning) | [Pl+Rs]₈ (Planning) | R1 |
| 8 | s57 | Ex₈(10) (Example) | Pl₉¹(3) (Planning) | R1 |
| 9 | s78 | Rf₉³ (Reflection) | Pl₁₀¹(3) (Planning) | R1 |
| 10 | s97 | Re₁₀⁴ (Reasoning) | Pl₁₁(3) (Planning) | R1 |
| 11 | s106 | Re₁₁(6) (Reasoning) | Pl₁₂ (Planning) | R1 |
| 12 | s113 | Co₁₂ (Conclusion) | [Pl+Rs]₁₃ (Planning) | R1 |
| 13 | s115 | Re₁₃ (Reasoning) | Pl₁₄ (Planning) | R1 |
| 14 | s119 | Re₁₄(2) (Reasoning) | Pl₁₅ (Planning) | R1 |
| 15 | s131 | Re₁₅(8) (Reasoning) | Pl₁₆ (Planning) | R1 |
| 16 | s136 | Rf₁₆ (Reflection) | Pl₁₇ (Planning) | R4 |
| 17 | s143 | Re₁₇(6) (Reasoning) | Pl₁₈ (Planning) | R1 |
| 18 | s147 | Re₁₈(2) (Reasoning) | Pl₁₉ (Planning) | R1 |
| 19 | s159 | Co₁₉ (Conclusion) | [Pl+Re]₂₀ (Planning) | R1 |
| 20 | s165 | Co₂₀ (Conclusion) | Pl₂₁ (Planning) | R1 |
| 21 | s170 | Re₂₁ (Reasoning) | Pl₂₂ (Planning) | R1 |
| 22 | s186 | Rs₂₂(15) (Restatement) | Pl₂₃ (Planning) | R1 |
| 23 | s189 | Rf₂₃ (Reflection) | Pl₂₄ (Planning) | R1 |
| 24 | s192 | Re₂₄(2) (Reasoning) | Pl₂₅ (Planning) | R1 |
| 25 | s198 | Re₂₅(4) (Reasoning) | Pl₂₆ (Planning) | R1 |
| 26 | s201 | Co₂₆(2) (Conclusion) | Pl₂₇ (Planning) | R1 |
| 27 | s208 | Re₂₇²(4) (Reasoning) | Pl₂₈ (Planning) | R1 |
| 28 | s215 | Re₂₈(6) (Reasoning) | As₂₉ (Assumption) | R2 |
| 29 | s226 | Co₂₉ (Conclusion) | [Pl+Rs]₃₀ (Planning) | R1 |
| 30 | s228 | Co₃₀ (Conclusion) | Pl₃₁¹(3) (Planning) | R1 |
| 31 | s253 | Co₃₁ (Conclusion) | Pl₃₂ (Planning) | R4 |
| 32 | s262 | Re₃₂(6) (Reasoning) | Pl₃₃ (Planning) | R1 |
| 33 | s265 | Re₃₃(2) (Reasoning) | Pl₃₄¹ (Planning) | R1 |
| 34 | s276 | Rf₃₄ (Reflection) | Pl₃₅ (Planning) | R1 |
| 35 | s287 | Co₃₅ (Conclusion) | Pl₃₆ (Planning) | R4 |
| 36 | s301 | Co₃₆ (Conclusion) | Pl₃₇¹(3) (Planning) | R1 |
| 37 | s324 | Co₃₇ (Conclusion) | Pl₃₈ (Planning) | R1 |
| 38 | s329 | Re₃₈(4) (Reasoning) | Pl₃₉¹ (Planning) | R1 |
| 39 | s339 | Rs₃₉³(5) (Restatement) | Pl₄₀ (Planning) | R4 |
| 40 | s341 | Re₄₀ (Reasoning) | Pl₄₁ (Planning) | R1 |
| 41 | s343 | Re₄₁ (Reasoning) | Pl₄₂ (Planning) | R1 |
| 42 | s351 | Co₄₂ (Conclusion) | Pl₄₃ (Planning) | R4 |
| 43 | s355 | Kn₄₃ (Knowledge) | As₄₄ (Assumption) | R2 |
| 44 | s361 | Re₄₄ (Reasoning) | Pl₄₅¹ (Planning) | R1 |
| 45 | s373 | Co₄₅ (Conclusion) | Co₄₆ (Conclusion) | R3 |

Pairs (last → next): Reasoning → Planning 19; Conclusion → Planning 11; Restatement → Planning 4; Reflection → Planning 4; Reasoning → Assumption 3; Planning → Assumption 1; Planning → Planning 1; Example → Planning 1; Knowledge → Assumption 1; Conclusion → Conclusion 1.

### P_source for e036 (reviewed labels under R4; 37 block-end cuts)

| m | cut after s | last node (label) | source next node (label) | opener rule |
|---|---|---|---|---|
| 0 | s11 | Rs₀³(2) (Restatement) | Pl₁(2) (Planning) | R1 |
| 1 | s15 | Kn₁(2) (Knowledge) | Pl₂ (Planning) | R1 |
| 2 | s18 | [Re+As]₂ (Reasoning) | [Pl+Re]₃ (Planning) | R4 |
| 3 | s19 | [Pl+Re]₃ (Planning) | Pl₄¹ (Planning) | R1 |
| 4 | s41 | Co₄ (Conclusion) | Pl₅(2) (Planning) | R1 |
| 5 | s52 | Rf₅³ (Reflection) | Pl₆¹ (Planning) | R1 |
| 6 | s70 | Re₆⁵(2) (Reasoning) | Pl₇ (Planning) | R4 |
| 7 | s74 | Rf₇ (Reflection) | Pl₈ (Planning) | R1 |
| 8 | s76 | Kn₈ (Knowledge) | Pl₉ (Planning) | R1 |
| 9 | s92 | Re₉³(2) (Reasoning) | Pl₁₀ (Planning) | R1 |
| 10 | s95 | Rf₁₀ (Reflection) | Pl₁₁(3) (Planning) | R1 |
| 11 | s99 | Co₁₁ (Conclusion) | Pl₁₂ (Planning) | R4 |
| 12 | s104 | Co₁₂ (Conclusion) | Pl₁₃¹(4) (Planning) | R1 |
| 13 | s116 | Co₁₃ (Conclusion) | Pl₁₄ (Planning) | R1 |
| 14 | s119 | Co₁₄ (Conclusion) | Pl₁₅(8) (Planning) | R1 |
| 15 | s133 | Co₁₅ (Conclusion) | Pl₁₆(7) (Planning) | R1 |
| 16 | s143 | Rf₁₆ (Reflection) | Pl₁₇(2) (Planning) | R1 |
| 17 | s151 | Co₁₇² (Conclusion) | Pl₁₈ (Planning) | R1 |
| 18 | s153 | Co₁₈ (Conclusion) | Pl₁₉ (Planning) | R1 |
| 19 | s165 | Co₁₉(2) (Conclusion) | Pl₂₀ (Planning) | R1 |
| 20 | s167 | Rf₂₀ (Reflection) | Pl₂₁(2) (Planning) | R1 |
| 21 | s173 | Rf₂₁ (Reflection) | Pl₂₂(2) (Planning) | R1 |
| 22 | s176 | Co₂₂ (Conclusion) | Pl₂₃(2) (Planning) | R1 |
| 23 | s178 | Pl₂₃(2) (Planning) | Pl₂₄ (Planning) | R4 |
| 24 | s181 | Rf₂₄ (Reflection) | Pl₂₅ (Planning) | R1 |
| 25 | s186 | Rf₂₅² (Reflection) | Pl₂₆(2) (Planning) | R1 |
| 26 | s192 | Rf₂₆(2) (Reflection) | [Pl+Rs]₂₇ (Planning) | R1 |
| 27 | s198 | Rf₂₇ (Reflection) | Pl₂₈(3) (Planning) | R1 |
| 28 | s203 | Co₂₈ (Conclusion) | Pl₂₉ (Planning) | R1 |
| 29 | s206 | Rf₂₉(2) (Reflection) | Pl₃₀(2) (Planning) | R1 |
| 30 | s212 | Co₃₀ (Conclusion) | Pl₃₁ (Planning) | R1 |
| 31 | s214 | Co₃₁ (Conclusion) | Pl₃₂(2) (Planning) | R1 |
| 32 | s219 | Rs₃₂(3) (Restatement) | Pl₃₃(3) (Planning) | R1 |
| 33 | s227 | Rf₃₃ (Reflection) | Pl₃₄(2) (Planning) | R1 |
| 34 | s244 | Co₃₄ (Conclusion) | Co₃₅(2) (Conclusion) | R3 |
| 35 | s246 | Co₃₅(2) (Conclusion) | Pl₃₆ (Planning) | R1 |
| 36 | s250 | Rf₃₆(3) (Reflection) | Pl₃₇(3) (Planning) | R1 |

Pairs (last → next): Conclusion → Planning 14; Reflection → Planning 13; Reasoning → Planning 3; Restatement → Planning 2; Knowledge → Planning 2; Planning → Planning 2; Conclusion → Conclusion 1.

