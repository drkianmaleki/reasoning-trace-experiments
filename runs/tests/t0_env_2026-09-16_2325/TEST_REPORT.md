# TEST_REPORT — t0_env — 2026-09-16 23:25

Environment test (pipeline v1, Section 9 item 2). Git commit `3954b3cc8baf1b0b385ba05a658209ea36ad74f9`; anthropic 1.6.0, requests 2.34.2, pytest 9.1.1; Python 3.12.10. API cost of this test: $0.000050 (Claude at $1/$5 per million tokens; DeepInfra's own estimated_cost).

## Result: PASS (5/5 checks passed)

## Diagnosis of the .env situation (recorded before any API call; no values)

```
git rev-parse --show-toplevel: <repo root>
current working directory: <repo root>
.env file opened: <repo root>\.env (exists: True)
files in the repo root whose name starts with '.env':
  .env  174 bytes  modified 2026-09-16T23:00:25
  .env.example  86 bytes  modified 2026-09-16T14:42:46
other .env-like files: ['.env.example']
variables in the opened file (2):
  CLAUDE_API_KEY: value length 108, placeholder False
  DEEPINFRA_API_KEY: value length 32, placeholder False
```

## Checks

- PASS — key CLAUDE_API_KEY in .env — present: True; non-placeholder: True; length 108 characters
- PASS — key DEEPINFRA_API_KEY in .env — present: True; non-placeholder: True; length 32 characters
- PASS — Claude endpoint — model echoed 'claude-haiku-4-5-20251001'; stop reason end_turn; usage 14 in / 4 out; reply 'OK'; cost $0.000034
- PASS — DeepInfra endpoint — status 200; model echoed 'Qwen/Qwen3.6-27B'; usage {'prompt_tokens': 1, 'total_tokens': 6, 'completion_tokens': 5, 'estimated_cost': 1.632e-05, 'prompt_tokens_details': None}; estimated_cost 1.632e-05; text '     '
- PASS — self-check, no key value in any file of the test folder — 3 files searched for the 2 key value(s) found in .env; leaks: none

## Files produced

- `runs/tests/t0_env_2026-09-16_2325/TEST_REPORT.md` (this file), `config.json`, `responses.json` (scrubbed API responses)
