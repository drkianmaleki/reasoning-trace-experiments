#!/usr/bin/env python3
"""s2_resample.py -- pipeline v2 step (7/9), the registered stage-one run (pre-registration
2026-09-17 v2, Sections 3 and 8): resampling of the two source traces at every block-end cut on
DeepInfra raw completions.

  python scripts/s2_resample.py --dry-run                      # prompts, prefix check, estimates; no call
  python scripts/s2_resample.py [--out runs/experiments/resample_blocks_<stamp>/]
  python scripts/s2_resample.py --trace c004 --skip-baselines --resume <folder>   # one trace, in parallel
  python scripts/s2_resample.py --resume <folder>              # continue from the last complete cut

Design (asserted before anything else): the reviewed blocks of listing v4 derived with rule R4
(scripts/derivation.py, texts from sentences_source.jsonl) must end exactly at the 46 (c004) and
37 (e036) registered block-end indices.  Conditions in the registered order: the no-think
baseline (n_0 = 100, prefill <think>\\n\\n</think>\\n\\n, max_tokens 8000), cut-0 (n = 25, prefill
<think>\\n), then the C-trace cuts m = 0, 1, ... and the E-trace cuts.  Prefix = raw trace text
[0, char_end of the block's last sentence); prompt = the archived template with the item prompt
of action summary v6 Section 4; the exact prompt string is stored in every record.  Sampling:
Qwen/Qwen3.6-27B, temperature 1.0, max_tokens 16000, 4 workers, timeout 600 s, the archived
stop sequence <|im_end|> (v2, 2.3).  Scoring: scripts/scorer.py.  After each cut: P_hat_m with "?" in
the denominator, the Wilson 95% interval, the stopping rule (P_hat_m = 1 -> M, no later cut of
that trace), Tk(B_m) from prompt_tokens differences, the cost from usage; a row of pcut.csv, a
line of _log.txt.  DEPARTURES.md is created empty at the start and appended for every deviation
(a retried call, a changed cap, a failed slug check, a short cut).  Cost guard: the run stops
when the cumulative sampling cost passes $45.  Keys from .env (DEEPINFRA_API_KEY), never printed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import derivation as D  # noqa: E402
import s0_split as S0  # noqa: E402
import s1a_make_prompt as P  # noqa: E402
import scorer as SC  # noqa: E402
import stats_utils as ST  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
ENV_FILE = REPO / ".env"
BASE_URL = "https://api.deepinfra.com/v1/openai"
ENDPOINT = BASE_URL + "/completions"
MODEL = "Qwen/Qwen3.6-27B"
TPL = "<|im_start|>user\n{p}<|im_end|>\n<|im_start|>assistant\n<think>\n{pre}"
NOTHINK_PRE = "\n</think>\n\n"          # the template then reads <think>\n\n</think>\n\n (pipeline Section 5 item 8)
# Pre-registration v2, 2.3: the archived stop sequence <|im_end|> (v1 wrote "no stop sequence"
# in error; the archived script sent the stop and no archived completion contains the marker).
STOP = ["<|im_end|>"]
N0, N = 100, 25
TEMPERATURE = 1.0
# v2, 3.1: the no-think cap is 8000 (v1: 2000; seven of ten smoke replies were cut off before
# their answer line); a reply still without a letter at 8000 tokens is "?".
MAX_TOKENS, MAX_TOKENS_NOTHINK = 16000, 8000
WORKERS, TIMEOUT = 4, 600
COST_CEILING_USD = 45.0
RETRIES = 3
PRICES = {"input": 0.32, "output": 3.20}  # USD per million tokens, DeepInfra August 2026 (fallback when usage has no estimated_cost)
A_T = {"c004": "C", "e036": "E"}
TK_TRACE = {"c004": 4740, "e036": 2890}   # sweep records' reasoning_tokens (registration 3.8)
# Pre-registration Section 3 items 3 and 4: the block-end sentence indices under R4
REGISTERED_ENDS = {
    "c004": [7, 12, 14, 22, 30, 35, 41, 42, 57, 78, 97, 106, 113, 115, 119, 131, 136, 143, 147, 159, 165, 170, 186, 189, 192, 198,
             201, 208, 215, 226, 228, 253, 262, 265, 276, 287, 301, 324, 329, 339, 341, 343, 351, 355, 361, 373],
    "e036": [11, 15, 18, 19, 41, 52, 70, 74, 76, 92, 95, 99, 104, 116, 119, 133, 143, 151, 153, 165, 167, 173, 176, 178, 181, 186,
             192, 198, 203, 206, 212, 214, 219, 227, 244, 246, 250],
}
# archived per-continuation means (pipeline Section 8 item 1) for the dry-run projection
EXPECTED_COMPLETION_TOKENS = {"nothink": 400, "cut0": 4450, "c004": 9490, "e036": 2391}
PCUT_FIELDS = ["trace_id", "m", "condition", "prefix_id", "block_end_s", "prefix_char_end", "n", "count_A", "count_B", "count_C", "count_D",
               "count_E", "count_F", "count_other", "count_unresolved", "p_hat", "ci_low", "ci_high", "prompt_tokens", "tk_block",
               "mean_completion_tokens", "cost_usd", "stopped", "think_reopened", "timestamp"]


# ----------------------------------------------------------------------------
# Design
# ----------------------------------------------------------------------------

def load_env(path: Path = ENV_FILE) -> dict[str, str]:
    env: dict[str, str] = {}
    if not Path(path).exists():
        return env
    for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        name, value = s.split("=", 1)
        env[name.strip().removeprefix("export ").strip()] = value.strip().strip("\"'")
    return env


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def git_head() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None


def load_design(listing_path: Path | str = D.LISTING, sentences_source: Path | str = D.SENTENCES_SOURCE,
                sweep_file: Path = S0.SWEEP_FILE, summary_path: Path = P.SUMMARY) -> dict:
    """The traces, their blocks under R4, the 83 prefixes, the item prompt and the options; the
    block ends are asserted against the registered lists before anything else."""
    listing = D.parse_listing(listing_path)
    texts = D.load_sentence_texts(sentences_source)
    sents: dict[str, list[dict]] = {}
    with open(sentences_source, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                sents.setdefault(r["trace_id"], []).append(r)
    records = {S0.SOURCE_SAMPLES[r["sample"]]: r for r in S0.load_sweep_condition(sweep_file) if r.get("sample") in S0.SOURCE_SAMPLES}
    item = P.item_prompt(Path(summary_path).read_text(encoding="utf-8"))
    traces = {}
    for tid in ("c004", "e036"):
        rec = records[tid]
        if rec["prompt"] != item:
            raise RuntimeError(f"{tid}: the sweep record's prompt differs from action summary v6 Section 4")
        der = D.derive(listing[tid]["labels"], tid, "reviewed_v4", texts[tid])
        ends = [b["s_end"] for b in der["blocks"]][:-1]
        if ends != REGISTERED_ENDS[tid]:
            raise RuntimeError(f"{tid}: derived block ends {ends} differ from the registered list {REGISTERED_ENDS[tid]}")
        text = rec["trace"]
        prefixes = []
        for m, e in enumerate(ends):
            char_end = sents[tid][e]["char_end"]
            prefixes.append({"m": m, "block_end_s": e, "char_end": char_end, "text": text[:char_end], "sha256": sha256_text(text[:char_end])})
        traces[tid] = {"text": text, "sentences": sents[tid], "blocks": [(b["m"], b["s_start"], b["s_end"]) for b in der["blocks"]],
                       "block_ends": ends, "prefixes": prefixes, "a_T": A_T[tid], "tk_trace": TK_TRACE[tid],
                       "reasoning_tokens": (rec.get("usage") or {}).get("completion_tokens_details", {}).get("reasoning_tokens"),
                       "sample": rec["sample"], "options": rec["options"]}
        if traces[tid]["reasoning_tokens"] != TK_TRACE[tid]:
            raise RuntimeError(f"{tid}: sweep record reasoning_tokens {traces[tid]['reasoning_tokens']} != registered {TK_TRACE[tid]}")
    return {"traces": traces, "item_prompt": item, "options": records["c004"]["options"], "template": TPL,
            "listing": str(listing_path), "sentences_source": str(sentences_source), "sweep_file": str(sweep_file)}


def conditions(design: dict, traces: list[str] | None = None, skip_baselines: bool = False, n: int = N, n0: int = N0,
               max_cuts: int | None = None) -> list[dict]:
    """The sampled conditions in the registered order."""
    item = design["item_prompt"]
    conds = []
    if not skip_baselines:
        conds.append({"condition": "nothink", "trace_id": "shared", "m": None, "prefix_id": "rb_nothink", "n": n0,
                      "prefill": NOTHINK_PRE, "max_tokens": MAX_TOKENS_NOTHINK, "prompt": TPL.format(p=item, pre=NOTHINK_PRE),
                      "block_end_s": None, "prefix_char_end": 0})
        conds.append({"condition": "cut0", "trace_id": "shared", "m": None, "prefix_id": "rb_cut0", "n": n,
                      "prefill": "", "max_tokens": MAX_TOKENS, "prompt": TPL.format(p=item, pre=""), "block_end_s": None, "prefix_char_end": 0})
    for tid in traces or ["c004", "e036"]:
        for p in design["traces"][tid]["prefixes"][: (max_cuts if max_cuts is not None else None)]:
            conds.append({"condition": "cut", "trace_id": tid, "m": p["m"], "prefix_id": f"rb_{tid}_B{p['m']:02d}", "n": n,
                          "prefill": p["text"], "max_tokens": MAX_TOKENS, "prompt": TPL.format(p=item, pre=p["text"]),
                          "block_end_s": p["block_end_s"], "prefix_char_end": p["char_end"]})
    return conds


def check_prefixes(design: dict) -> dict:
    """Every prefix ends exactly at char_end of its registered block-end sentence and its last
    characters are that sentence's text."""
    out = {}
    for tid, t in design["traces"].items():
        ok = 0
        for p in t["prefixes"]:
            s = t["sentences"][p["block_end_s"]]
            raw_sentence = t["text"][s["char_start"]:s["char_end"]]
            if p["text"].endswith(raw_sentence) and len(p["text"]) == s["char_end"] and p["block_end_s"] == REGISTERED_ENDS[tid][p["m"]]:
                ok += 1
        out[tid] = {"prefixes": len(t["prefixes"]), "matched": ok, "registered": len(REGISTERED_ENDS[tid])}
    return out


def estimate(conds: list[dict]) -> dict:
    """Prompt tokens (characters/4) and a cost projection per trace, with and without the
    stopping rule (the archived P_hat = 1 cuts lie in C-B09 and E-B06: 10 and 7 cuts)."""
    per_trace: dict[str, dict] = {}
    for c in conds:
        key = c["trace_id"] if c["condition"] == "cut" else c["condition"]
        pt = len(c["prompt"]) / 4
        comp = EXPECTED_COMPLETION_TOKENS[key]
        cost = c["n"] * (pt * PRICES["input"] + comp * PRICES["output"]) / 1e6
        d = per_trace.setdefault(key, {"conditions": 0, "calls": 0, "prompt_tokens_est": 0.0, "cost_est_usd": 0.0, "cost_est_stop_usd": 0.0})
        d["conditions"] += 1
        d["calls"] += c["n"]
        d["prompt_tokens_est"] += pt
        d["cost_est_usd"] += cost
        stop_m = {"c004": 9, "e036": 6}.get(key)
        if c["condition"] != "cut" or (stop_m is not None and c["m"] <= stop_m):
            d["cost_est_stop_usd"] += cost
    total = {"cost_est_usd": sum(d["cost_est_usd"] for d in per_trace.values()),
             "cost_est_stop_usd": sum(d["cost_est_stop_usd"] for d in per_trace.values()),
             "calls": sum(d["calls"] for d in per_trace.values())}
    return {"per_trace": per_trace, "total": total, "assumptions": {"prompt_tokens": "characters/4", "completion_tokens": EXPECTED_COMPLETION_TOKENS,
                                                                     "prices_usd_per_million": PRICES, "stop_at": {"c004": "C-B09", "e036": "E-B06"}}}


# ----------------------------------------------------------------------------
# Calls
# ----------------------------------------------------------------------------

def make_post(env_path: Path = ENV_FILE):
    """A callable post(payload, timeout) -> response body dict, holding the key in a closure."""
    import requests
    key = load_env(env_path).get("DEEPINFRA_API_KEY", "")
    if not key or "your-" in key.lower():
        raise RuntimeError("DEEPINFRA_API_KEY missing or placeholder in .env")
    headers = {"Authorization": f"bearer {key}"}

    def post(payload: dict, timeout: float = TIMEOUT) -> dict:
        r = requests.post(ENDPOINT, headers=headers, json=payload, timeout=timeout)
        try:
            body = r.json()
        except ValueError:
            body = {"raw_text": r.text[:500]}
        body["_status"] = r.status_code
        return body
    return post


def slug_check(post) -> dict:
    body = post({"model": MODEL, "prompt": "OK", "max_tokens": 1, "temperature": 0}, timeout=60)
    ok = body.get("_status") == 200 and "choices" in body
    return {"ok": ok, "status": body.get("_status"), "model_echoed": body.get("model"), "usage": body.get("usage"),
            "text": (body.get("choices") or [{}])[0].get("text") if ok else None,
            "error": None if ok else json.dumps({k: v for k, v in body.items() if k != "_status"})[:300]}


def completion_cost(usage: dict) -> float:
    if usage.get("estimated_cost") is not None:
        return float(usage["estimated_cost"])
    return (usage.get("prompt_tokens", 0) * PRICES["input"] + usage.get("completion_tokens", 0) * PRICES["output"]) / 1e6


def sample_one(post, cond: dict, seq: int, options: dict, departures: list[str], sleep=time.sleep) -> dict | None:
    """One continuation: up to RETRIES calls; every retry is appended to `departures` (a list
    private to this call; the caller writes it out).  Returns the record (archived format plus
    block, prefix_char_end, prompt, condition) or None."""
    rid = f"{cond['prefix_id']}_{seq:03d}"
    payload = {"model": MODEL, "prompt": cond["prompt"], "temperature": TEMPERATURE, "max_tokens": cond["max_tokens"], "stop": STOP}
    last = "?"
    for attempt in range(1, RETRIES + 1):
        try:
            body = post(payload, TIMEOUT)
            if body.get("_status") != 200 or "choices" not in body:
                raise RuntimeError(f"status {body.get('_status')}: {json.dumps({k: v for k, v in body.items() if k != '_status'})[:200]}")
            ch = body["choices"][0]
            text = ch.get("text") or ""
            finish = ch.get("finish_reason")
            if finish is None or not text.strip():
                raise RuntimeError("dropped or blank completion")
            usage = body.get("usage") or {}
            sc = SC.score(text, "".join(options))
            reopened = cond["condition"] == "nothink" and "<think>" in text
            return {"id": rid, "prefix_id": cond["prefix_id"], "trace_arm": cond["trace_id"], "cut": cond["block_end_s"],
                    "block": cond["m"], "condition": cond["condition"], "prefix_char_end": cond["prefix_char_end"], "seq": seq,
                    "letters": sc["letters"], "chosen": [options[L] for L in sc["letters"]], "answer": sc["answer"],
                    "think_closed": sc["think_closed"] if cond["condition"] != "nothink" else True, "think_reopened": reopened,
                    "finish": finish, "cont_len": len(text), "cont_text": text, "usage": usage, "cost_usd": completion_cost(usage),
                    "model": body.get("model"), "prompt": cond["prompt"], "attempt": attempt,
                    "timestamp": datetime.now().isoformat(timespec="seconds")}
        except Exception as e:  # transport or API failure: retry with backoff, recorded as a departure
            last = str(e)[:200]
            departures.append(f"retried call {rid} (attempt {attempt} of {RETRIES} failed): {last}")
            if attempt < RETRIES:
                sleep(10 * attempt)
    departures.append(f"failed call {rid} after {RETRIES} attempts: {last}")
    return None


def append_line(path: Path, line: str) -> None:
    """One whole-line append (os-level, so that two processes sharing a file do not interleave)."""
    fd = os.open(str(path), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, (line.rstrip("\n") + "\n").encode("utf-8"))
    finally:
        os.close(fd)


# ----------------------------------------------------------------------------
# Per-cut summary
# ----------------------------------------------------------------------------

def summarize(records: list[dict], cond: dict, a_t: str | None, prev_prompt_tokens: int | None) -> dict:
    """A pcut.csv row (pipeline Section 3 item 8 plus letter counts): P_hat of a_T with "?" in
    the denominator, Wilson 95%, Tk(B_m) = prompt_tokens - prompt_tokens of the previous cut."""
    n = len(records)
    counts = {L: sum(1 for r in records if r["answer"] == L) for L in SC.VALID}
    unresolved = sum(1 for r in records if r["answer"] == "?")
    target = a_t if a_t else None
    k = counts[target] if target else None
    p = (k / n) if (target and n) else None
    lo, hi = ST.wilson(k, n) if (target and n) else (None, None)
    pts = sorted({r["usage"].get("prompt_tokens") for r in records if r.get("usage")} - {None})
    prompt_tokens = pts[0] if pts else None
    tk = (prompt_tokens - prev_prompt_tokens) if (prompt_tokens is not None and prev_prompt_tokens is not None and cond["condition"] == "cut") else None
    return {"trace_id": cond["trace_id"], "m": cond["condition"] if cond["condition"] != "cut" else cond["m"], "condition": cond["condition"],
            "prefix_id": cond["prefix_id"], "block_end_s": cond["block_end_s"], "prefix_char_end": cond["prefix_char_end"], "n": n,
            **{f"count_{L}": counts[L] for L in SC.VALID},
            "count_other": n - unresolved - (counts["C"] + counts["E"]), "count_unresolved": unresolved,
            "p_hat": None if p is None else round(p, 4), "ci_low": None if lo is None else round(lo, 4), "ci_high": None if hi is None else round(hi, 4),
            "prompt_tokens": prompt_tokens, "prompt_tokens_distinct": len(pts), "tk_block": tk,
            "mean_completion_tokens": round(sum(r["usage"].get("completion_tokens", 0) for r in records) / n, 1) if n else None,
            "cost_usd": round(sum(r.get("cost_usd", 0.0) for r in records), 6),
            "stopped": bool(target and n and k == n), "think_reopened": sum(1 for r in records if r.get("think_reopened")),
            "timestamp": datetime.now().isoformat(timespec="seconds")}


def write_pcut_row(path: Path, row: dict) -> None:
    new = not path.exists() or path.stat().st_size == 0
    with open(path, "a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=PCUT_FIELDS, extrasaction="ignore")
        if new:
            w.writeheader()
        w.writerow(row)


def read_pcut(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def read_records(path: Path) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    if not path.exists():
        return out
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                out.setdefault(r["prefix_id"], []).append(r)
    return out


# ----------------------------------------------------------------------------
# The run
# ----------------------------------------------------------------------------

def run(out_dir: Path, design: dict, conds: list[dict], post=None, workers: int = WORKERS, dry_run: bool = False,
        cost_ceiling: float = COST_CEILING_USD, log=print, sleep=time.sleep, resume: bool = False, label: str = "run") -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cont_path, pcut_path, log_path, dep_path = out_dir / "continuations.jsonl", out_dir / "pcut.csv", out_dir / "_log.txt", out_dir / "DEPARTURES.md"
    if not dep_path.exists():
        dep_path.write_text("", encoding="utf-8")
    config_path = out_dir / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8")) if (resume and config_path.exists()) else {}
    config.update({
        "run_id": out_dir.name, "label": label, "endpoint": ENDPOINT, "model": MODEL, "template": TPL, "nothink_prefill": TPL.format(p="{p}", pre=NOTHINK_PRE)[-len("<think>\n\n</think>\n\n"):],
        "stop": STOP, "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS, "max_tokens_nothink": MAX_TOKENS_NOTHINK, "workers": workers,
        "timeout_s": TIMEOUT, "retries": RETRIES, "n": N, "n0": N0, "cost_ceiling_usd": cost_ceiling, "prices_usd_per_million": PRICES,
        "item_prompt_sha256": sha256_text(design["item_prompt"]), "options": design["options"], "listing": design["listing"],
        "sentences_source": design["sentences_source"], "sweep_file": design["sweep_file"], "registered_ends": REGISTERED_ENDS,
        "a_T": A_T, "tk_trace": TK_TRACE, "conditions_this_process": [c["prefix_id"] for c in conds], "git_commit": git_head(),
        "python": sys.version.split()[0], "timestamp": datetime.now().isoformat(timespec="seconds"), "dry_run": dry_run,
        "prefix_check": check_prefixes(design), "estimate": estimate(conds),
    })
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = {"out_dir": str(out_dir), "conditions": len(conds), "rows": [], "cost_usd": 0.0, "stopped": None, "M": {}, "departures": 0}
    if dry_run:
        with open(out_dir / "prompts_dry_run.jsonl", "w", encoding="utf-8", newline="\n") as fh:
            for c in conds:
                fh.write(json.dumps({k: v for k, v in c.items() if k != "prefill"}, ensure_ascii=False) + "\n")
        summary["prefix_check"] = config["prefix_check"]
        summary["estimate"] = config["estimate"]
        return summary
    if post is None:
        post = make_post()
    lock = threading.RLock()

    def departure(msg: str):
        with lock:
            append_line(dep_path, f"- {datetime.now().isoformat(timespec='seconds')} {msg}")
            summary["departures"] += 1

    def sample_and_note(cond: dict, seq: int) -> tuple[dict | None, list[str]]:
        notes: list[str] = []
        rec = sample_one(post, cond, seq, design["options"], notes, sleep)
        return rec, notes

    # slug check (t0 pattern)
    sc = slug_check(post)
    config["slug_check"] = sc
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    append_line(log_path, f"# s2_resample {label} {config['timestamp']} slug check {'PASS' if sc['ok'] else 'FAIL'}: model {sc['model_echoed']!r} status {sc['status']}")
    if not sc["ok"]:
        departure(f"slug check failed: status {sc['status']}, {sc['error']}; run aborted before any sampling")
        summary["stopped"] = "slug check failed"
        return summary
    # state on disk (resume)
    existing = read_records(cont_path)
    prior_rows = read_pcut(pcut_path)
    prompt_tokens_of: dict[str, int | None] = {r["prefix_id"]: (int(r["prompt_tokens"]) if r.get("prompt_tokens") else None) for r in prior_rows}
    cost_so_far = sum(float(r["cost_usd"] or 0) for r in prior_rows) + 0.0
    stopped = {tid: any(r["trace_id"] == tid and r["stopped"] == "True" for r in prior_rows) for tid in A_T}
    done_prefixes = {r["prefix_id"] for r in prior_rows}
    summary["cost_usd"] = cost_so_far
    for cond in conds:
        pid, tid = cond["prefix_id"], cond["trace_id"]
        if pid in done_prefixes:
            log(f"{pid}: already complete (pcut row present), skipped")
            continue
        if cond["condition"] == "cut" and stopped.get(tid):
            append_line(log_path, f"{pid}\tskipped: trace {tid} stopped by the rule at an earlier cut")
            continue
        if cost_so_far >= cost_ceiling:
            departure(f"cost ceiling ${cost_ceiling:.2f} reached (${cost_so_far:.2f}) before {pid}; run stopped")
            summary["stopped"] = f"cost ceiling before {pid}"
            break
        have = {r["seq"]: r for r in existing.get(pid, [])}
        missing = [s for s in range(cond["n"]) if s not in have]
        if have and missing:
            departure(f"{pid}: resumed with {len(have)} continuations on disk, {len(missing)} still to sample")
        a_t = A_T.get(tid)
        t0 = time.monotonic()
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(sample_and_note, cond, s): s for s in missing}
            for fut in as_completed(futs):
                rec, notes = fut.result()
                with lock:
                    for note in notes:
                        departure(note)
                    if rec is None:
                        continue
                    append_line(cont_path, json.dumps(rec, ensure_ascii=False))
                    have[rec["seq"]] = rec
                    if rec.get("think_reopened"):
                        departure(f"{rec['id']}: the no-think reply reopened <think>")
        # top up to n after failures (each a departure), at most one more round
        short = [s for s in range(cond["n"]) if s not in have]
        if short:
            departure(f"{pid}: {len(short)} continuations failed after {RETRIES} attempts each; one top-up round")
            for s in short:
                rec, notes = sample_and_note(cond, s)
                for note in notes:
                    departure(note)
                if rec is not None:
                    append_line(cont_path, json.dumps(rec, ensure_ascii=False))
                    have[rec["seq"]] = rec
        records = [have[s] for s in sorted(have)]
        if len(records) < cond["n"]:
            departure(f"{pid}: short cut, {len(records)} of {cond['n']} continuations; P_hat computed over the {len(records)} obtained")
        prev = None
        if cond["condition"] == "cut":
            prev_pid = "rb_cut0" if cond["m"] == 0 else f"rb_{tid}_B{cond['m'] - 1:02d}"
            prev = prompt_tokens_of.get(prev_pid)
            if prev is None:
                departure(f"{pid}: prompt_tokens of the previous cut ({prev_pid}) unknown in this folder; Tk(B_m) left empty")
        row = summarize(records, cond, a_t, prev)
        prompt_tokens_of[pid] = row["prompt_tokens"]
        if row.get("prompt_tokens_distinct", 1) > 1:
            departure(f"{pid}: prompt_tokens not constant over the continuations ({row['prompt_tokens_distinct']} values); the smallest is used for Tk")
        write_pcut_row(pcut_path, row)
        cost_so_far += row["cost_usd"]
        summary["cost_usd"] = cost_so_far
        summary["rows"].append(row)
        done_prefixes.add(pid)
        append_line(log_path, f"{pid}\tn={row['n']}\tcounts A{row['count_A']} B{row['count_B']} C{row['count_C']} D{row['count_D']} E{row['count_E']} F{row['count_F']} ?{row['count_unresolved']}"
                    f"\tp_hat={row['p_hat']}\tci=[{row['ci_low']}, {row['ci_high']}]\tprompt_tokens={row['prompt_tokens']}\ttk_block={row['tk_block']}"
                    f"\tmean_completion={row['mean_completion_tokens']}\tcost={row['cost_usd']:.4f}\tcum=${cost_so_far:.2f}\tstopped={row['stopped']}\t{time.monotonic() - t0:.0f}s")
        log(f"{pid}: n {row['n']}, p_hat {row['p_hat']} [{row['ci_low']}, {row['ci_high']}], Tk {row['tk_block']}, cost ${row['cost_usd']:.4f}, cumulative ${cost_so_far:.2f}")
        if row["stopped"] and cond["condition"] == "cut":
            stopped[tid] = True
            summary["M"][tid] = cond["m"]
            append_line(log_path, f"# stopping rule: {tid} P_hat = 1 at m = {cond['m']}; M = {cond['m']}; later cuts of {tid} not sampled")
    config["cost_usd_this_process"] = cost_so_far
    config["M"] = summary["M"]
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Pipeline step (7/9): the registered stage-one resampling run.")
    ap.add_argument("--out", help="run folder (default runs/experiments/resample_blocks_<date>_<hhmm>/)")
    ap.add_argument("--resume", help="an existing run folder: continue from the last complete cut")
    ap.add_argument("--dry-run", action="store_true", help="build every prompt, check the prefixes, estimate; no call")
    ap.add_argument("--trace", action="append", choices=["c004", "e036"], help="only this trace's cuts (repeatable)")
    ap.add_argument("--skip-baselines", action="store_true", help="do not sample the no-think baseline and cut-0 in this process")
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--cost-ceiling", type=float, default=COST_CEILING_USD)
    args = ap.parse_args(argv)
    design = load_design()
    conds = conditions(design, args.trace, args.skip_baselines)
    out_dir = Path(args.resume) if args.resume else (Path(args.out) if args.out else REPO / "runs" / "experiments" / f"resample_blocks_{datetime.now():%Y-%m-%d_%H%M}")
    print(f"s2_resample: out={out_dir} conditions={len(conds)} dry_run={args.dry_run} resume={bool(args.resume)} traces={args.trace or ['c004', 'e036']} "
          f"skip_baselines={args.skip_baselines} git={git_head()}")
    summary = run(out_dir, design, conds, dry_run=args.dry_run, workers=args.workers, cost_ceiling=args.cost_ceiling, resume=bool(args.resume))
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=2, default=str))
    return 0 if not summary["stopped"] else 1


if __name__ == "__main__":
    sys.exit(main())
