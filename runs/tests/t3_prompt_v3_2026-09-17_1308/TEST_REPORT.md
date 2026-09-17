# TEST_REPORT — t3_prompt — 2026-09-17 13:08

Gate test of pipeline step (3/9), the judge prompt and the label codes (`scripts/s1a_make_prompt.py`, `scripts/judge_codec.py`), per pipeline v1 Section 9 item 5. Prompt version v3 (`judge_prompt_v3.md`, `labels_v3.json`). Git commit at run time: `cb372474119b2ee1a5b5caa031c6225a0cefd133`. Scheme `2026-09-17_labeling_scheme_v6.md` sha256 `23b86eefd9442bde8637d2b9f7697d36cf7fa95c6f9b5b9fccf90dae3697d0a9`; prompt sha256 `e999f7081d5a285c4db1dcb4fb55f9eb5291b1ba536f770d1ad53a815e43f51a`. Python 3.12.10. Offline; API cost $0.

## Result: FAIL (4/5 checks passed)

## Checks

- PASS — check 1, no-quote gate (decision 6) — 446 sentences with 4+ words searched (c004: 269, e036: 177); non-exempt hits 0; exempt (verbatim parts of the item prompt) 12; listed in hits.txt
- PASS — check 2, inventory and codes — 77 paths (44 at Level 2, 33 at Level 3), 77 unique codes, each code decodes to its path and back; labels_v3.json matches the parse of 2026-09-17_labeling_scheme_v6.md
- PASS — check 3, prompt contents — Level 1 names missing none; option codes missing none; output-format section present; worked examples 1: present, expected output parses (9 sentences); 2: present, expected output parses (9 sentences); 3: present, expected output parses (11 sentences)
- FAIL — check 4, pytest on scripts/tests — exit code 1; last line: 4 failed, 134 passed in 0.57s
- PASS — check 5, prompt size — 23280 characters, about 5820 tokens (characters/4); under 15000 estimated tokens

## Files produced

- `runs/tests/t3_prompt_v3_2026-09-17_1308/TEST_REPORT.md` (this file)
- `judge_prompt_v3.md`, `labels_v3.json` — copies of the generated prompt and inventory
- `hits.txt` — 0 non-exempt hits, 12 exemptions
- `pytest_output.txt`, `config.json`

## pytest output

```
...................F.................................FFF................ [ 52%]
..................................................................       [100%]
================================== FAILURES ===================================
___________________ test_r4_regex[   \u23ce * _Wait_-True] ____________________

text = '   ⏎ * _Wait_', hit = True

    @pytest.mark.parametrize("text,hit", [
        ("Wait, is that right?", True), ("But wait, the classic says $1.00 more.", True), ("⏎⏎    **Wait, hold on.**", True),
        ("(Wait, the classic problem says …", True), ("Oh wait.", True), ("Oh, wait — no.", True), ("Okay, wait.", True), ("And wait, what?", True),
        ("1. Wait a moment.", True), ("- wait, no", True), ("> WAIT", True), ("   ⏎ * _Wait_", True),
        ("Actually, wait.", False), ("Waiting for the sum.", False), ("await the result", False), ("Let me wait.", False),
        ("Hmm, wait.", False), ("", False), ("But", False), ("Wait", True), ("wait.", True),
    ])
    def test_r4_regex(text, hit):
>       assert D.is_r4(text) is hit
E       AssertionError: assert False is True
E        +  where False = <function is_r4 at 0x0000020C1171CA40>('   ⏎ * _Wait_')
E        +    where <function is_r4 at 0x0000020C1171CA40> = D.is_r4

scripts\tests\test_derivation.py:112: AssertionError
________________ test_every_reviewed_path_is_in_the_inventory _________________

inv = <judge_codec.Inventory object at 0x0000020C117FD3D0>

    def test_every_reviewed_path_is_in_the_inventory(inv):
>       used = {p for labels in reviewed_labels().values() for paths in labels for p in paths}
                                ^^^^^^^^^^^^^^^^^

scripts\tests\test_judge_codec.py:94: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

    def reviewed_labels() -> dict[str, list[list[str]]]:
        """{trace: [[path, ...] per sentence]} from the listing's Node column."""
        out: dict[str, list[list[str]]] = {"c004": [], "e036": []}
        trace = None
>       with open(LISTING, encoding="utf-8") as fh:
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       FileNotFoundError: [Errno 2] No such file or directory: 'C:\\Users\\kianu\\Dropbox\\Projects\\Ongoing\\reasoning-trace-experiments\\docs\\shared\\2026-09-16_source_traces_labeled_v3.md'

scripts\tests\test_judge_codec.py:31: FileNotFoundError
__________________ test_round_trip_reviewed_labels[c004-375] __________________

inv = <judge_codec.Inventory object at 0x0000020C117FD3D0>
sentence_counts = {'c004': 375, 'e036': 254}, trace_id = 'c004'
n_expected = 375

    @pytest.mark.parametrize("trace_id,n_expected", [("c004", 375), ("e036", 254)])
    def test_round_trip_reviewed_labels(inv, sentence_counts, trace_id, n_expected):
>       labels = reviewed_labels()[trace_id]
                 ^^^^^^^^^^^^^^^^^

scripts\tests\test_judge_codec.py:106: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

    def reviewed_labels() -> dict[str, list[list[str]]]:
        """{trace: [[path, ...] per sentence]} from the listing's Node column."""
        out: dict[str, list[list[str]]] = {"c004": [], "e036": []}
        trace = None
>       with open(LISTING, encoding="utf-8") as fh:
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       FileNotFoundError: [Errno 2] No such file or directory: 'C:\\Users\\kianu\\Dropbox\\Projects\\Ongoing\\reasoning-trace-experiments\\docs\\shared\\2026-09-16_source_traces_labeled_v3.md'

scripts\tests\test_judge_codec.py:31: FileNotFoundError
__________________ test_round_trip_reviewed_labels[e036-254] __________________

inv = <judge_codec.Inventory object at 0x0000020C117FD3D0>
sentence_counts = {'c004': 375, 'e036': 254}, trace_id = 'e036'
n_expected = 254

    @pytest.mark.parametrize("trace_id,n_expected", [("c004", 375), ("e036", 254)])
    def test_round_trip_reviewed_labels(inv, sentence_counts, trace_id, n_expected):
>       labels = reviewed_labels()[trace_id]
                 ^^^^^^^^^^^^^^^^^

scripts\tests\test_judge_codec.py:106: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

    def reviewed_labels() -> dict[str, list[list[str]]]:
        """{trace: [[path, ...] per sentence]} from the listing's Node column."""
        out: dict[str, list[list[str]]] = {"c004": [], "e036": []}
        trace = None
>       with open(LISTING, encoding="utf-8") as fh:
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       FileNotFoundError: [Errno 2] No such file or directory: 'C:\\Users\\kianu\\Dropbox\\Projects\\Ongoing\\reasoning-trace-experiments\\docs\\shared\\2026-09-16_source_traces_labeled_v3.md'

scripts\tests\test_judge_codec.py:31: FileNotFoundError
=========================== short test summary info ===========================
FAILED scripts/tests/test_derivation.py::test_r4_regex[   \u23ce * _Wait_-True]
FAILED scripts/tests/test_judge_codec.py::test_every_reviewed_path_is_in_the_inventory
FAILED scripts/tests/test_judge_codec.py::test_round_trip_reviewed_labels[c004-375]
FAILED scripts/tests/test_judge_codec.py::test_round_trip_reviewed_labels[e036-254]
4 failed, 134 passed in 0.57s
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
