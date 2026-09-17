#!/usr/bin/env python3
"""t0_env -- environment test (pipeline v1, Section 9 item 2): the two API keys load from .env
and never appear in any output; each endpoint answers a one-token request; config.json records
the git commit and the installed package versions.

Writes runs/tests/t0_env_<YYYY-MM-DD>_<HHMM>/TEST_REPORT.md, config.json, responses.json.
Cost: cents (two tiny calls).  Keys are read from .env only and are never printed, logged or
written; every recorded string is scrubbed of the key values, and the report ends with a search
of the test folder for them.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ENV_FILE = REPO / ".env"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
DEEPINFRA_MODEL = "Qwen/Qwen3.6-27B"
DEEPINFRA_URL = "https://api.deepinfra.com/v1/openai/completions"
KEY_NAMES = ("CLAUDE_API_KEY", "DEEPINFRA_API_KEY")
PRICE_CLAUDE_IN, PRICE_CLAUDE_OUT = 1.0, 5.0  # USD per million tokens, Haiku 4.5 (verified 2026-09-15)


def load_env(path: Path) -> dict[str, str]:
    """KEY=value lines; comments and blanks ignored; surrounding quotes stripped."""
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        name, value = s.split("=", 1)
        name = name.strip()
        if name.startswith("export "):
            name = name[7:].strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        env[name] = value
    return env


def git_head() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    stamp = datetime.now()
    folder = REPO / "runs" / "tests" / f"t0_env_{stamp:%Y-%m-%d_%H%M}"
    folder.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    verdicts: list[bool] = []
    secrets: list[str] = []

    def scrub(s) -> str:
        s = str(s)
        for v in secrets:
            if v:
                s = s.replace(v, "<redacted>")
        return s

    def check(ok: bool, name: str, numbers: str):
        verdicts.append(ok)
        lines.append(scrub(f"- {'PASS' if ok else 'FAIL'} — {name} — {numbers}"))
        print(lines[-1])

    # ---- diagnosis of the .env situation (no values; recorded before any API call) ----------------
    diagnosis: list[str] = []
    try:
        toplevel = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=REPO, capture_output=True,
                                  text=True, check=True).stdout.strip()
    except Exception as e:
        toplevel = f"(git error: {e})"
    diagnosis.append(f"git rev-parse --show-toplevel: {toplevel}")
    diagnosis.append(f"current working directory: {Path.cwd()}")
    diagnosis.append(f".env file opened: {ENV_FILE.resolve()} (exists: {ENV_FILE.exists()})")
    env_like = sorted(p for p in REPO.iterdir() if p.name.startswith(".env"))
    diagnosis.append("files in the repo root whose name starts with '.env':")
    for p in env_like:
        st = p.stat()
        diagnosis.append(f"  {p.name}  {st.st_size} bytes  modified {datetime.fromtimestamp(st.st_mtime).isoformat(timespec='seconds')}")
    others = [p.name for p in env_like if p != ENV_FILE]
    diagnosis.append(f"other .env-like files: {others if others else 'none'}")
    env = load_env(ENV_FILE)
    diagnosis.append(f"variables in the opened file ({len(env)}):")
    for name, value in env.items():
        diagnosis.append(f"  {name}: value length {len(value)}, placeholder {(not value) or ('your-' in value.lower())}")
    for d in diagnosis:
        print("  " + d)
    secrets = [env.get(k, "") for k in KEY_NAMES if env.get(k)]
    key_ok: dict[str, bool] = {}
    for name in KEY_NAMES:
        value = env.get(name, "")
        present = name in env
        placeholder = (not value) or ("your-" in value.lower())
        key_ok[name] = present and not placeholder
        check(key_ok[name], f"key {name} in .env",
              f"present: {present}; non-placeholder: {not placeholder}; length {len(value)} characters"
              + ("" if present else f"; variables found in .env: {sorted(env)}"))
    if not all(key_ok.values()):
        print("  keys missing or placeholders: no API call is attempted")

    responses: dict = {}

    # ---- Claude ------------------------------------------------------------------------------
    import anthropic  # third-party, pinned in requirements.txt
    if key_ok["CLAUDE_API_KEY"]:
        try:
            client = anthropic.Anthropic(api_key=env["CLAUDE_API_KEY"])
            # anthropic 1.x removed `temperature` as a named argument of messages.create (sampling
            # parameters are gone on current models); Haiku 4.5 still accepts it on the wire, so it
            # is passed through extra_body.  The judge script must do the same.
            msg = client.messages.create(model=CLAUDE_MODEL, max_tokens=5, extra_body={"temperature": 0},
                                         messages=[{"role": "user", "content": "Reply with the single word OK."}])
            reply = "".join(getattr(b, "text", "") for b in msg.content)
            usage = {"input_tokens": msg.usage.input_tokens, "output_tokens": msg.usage.output_tokens}
            cost = (usage["input_tokens"] * PRICE_CLAUDE_IN + usage["output_tokens"] * PRICE_CLAUDE_OUT) / 1e6
            responses["claude"] = {"model": msg.model, "stop_reason": msg.stop_reason, "usage": usage,
                                   "reply": reply, "cost_usd": cost}
            check(True, "Claude endpoint", f"model echoed {msg.model!r}; stop reason {msg.stop_reason}; "
                  f"usage {usage['input_tokens']} in / {usage['output_tokens']} out; reply {reply!r}; cost ${cost:.6f}")
        except Exception as e:  # recorded verbatim (scrubbed), never raised past the report
            responses["claude"] = {"error": scrub(repr(e))}
            check(False, "Claude endpoint", f"error: {scrub(repr(e))[:500]}")
    else:
        responses["claude"] = {"skipped": "CLAUDE_API_KEY missing or placeholder"}
        check(False, "Claude endpoint", "not attempted: CLAUDE_API_KEY missing or placeholder")

    # ---- DeepInfra ---------------------------------------------------------------------------
    import requests  # third-party, pinned in requirements.txt
    if key_ok["DEEPINFRA_API_KEY"]:
        try:
            r = requests.post(DEEPINFRA_URL, headers={"Authorization": f"bearer {env['DEEPINFRA_API_KEY']}"},
                              json={"model": DEEPINFRA_MODEL, "prompt": "OK", "max_tokens": 5, "temperature": 0},
                              timeout=60)
            try:
                body = r.json()
            except ValueError:
                body = {"raw_text": r.text}
            body_s = scrub(json.dumps(body, ensure_ascii=False))
            if r.status_code == 200 and isinstance(body, dict) and "choices" in body:
                usage = body.get("usage", {})
                responses["deepinfra"] = {"status": r.status_code, "model": body.get("model"), "usage": usage,
                                          "estimated_cost": usage.get("estimated_cost", body.get("estimated_cost")),
                                          "text": body["choices"][0].get("text", "")}
                check(True, "DeepInfra endpoint", f"status {r.status_code}; model echoed {body.get('model')!r}; usage {usage}; "
                      f"estimated_cost {responses['deepinfra']['estimated_cost']}; text {responses['deepinfra']['text']!r}")
            else:
                responses["deepinfra"] = {"status": r.status_code, "error_body": body_s}
                check(False, "DeepInfra endpoint", f"status {r.status_code}; body: {body_s[:800]} "
                      "(a rejected model slug is a finding about the slug, not about this script)")
        except Exception as e:
            responses["deepinfra"] = {"error": scrub(repr(e))}
            check(False, "DeepInfra endpoint", f"error: {scrub(repr(e))[:500]}")
    else:
        responses["deepinfra"] = {"skipped": "DEEPINFRA_API_KEY missing or placeholder"}
        check(False, "DeepInfra endpoint", "not attempted: DEEPINFRA_API_KEY missing or placeholder")

    # ---- config and artifacts -----------------------------------------------------------------
    import pytest  # for the version only
    config = {
        "git_commit": git_head(),
        "python": sys.version.split()[0],
        "anthropic": anthropic.__version__,
        "requests": requests.__version__,
        "pytest": pytest.__version__,
        "claude_model_requested": CLAUDE_MODEL,
        "deepinfra_model_requested": DEEPINFRA_MODEL,
        "deepinfra_url": DEEPINFRA_URL,
        "env_file": ENV_FILE.name,
        "env_variables_present": sorted(env),
        "timestamp": stamp.isoformat(timespec="seconds"),
    }
    (folder / "config.json").write_text(scrub(json.dumps(config, indent=2)) + "\n", encoding="utf-8")
    (folder / "responses.json").write_text(scrub(json.dumps(responses, indent=2, ensure_ascii=False)) + "\n", encoding="utf-8")
    total_cost = (responses.get("claude", {}).get("cost_usd") or 0) + (responses.get("deepinfra", {}).get("estimated_cost") or 0)

    # ---- self-check: no key value in any file of the test folder ----------------------------------
    report_path = folder / "TEST_REPORT.md"

    def write_report(self_check_line: str):
        gate = all(verdicts)
        text = [
            f"# TEST_REPORT — t0_env — {stamp:%Y-%m-%d %H:%M}",
            "",
            f"Environment test (pipeline v1, Section 9 item 2). Git commit `{config['git_commit']}`; anthropic {config['anthropic']}, requests {config['requests']}, pytest {config['pytest']}; Python {config['python']}. "
            f"API cost of this test: ${total_cost:.6f} (Claude at $1/$5 per million tokens; DeepInfra's own estimated_cost).",
            "",
            f"## Result: {'PASS' if gate else 'FAIL'} ({sum(verdicts)}/{len(verdicts)} checks passed)",
            "",
            "## Diagnosis of the .env situation (recorded before any API call; no values)",
            "",
            "```",
            *diagnosis,
            "```",
            "",
            "## Checks",
            "",
            *lines,
            self_check_line,
            "",
            "## Files produced",
            "",
            f"- `{folder.relative_to(REPO).as_posix()}/TEST_REPORT.md` (this file), `config.json`, `responses.json` (scrubbed API responses)",
        ]
        report_path.write_text(scrub("\n".join(text)) + "\n", encoding="utf-8")

    write_report("- (self-check pending)")
    leaks = []
    for f in folder.iterdir():
        content = f.read_text(encoding="utf-8", errors="replace")
        for name in KEY_NAMES:
            v = env.get(name, "")
            if v and v in content:
                leaks.append(f"{f.name}: {name}")
    ok = not leaks
    verdicts.append(ok)
    line = f"- {'PASS' if ok else 'FAIL'} — self-check, no key value in any file of the test folder — {len(list(folder.iterdir()))} files searched for the {len([k for k in KEY_NAMES if env.get(k)])} key value(s) found in .env; leaks: {leaks or 'none'}"
    lines_len = len(lines)
    write_report(line)
    print(line)
    print(f"\nReport: {report_path}\nGate: {'PASS' if all(verdicts) else 'FAIL'}")
    return 0 if all(verdicts) else 1


if __name__ == "__main__":
    sys.exit(main())
