# TEST_REPORT — t0_env — 2026-09-16 22:47

Environment test (pipeline v1, Section 9 item 2). Git commit `0b91a47476d83c08308adb017bb40b60f2b9e7a8`; anthropic 1.6.0, requests 2.34.2, pytest 9.1.1; Python 3.12.10. API cost of this test: $0.000000 (Claude at $1/$5 per million tokens; DeepInfra's own estimated_cost).

## Result: FAIL (1/5 checks passed)

## Checks

- FAIL — key CLAUDE_API_KEY in .env — present: False; non-placeholder: False; length 0 characters; variables found in .env: ['DEEPINFRA_API_KEY', 'OpenRouter_API_KEY']
- FAIL — key DEEPINFRA_API_KEY in .env — present: True; non-placeholder: False; length 27 characters
- FAIL — Claude endpoint — not attempted: CLAUDE_API_KEY missing or placeholder
- FAIL — DeepInfra endpoint — not attempted: DEEPINFRA_API_KEY missing or placeholder
- PASS — self-check, no key value in any file of the test folder — 3 files searched for the 1 key value(s) found in .env; leaks: none

## Files produced

- `runs/tests/t0_env_2026-09-16_2247/TEST_REPORT.md` (this file), `config.json`, `responses.json` (scrubbed API responses)
