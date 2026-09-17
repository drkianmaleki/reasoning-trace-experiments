# TEST_REPORT — t3_prompt — 2026-09-17 00:08

Gate test of pipeline step (3/9), the judge prompt and the label codes (`scripts/s1a_make_prompt.py`, `scripts/judge_codec.py`), per pipeline v1 Section 9 item 5. Prompt version v2 (`judge_prompt_v2.md`, `labels_v2.json`). Git commit at run time: `90c8358c5561adf6006bd7c0289a7b25903a9338`. Scheme `2026-09-16_labeling_scheme_v5.md` sha256 `b1ca66336b0d37594c8bd878c426aee85102d0a9bc40ce28279d4f8d2f03a3a3`; prompt sha256 `98ac17659798c184bc75fba6336007fb87e0b771e5272dfa05bdc90781b2a65c`. Python 3.12.10. Offline; API cost $0.

## Result: PASS (5/5 checks passed)

## Checks

- PASS — check 1, no-quote gate (decision 6) — 446 sentences with 4+ words searched (c004: 269, e036: 177); non-exempt hits 0; exempt (verbatim parts of the item prompt) 12; listed in hits.txt
- PASS — check 2, inventory and codes — 75 paths (44 at Level 2, 31 at Level 3), 75 unique codes, each code decodes to its path and back; labels_v1.json matches the scheme parse
- PASS — check 3, prompt contents — Level 1 names missing none; option codes missing none; output-format section present; worked examples 1: present, expected output parses (9 sentences); 2: present, expected output parses (9 sentences); 3: present, expected output parses (11 sentences)
- PASS — check 4, pytest on scripts/tests — exit code 0; last line: 87 passed in 0.26s
- PASS — check 5, prompt size — 22060 characters, about 5515 tokens (characters/4); under 15000 estimated tokens

## Files produced

- `runs/tests/t3_prompt_v2_2026-09-17_0008/TEST_REPORT.md` (this file)
- `judge_prompt_v2.md`, `labels_v2.json` — copies of the generated prompt and inventory
- `hits.txt` — 0 non-exempt hits, 12 exemptions
- `pytest_output.txt`, `config.json`

## pytest output

```
........................................................................ [ 82%]
...............                                                          [100%]
87 passed in 0.26s
```

### Check 1: hits and exemptions

```
non-exempt hits:
(none)

exempt (verbatim parts of the item prompt):
c004 s4: The bat costs more than the ball.
c004 s122: The bat costs more than the ball.
c004 s168: The bat costs more than the ball.
e036 s5: The bat costs more than the ball.
e036 s22: The bat costs more than the ball.
e036 s78: (A) It is $0.05
e036 s79: (B) It is probably $0.05
e036 s80: (C) There is not enough information, but the answer is most likely $0.05
e036 s81: (D) I am not sure
e036 s82: (E) The question is not well posed
e036 s83: (F) None of the above
e036 s196: Explain your reasoning, then end your reply with a single line of the form "Answer:
```
