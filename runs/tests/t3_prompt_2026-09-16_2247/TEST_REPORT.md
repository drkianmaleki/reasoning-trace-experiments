# TEST_REPORT — t3_prompt — 2026-09-16 22:47

Gate test of pipeline step (3/9), the judge prompt and the label codes (`scripts/s1a_make_prompt.py`, `scripts/judge_codec.py`), per pipeline v1 Section 9 item 5. Git commit at run time: `0b91a47476d83c08308adb017bb40b60f2b9e7a8`. Scheme `2026-09-16_labeling_scheme_v4.md` sha256 `fe51d18e891eef3331cd7d3b5f3334123c097f39f7340ce7d805b870d7413629`; prompt sha256 `3f1c1aecbae8242353105a757e2215909caadcfa8cf20f0b48fa9b3f316d9c35`. Python 3.12.10. Offline; API cost $0.

## Result: PASS (5/5 checks passed)

## Checks

- PASS — check 1, no-quote gate (decision 6) — 446 sentences with 4+ words searched (c004: 269, e036: 177); non-exempt hits 0; exempt (verbatim parts of the item prompt) 12; listed in hits.txt
- PASS — check 2, inventory and codes — 74 paths (44 at Level 2, 30 at Level 3), 74 unique codes, each code decodes to its path and back; labels_v1.json matches the scheme parse
- PASS — check 3, prompt contents — Level 1 names missing none; option codes missing none; output-format section present; worked examples 1: present, expected output parses (7 sentences); 2: present, expected output parses (8 sentences); 3: present, expected output parses (7 sentences)
- PASS — check 4, pytest on scripts/tests — exit code 0; last line: 56 passed in 0.20s
- PASS — check 5, prompt size — 17667 characters, about 4417 tokens (characters/4); under 15000 estimated tokens

## Files produced

- `runs/tests/t3_prompt_2026-09-16_2247/TEST_REPORT.md` (this file)
- `judge_prompt_v1.md`, `labels_v1.json` — copies of the generated prompt and inventory
- `hits.txt` — 0 non-exempt hits, 12 exemptions
- `pytest_output.txt`, `config.json`

## pytest output

```
........................................................                 [100%]
56 passed in 0.20s
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
