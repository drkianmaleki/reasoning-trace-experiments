#!/usr/bin/env python3
"""s1_judge.py -- pipeline step (4/9): the judge (Claude Haiku 4.5) on a collection of
sentence files, one ordinary call per trace, replies in the run-length code format of
prompts/judge_prompt_v1.md, parsed by judge_codec, one retry, then the derivation.

  python scripts/s1_judge.py --sentences runs/tests/t2_split_2026-09-16_2224/sentences_source.jsonl \
      --mode ordinary --out runs/experiments/judge_source_<date>_<hhmm>/ [--trace e036] [--dry-run] \
      [--reviewed docs/shared/2026-09-16_source_traces_labeled_v3.md]

Request: system = the full prompt as one text block with cache_control ephemeral; user = a
header line, one line per sentence "s<i>: <text>", a closing line; model claude-haiku-4-5-20251001,
max_tokens 8000, temperature 0 via extra_body (anthropic 1.6.0 has no temperature argument).
Outputs in the run folder: labels_<collection>_judge.jsonl, blocks_<collection>_judge.jsonl,
replies/<trace>_attempt<k>.txt, requests/<trace>.json (dry run), config.json, _log.txt, and with
--reviewed: agreement_<collection>.csv, residue_<collection>.csv, confusions_<collection>.csv.
Keys are read from .env (CLAUDE_API_KEY) and never printed, logged or written.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import derivation as D  # noqa: E402
import judge_codec as J  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
PROMPT_FILE = REPO / "prompts" / "judge_prompt_v1.md"
LABELS_FILE = REPO / "prompts" / "labels_v1.json"
ENV_FILE = REPO / ".env"
MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 8000
TEMPERATURE = 0
PRICES = {"input": 1.0, "output": 5.0, "cache_read": 0.10, "cache_write": 1.25}  # USD per million tokens
LEVEL_NAMES = {1: "Level 1", 2: "Level 1 > Level 2", 3: "full path"}
PROMPT_VERSIONS = ("v1", "v2")
# Per-model request options.  Haiku 4.5 accepts sampling parameters (temperature 0 via extra_body,
# since anthropic 1.x has no temperature argument) and runs without thinking when the parameter is
# omitted.  Sonnet 5 rejects sampling parameters with a 400 and runs adaptive thinking unless it is
# disabled explicitly, so no temperature is sent and thinking is disabled.
MODELS = {
    "haiku": {"id": "claude-haiku-4-5-20251001", "temperature": 0, "thinking": None,
              "prices": {"input": 1.0, "output": 5.0, "cache_read": 0.10, "cache_write": 1.25}},
    "sonnet": {"id": "claude-sonnet-5", "temperature": None, "thinking": {"type": "disabled"},
               "prices": {"input": 2.0, "output": 10.0, "cache_read": 0.20, "cache_write": 2.50}},
}


def prompt_files(version: str) -> tuple[Path, Path]:
    if version not in PROMPT_VERSIONS:
        raise ValueError(f"unknown prompt version {version!r}")
    return REPO / "prompts" / f"judge_prompt_{version}.md", REPO / "prompts" / f"labels_{version}.json"


# Thinking modes.  "off" = the current behaviour (Haiku: no thinking parameter; Sonnet: thinking
# disabled).  "low"/"medium" = adaptive thinking at that effort level, documented at
# https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost (fields
# `thinking: {"type": "adaptive", "display": ...}`; effort at `output_config.effort`; thinking is
# billed as output and counted inside max_tokens; the count is `usage.output_tokens_details.
# thinking_tokens`) and https://platform.claude.com/docs/en/build-with-claude/effort (levels).
# Adaptive thinking exists on Sonnet 5 only among the two judges; Haiku 4.5 uses manual budgets.
THINKING_MODES = ("off", "none", "low", "medium")
MAX_TOKENS_THINKING = 24000
# "none" (Kian, 2026-09-17): thinking disabled as in "off" AND the user message ends with this
# extra line, recorded in config.json as reply_instruction.
REPLY_INSTRUCTION = ("Reply with the run-length labels only: no reasoning, no commentary, no tags of any kind, "
                     "nothing before the first run line.")


def thinking_params(model_key: str, mode: str) -> dict:
    if mode not in THINKING_MODES:
        raise ValueError(f"unknown thinking mode {mode!r}; known: {THINKING_MODES}")
    if mode in ("off", "none"):
        return {}
    if model_key != "sonnet":
        raise ValueError("thinking modes low/medium are implemented for Sonnet 5 only (adaptive thinking)")
    return {"thinking": {"type": "adaptive", "display": "summarized"}, "output_config": {"effort": mode}}


def make_run_id(model_key: str, version: str, stamp: datetime | None = None, thinking: str = "off",
                repeat: int | None = None) -> str:
    stamp = stamp or datetime.now()
    tag = f"_think{thinking}" if thinking != "off" else ""
    rep = f"_r{repeat}" if repeat is not None else ""
    return f"judge_source_{model_key}_{version}{tag}{rep}_{stamp:%Y-%m-%d_%H%M}"


# ----------------------------------------------------------------------------
# Inputs
# ----------------------------------------------------------------------------

def sha256_of_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git_head() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None


def load_env(path: Path = ENV_FILE) -> dict[str, str]:
    env: dict[str, str] = {}
    if not Path(path).exists():
        return env
    for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
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


def load_sentences(path: Path) -> dict[str, list[dict]]:
    """{trace_id: [record, ...]} in file order; records must be s = 0..N-1 per trace."""
    out: dict[str, list[dict]] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                out.setdefault(r["trace_id"], []).append(r)
    for tid, recs in out.items():
        if [r["s"] for r in recs] != list(range(len(recs))):
            raise ValueError(f"{tid}: sentence indices are not 0..N-1 in order")
    return out


def collection_name(sentences_path: Path) -> str:
    stem = Path(sentences_path).stem
    return stem[len("sentences_"):] if stem.startswith("sentences_") else stem


# ----------------------------------------------------------------------------
# Requests
# ----------------------------------------------------------------------------

def user_message(trace_id: str, sents: list[dict], extra_line: str | None = None) -> str:
    n = len(sents)
    lines = [f"Trace {trace_id}, {n} sentences, indices s0 to s{n - 1}. Label every sentence."]
    lines += [f"s{r['s']}: {r['text']}" for r in sents]
    lines.append("Output the run-length labels now, nothing else.")
    if extra_line:
        lines.append(extra_line)
    return "\n".join(lines)


def build_request(trace_id: str, sents: list[dict], prompt_text: str, model_key: str = "haiku",
                  thinking_mode: str = "off") -> dict:
    m = MODELS[model_key]
    tp = thinking_params(model_key, thinking_mode)
    extra = REPLY_INSTRUCTION if thinking_mode == "none" else None
    req = {
        "model": m["id"],
        "max_tokens": MAX_TOKENS_THINKING if tp else MAX_TOKENS,
        "system": [{"type": "text", "text": prompt_text, "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": user_message(trace_id, sents, extra)}],
    }
    if m["temperature"] is not None:
        req["extra_body"] = {"temperature": m["temperature"]}
    if tp:
        req.update(tp)
    elif m["thinking"] is not None:
        req["thinking"] = m["thinking"]
    return req


def estimate_input_tokens(request: dict) -> int:
    chars = sum(len(b["text"]) for b in request["system"])
    for m in request["messages"]:
        chars += len(m["content"]) if isinstance(m["content"], str) else sum(len(b.get("text", "")) for b in m["content"])
    return round(chars / 4)


def rejection_message(err: J.ReplyError, n: int) -> str:
    return (f"Your labeling was rejected: {err.kind}: {err.detail} at line {err.line_no}: {err.line}. "
            f"Output the complete labeling again, every index from 0 to {n - 1} exactly once, one run per line, codes only.")


# ----------------------------------------------------------------------------
# Calls
# ----------------------------------------------------------------------------

def usage_dict(usage) -> dict:
    details = getattr(usage, "output_tokens_details", None)
    return {
        "input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
        "output_tokens": int(getattr(usage, "output_tokens", 0) or 0),
        "cache_creation_input_tokens": int(getattr(usage, "cache_creation_input_tokens", 0) or 0),
        "cache_read_input_tokens": int(getattr(usage, "cache_read_input_tokens", 0) or 0),
        "thinking_tokens": int(getattr(details, "thinking_tokens", 0) or 0) if details is not None else 0,
    }


def add_usage(a: dict, b: dict) -> dict:
    return {k: a.get(k, 0) + b.get(k, 0) for k in set(a) | set(b)}


def cost_usd(usage: dict, model_key: str = "haiku") -> float:
    prices = MODELS[model_key]["prices"]
    return (usage.get("input_tokens", 0) * prices["input"]
            + usage.get("output_tokens", 0) * prices["output"]
            + usage.get("cache_read_input_tokens", 0) * prices["cache_read"]
            + usage.get("cache_creation_input_tokens", 0) * prices["cache_write"]) / 1e6


def reply_text(response) -> str:
    """The concatenation of the reply's text blocks only (thinking blocks are never parsed)."""
    return "".join(getattr(b, "text", "") for b in response.content if getattr(b, "type", "") == "text")


def thinking_text(response) -> str:
    """The thinking blocks of a reply (summarized text; a redacted block leaves a marker)."""
    parts = []
    for b in response.content:
        t = getattr(b, "type", "")
        if t == "thinking":
            parts.append(getattr(b, "thinking", "") or "")
        elif t == "redacted_thinking":
            parts.append("[redacted_thinking block]")
    return "\n".join(parts)


def make_client(env_path: Path = ENV_FILE):
    import anthropic  # third-party, pinned in requirements.txt
    key = load_env(env_path).get("CLAUDE_API_KEY", "")
    if not key or "your-" in key.lower():
        raise RuntimeError("CLAUDE_API_KEY missing or placeholder in .env")
    return anthropic.Anthropic(api_key=key)


def streaming_create(client):
    """A create-like callable that streams the response and returns the final Message.
    The SDK refuses a non-streaming request whose max_tokens implies more than 10 minutes
    (24000 tokens does), so every real call goes through client.messages.stream(...) and
    stream.get_final_message(), which returns the same Message object (content, usage with
    output_tokens_details, stop_reason, model)."""
    def create(**kwargs):
        with client.messages.stream(**kwargs) as stream:
            return stream.get_final_message()
    return create


def judge_trace(create, trace_id: str, sents: list[dict], prompt_text: str, inventory,
                replies_dir: Path | None = None, model_key: str = "haiku", thinking_mode: str = "off") -> dict:
    """One trace: the call, the parse, one retry in the same conversation.
    `create` is client.messages.create (or a stub with the same interface)."""
    n = len(sents)
    request = build_request(trace_id, sents, prompt_text, model_key, thinking_mode)
    messages = list(request["messages"])
    fixed = {k: v for k, v in request.items() if k != "messages"}
    usage_total: dict = {}
    replies: list[str] = []
    result = {"trace_id": trace_id, "n": n, "attempts": 0, "valid": False, "labels": None,
              "warnings": [], "retry_message": None, "error": None, "model": None,
              "stop_reasons": [], "usage": {}, "cost_usd": 0.0, "replies": replies,
              "thinking_mode": thinking_mode, "thinking_tokens": 0, "leaks": [], "thinking_chars": []}
    for attempt in (1, 2):
        result["attempts"] = attempt
        response = create(**fixed, messages=messages)
        text = reply_text(response)
        think = thinking_text(response)
        replies.append(text)
        result["leaks"].append("<think>" in text)
        result["thinking_chars"].append(len(think))
        if replies_dir is not None:
            replies_dir.mkdir(parents=True, exist_ok=True)
            (replies_dir / f"{trace_id}_attempt{attempt}.txt").write_text(text, encoding="utf-8")
            if think or thinking_mode != "off":
                (replies_dir / f"{trace_id}_attempt{attempt}_thinking.txt").write_text(think, encoding="utf-8")
        result["model"] = getattr(response, "model", None)
        result["stop_reasons"].append(getattr(response, "stop_reason", None))
        usage_total = add_usage(usage_total, usage_dict(getattr(response, "usage", None)))
        try:
            labels, warnings = J.parse_reply_with_warnings(text, n, inventory)
            result["labels"], result["warnings"], result["valid"] = labels, warnings, True
            break
        except J.ReplyError as err:
            result["error"] = f"{err.kind}: {err.detail} at line {err.line_no}: {err.line}"
            if attempt == 1:
                result["retry_message"] = rejection_message(err, n)
                messages = messages + [{"role": "assistant", "content": text},
                                       {"role": "user", "content": result["retry_message"]}]
    result["usage"] = usage_total
    result["cost_usd"] = cost_usd(usage_total, model_key)
    result["model_key"] = model_key
    result["thinking_tokens"] = usage_total.get("thinking_tokens", 0)
    result["final_stop_reason"] = result["stop_reasons"][-1] if result["stop_reasons"] else None
    return result


# ----------------------------------------------------------------------------
# Records
# ----------------------------------------------------------------------------

def label_dicts(paths: list[str]) -> list[dict]:
    out = []
    for p in paths:
        parts = D.split_path(p)
        out.append({"L1": parts[0], "L2": parts[1] if len(parts) > 1 else None, "L3": parts[2] if len(parts) > 2 else None})
    return out


def path_of(label: dict) -> str:
    return " > ".join(x for x in (label["L1"], label["L2"], label["L3"]) if x)


def label_records(res: dict, run_id: str, prompt_sha: str, timestamp: str, prompt_version: str = "v1") -> list[dict]:
    recs = []
    model_key = res.get("model_key", "haiku")
    for s, paths in enumerate(res["labels"]):
        first = s == 0
        recs.append({
            "trace_id": res["trace_id"], "s": s, "labels": label_dicts(paths), "combined": len(paths) == 2,
            "raw_reply": res["replies"][-1] if first else None,
            "model": res["model"], "model_key": model_key, "prompt_version": prompt_sha, "prompt_file": f"judge_prompt_{prompt_version}.md",
            "temperature": MODELS[model_key]["temperature"],
            "thinking_mode": res.get("thinking_mode", "off"), "thinking_tokens": res.get("thinking_tokens", 0),
            "stop_reason": res.get("final_stop_reason"),
            "run_id": run_id, "timestamp": timestamp,
            "usage": res["usage"] if first else None, "cost_usd": res["cost_usd"] if first else None,
            "attempt": res["attempts"], "valid": res["valid"],
        })
    return recs


# ----------------------------------------------------------------------------
# Agreement
# ----------------------------------------------------------------------------

def truncate(path: str, level: int) -> str:
    return " > ".join(D.split_path(path)[:level])


def kappa(reference: list[str], other: list[str]) -> float:
    n = len(reference)
    if n == 0:
        return float("nan")
    po = sum(1 for a, b in zip(reference, other) if a == b) / n
    cr, co = Counter(reference), Counter(other)
    pe = sum(cr[l] / n * co[l] / n for l in set(cr) | set(co))
    if pe >= 1.0:
        return 1.0 if po >= 1.0 else 0.0
    return (po - pe) / (1 - pe)


def agreement(judge: dict[str, list[list[str]]], reviewed: dict[str, list[list[str]]],
              texts: dict[str, list[str]]) -> dict:
    """judge/reviewed: {trace_id: [[path, ...] per sentence]}.  Returns level summaries,
    per-label rows, residue rows and confusion counts."""
    traces = [t for t in reviewed if t in judge]
    pairs = [(t, s, reviewed[t][s], judge[t][s]) for t in traces for s in range(len(reviewed[t]))]
    levels, per_label, confusions = [], [], {}
    for level in (1, 2, 3):
        rsets = [frozenset(truncate(p, level) for p in r) for _, _, r, _ in pairs]
        jsets = [frozenset(truncate(p, level) for p in j) for _, _, _, j in pairs]
        exact = sum(1 for a, b in zip(rsets, jsets) if a == b) / len(pairs)
        jac = sum(len(a & b) / len(a | b) for a, b in zip(rsets, jsets)) / len(pairs)
        rprim = [truncate(r[0], level) for _, _, r, _ in pairs]
        jprim = [truncate(j[0], level) for _, _, _, j in pairs]
        k = kappa(rprim, jprim)
        levels.append({"level": level, "name": LEVEL_NAMES[level], "n": len(pairs), "exact_match": exact,
                       "mean_jaccard": jac, "kappa": k, "primary_agreement": sum(1 for a, b in zip(rprim, jprim) if a == b) / len(pairs)})
        for label in sorted(set().union(*rsets, *jsets)):
            n_r = sum(1 for a in rsets if label in a)
            n_j = sum(1 for b in jsets if label in b)
            tp = sum(1 for a, b in zip(rsets, jsets) if label in a and label in b)
            prec = tp / n_j if n_j else 0.0
            rec = tp / n_r if n_r else 0.0
            f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
            per_label.append({"level": level, "label": label, "n_reviewed": n_r, "n_judge": n_j, "tp": tp,
                              "precision": prec, "recall": rec, "f1": f1})
        confusions[level] = Counter((a, b) for a, b in zip(rprim, jprim) if a != b).most_common(20)
    residue = [{"trace_id": t, "s": s, "reviewed": " || ".join(r), "judge": " || ".join(j), "text": texts[t][s]}
               for t, s, r, j in pairs if frozenset(r) != frozenset(j)]
    residue.sort(key=lambda x: (x["trace_id"], x["s"]))
    return {"levels": levels, "per_label": per_label, "residue": residue, "confusions": confusions, "n": len(pairs)}


def write_agreement(agr: dict, out_dir: Path, collection: str) -> tuple[Path, Path, Path]:
    a_path = out_dir / f"agreement_{collection}.csv"
    with open(a_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["level", "label", "n_reviewed", "n_judge", "tp", "precision", "recall", "f1", "exact_match", "mean_jaccard", "kappa"])
        for lv in agr["levels"]:
            w.writerow([lv["level"], "(all sentences)", lv["n"], lv["n"], "", "", "", "",
                        f"{lv['exact_match']:.4f}", f"{lv['mean_jaccard']:.4f}", f"{lv['kappa']:.4f}"])
        for r in agr["per_label"]:
            w.writerow([r["level"], r["label"], r["n_reviewed"], r["n_judge"], r["tp"],
                        f"{r['precision']:.4f}", f"{r['recall']:.4f}", f"{r['f1']:.4f}", "", "", ""])
    r_path = out_dir / f"residue_{collection}.csv"
    with open(r_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["trace_id", "s", "reviewed", "judge", "text"])
        w.writeheader()
        w.writerows(agr["residue"])
    c_path = out_dir / f"confusions_{collection}.csv"
    with open(c_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["level", "reviewed", "judge", "count"])
        for level in (1, 2):
            for (a, b), c in agr["confusions"][level]:
                w.writerow([level, a, b, c])
    return a_path, r_path, c_path


# ----------------------------------------------------------------------------
# The run
# ----------------------------------------------------------------------------

def run_judge(sentences_path: Path, out_dir: Path, traces: list[str] | None = None, dry_run: bool = False,
              client=None, reviewed_path: Path | None = None, run_id: str | None = None, log=print,
              model_key: str = "haiku", prompt_version: str = "v1", thinking_mode: str = "off") -> dict:
    """The whole step for one collection.  Returns a summary dict (per trace results, paths)."""
    if model_key not in MODELS:
        raise ValueError(f"unknown model {model_key!r}; known: {tuple(MODELS)}")
    tparams = thinking_params(model_key, thinking_mode)
    sentences_path, out_dir = Path(sentences_path), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    collection = collection_name(sentences_path)
    run_id = run_id or out_dir.name
    prompt_file, labels_file = prompt_files(prompt_version)
    prompt_text = prompt_file.read_text(encoding="utf-8")
    prompt_sha = sha256_of_file(prompt_file)
    inventory = J.Inventory.load(labels_file)
    model = MODELS[model_key]
    all_sents = load_sentences(sentences_path)
    order = traces or list(all_sents)
    missing = [t for t in order if t not in all_sents]
    if missing:
        raise ValueError(f"traces not in the sentences file: {missing}")
    summary = {"collection": collection, "run_id": run_id, "out_dir": str(out_dir), "traces": {}, "stopped": None,
               "total_cost_usd": 0.0, "dry_run": dry_run, "model_key": model_key, "model_id": model["id"],
               "prompt_version": prompt_version, "thinking_mode": thinking_mode}
    # dry run: build and write every request
    req_dir = out_dir / "requests"
    req_dir.mkdir(exist_ok=True)
    for tid in order:
        req = build_request(tid, all_sents[tid], prompt_text, model_key, thinking_mode)
        (req_dir / f"{tid}.json").write_text(json.dumps(req, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        est = estimate_input_tokens(req)
        summary["traces"][tid] = {"n": len(all_sents[tid]), "estimated_input_tokens": est}
        log(f"request {tid}: {len(all_sents[tid])} sentences, about {est} input tokens (characters/4)")
    import anthropic
    import requests as requests_lib
    import pytest
    config = {
        "run_id": run_id, "collection": collection, "mode": "dry-run" if dry_run else "ordinary",
        "model_key": model_key, "model": model["id"], "model_echoed": {}, "max_tokens": MAX_TOKENS_THINKING if tparams else MAX_TOKENS,
        "temperature": model["temperature"],
        "temperature_via": "extra_body" if model["temperature"] is not None else "not sent (the model rejects sampling parameters)",
        "thinking_mode": thinking_mode,
        "thinking_params": tparams if tparams else (model["thinking"] if model["thinking"] is not None else "omitted (the model runs without thinking by default)"),
        "reply_instruction": REPLY_INSTRUCTION if thinking_mode == "none" else None,
        "thinking_tokens": {}, "final_stop_reason": {},
        "prompt_version": prompt_version, "prompt": prompt_file.name, "prompt_sha256": prompt_sha,
        "inventory": labels_file.name, "inventory_sha256": sha256_of_file(labels_file),
        "sentences": str(sentences_path), "sentences_sha256": sha256_of_file(sentences_path),
        "traces": order, "git_commit": git_head(), "python": sys.version.split()[0],
        "anthropic": anthropic.__version__, "requests": requests_lib.__version__, "pytest": pytest.__version__,
        "prices_usd_per_million": model["prices"], "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

    def write_config():
        (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    write_config()
    if dry_run:
        return summary
    if client is None:
        client = make_client()
    labels_path = out_dir / f"labels_{collection}_judge.jsonl"
    blocks_path = out_dir / f"blocks_{collection}_judge.jsonl"
    log_path = out_dir / "_log.txt"
    judge_labels: dict[str, list[list[str]]] = {}
    with open(labels_path, "w", encoding="utf-8", newline="\n") as lf, open(blocks_path, "w", encoding="utf-8", newline="\n") as bf, \
            open(log_path, "a", encoding="utf-8", newline="\n") as lg:
        lg.write(f"# s1_judge run_id={run_id} model={model['id']} ({model_key}) prompt={prompt_version} thinking={thinking_mode} {config['timestamp']}\n")
        lg.write("# trace_id\tattempts\tvalid\tinput\tcache_read\tcache_write\toutput\tcost_usd\tstop_reasons\tthinking_tokens\tleaks\n")
        for tid in order:
            timestamp = datetime.now().isoformat(timespec="seconds")
            res = judge_trace(streaming_create(client), tid, all_sents[tid], prompt_text, inventory, out_dir / "replies",
                              model_key, thinking_mode)
            config["model_echoed"][tid] = res["model"]
            config["thinking_tokens"][tid] = res["thinking_tokens"]
            config["final_stop_reason"][tid] = res["final_stop_reason"]
            write_config()
            u = res["usage"]
            lg.write(f"{tid}\t{res['attempts']}\t{res['valid']}\t{u.get('input_tokens', 0)}\t{u.get('cache_read_input_tokens', 0)}\t"
                     f"{u.get('cache_creation_input_tokens', 0)}\t{u.get('output_tokens', 0)}\t{res['cost_usd']:.6f}\t{res['stop_reasons']}\t"
                     f"{res['thinking_tokens']}\t{res['leaks']}\n")
            lg.flush()
            summary["total_cost_usd"] += res["cost_usd"]
            t = summary["traces"][tid]
            t.update({"attempts": res["attempts"], "valid": res["valid"], "usage": u, "cost_usd": res["cost_usd"],
                      "model": res["model"], "stop_reasons": res["stop_reasons"], "retry_message": res["retry_message"],
                      "error": res["error"], "warnings": res["warnings"], "thinking_tokens": res["thinking_tokens"],
                      "leaks": res["leaks"], "final_stop_reason": res["final_stop_reason"], "thinking_chars": res["thinking_chars"]})
            log(f"{tid}: attempts {res['attempts']}, valid {res['valid']}, usage {u}, cost ${res['cost_usd']:.6f}")
            if not res["valid"]:
                summary["stopped"] = f"{tid}: {res['error']}"
                lg.write(f"# STOP: {tid} failed after {res['attempts']} attempts: {res['error']}\n")
                log(f"STOP: {tid} failed after {res['attempts']} attempts: {res['error']}")
                break
            for rec in label_records(res, run_id, prompt_sha, timestamp, prompt_version):
                lf.write(json.dumps(rec, ensure_ascii=False) + "\n")
            judge_labels[tid] = res["labels"]
            der = D.derive(res["labels"], tid, "judge")
            t.update({"nodes": len(der["nodes"]), "blocks": len(der["blocks"])})
            bf.write(json.dumps({k: der[k] for k in ("trace_id", "label_source", "nodes", "blocks")}, ensure_ascii=False) + "\n")
    summary["labels_path"], summary["blocks_path"] = str(labels_path), str(blocks_path)
    if reviewed_path is not None and judge_labels:
        listing = D.parse_listing(reviewed_path)
        reviewed = {t: listing[t]["labels"] for t in listing if t in judge_labels}
        texts = {t: listing[t]["texts"] for t in reviewed}
        agr = agreement(judge_labels, reviewed, texts)
        a, r, c = write_agreement(agr, out_dir, collection)
        summary["agreement"] = agr
        summary["agreement_paths"] = [str(a), str(r), str(c)]
    return summary


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Pipeline step (4/9): the judge on a collection.")
    ap.add_argument("--sentences", required=True)
    ap.add_argument("--mode", choices=["ordinary", "batch"], default="ordinary")
    ap.add_argument("--out", help="run folder (default runs/experiments/judge_<collection>_<model>_<version>_<date>_<hhmm>)")
    ap.add_argument("--trace", action="append", help="run this trace only (repeatable)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--reviewed", help="the reviewed listing; writes the agreement and residue files")
    ap.add_argument("--model", choices=tuple(MODELS), default="haiku")
    ap.add_argument("--prompt-version", choices=PROMPT_VERSIONS, default="v1")
    ap.add_argument("--thinking", choices=THINKING_MODES, default="off",
                    help="off (default): current behaviour; none: thinking disabled plus the labels-only closing line; "
                         "low/medium: adaptive thinking at that effort (Sonnet 5 only)")
    args = ap.parse_args(argv)
    if args.mode == "batch":
        raise NotImplementedError("batch mode is pipeline step (5/9) (sweep44, archived500, the new continuations); "
                                  "not implemented in step (4/9), use --mode ordinary")
    collection = collection_name(Path(args.sentences))
    tag = f"_think{args.thinking}" if args.thinking != "off" else ""
    out_dir = Path(args.out) if args.out else REPO / "runs" / "experiments" / f"judge_{collection}_{args.model}_{args.prompt_version}{tag}_{datetime.now():%Y-%m-%d_%H%M}"
    prompt_file, _ = prompt_files(args.prompt_version)
    print(f"s1_judge: sentences={args.sentences} out={out_dir} model={MODELS[args.model]['id']} ({args.model}) "
          f"thinking={args.thinking} max_tokens={MAX_TOKENS_THINKING if args.thinking != 'off' else MAX_TOKENS} "
          f"temperature={MODELS[args.model]['temperature']} prompt={prompt_file.name} sha256={sha256_of_file(prompt_file)[:12]} dry_run={args.dry_run} git={git_head()}")
    summary = run_judge(Path(args.sentences), out_dir, args.trace, args.dry_run,
                        reviewed_path=Path(args.reviewed) if args.reviewed else None,
                        model_key=args.model, prompt_version=args.prompt_version, thinking_mode=args.thinking)
    print(json.dumps({k: v for k, v in summary.items() if k != "agreement"}, indent=2, default=str))
    return 0 if not summary["stopped"] else 1


if __name__ == "__main__":
    sys.exit(main())
