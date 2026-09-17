# TEST_REPORT — t3_prompt — 2026-09-17 13:24

Gate test of pipeline step (3/9), the judge prompt and the label codes (`scripts/s1a_make_prompt.py`, `scripts/judge_codec.py`), per pipeline v1 Section 9 item 5. Prompt version v3 (`judge_prompt_v3.md`, `labels_v3.json`). Git commit at run time: `cb372474119b2ee1a5b5caa031c6225a0cefd133`. Scheme `2026-09-17_labeling_scheme_v6.md` sha256 `23b86eefd9442bde8637d2b9f7697d36cf7fa95c6f9b5b9fccf90dae3697d0a9`; prompt sha256 `e999f7081d5a285c4db1dcb4fb55f9eb5291b1ba536f770d1ad53a815e43f51a`. Python 3.12.10. Offline; API cost $0.

## Result: PASS (5/5 checks passed)

## Checks

- PASS — check 1, no-quote gate (decision 6) — 446 sentences with 4+ words searched (c004: 269, e036: 177); non-exempt hits 0; exempt (verbatim parts of the item prompt) 12; listed in hits.txt
- PASS — check 2, inventory and codes — 77 paths (44 at Level 2, 33 at Level 3), 77 unique codes, each code decodes to its path and back; labels_v3.json matches the parse of 2026-09-17_labeling_scheme_v6.md
- PASS — check 3, prompt contents — Level 1 names missing none; option codes missing none; output-format section present; worked examples 1: present, expected output parses (9 sentences); 2: present, expected output parses (9 sentences); 3: present, expected output parses (11 sentences)
- PASS — check 4, pytest on scripts/tests — exit code 0; last line: 161 passed in 1.90s
- PASS — check 5, prompt size — 23280 characters, about 5820 tokens (characters/4); under 15000 estimated tokens

## Files produced

- `runs/tests/t3_prompt_v3_2026-09-17_1324/TEST_REPORT.md` (this file)
- `judge_prompt_v3.md`, `labels_v3.json` — copies of the generated prompt and inventory
- `hits.txt` — 0 non-exempt hits, 12 exemptions
- `pytest_output.txt`, `config.json`

## pytest output

```
........................................................................ [ 44%]
........................................................................ [ 89%]
.................                                                        [100%]
161 passed in 1.90s
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
