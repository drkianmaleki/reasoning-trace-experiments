#!/usr/bin/env python3
"""s1_judge.py -- pipeline steps (4/9) and (5/9): the judge on a collection of sentence files.

Ordinary mode (step 4/9): one streamed call per trace, the reply in the run-length code format
of prompts/judge_prompt_v<K>.md, parsed by judge_codec, one retry, then the derivation (rule R4
applied to the sentence texts, pipeline v2 decision 20).

  python scripts/s1_judge.py --sentences runs/tests/t2_split_2026-09-16_2224/sentences_source.jsonl \
      --mode ordinary --model sonnet --prompt-version v3 --thinking low \
      --out runs/experiments/judge_source_<date>_<hhmm>/ [--trace e036] [--dry-run] [--reviewed <listing>]

Batch mode (step 5/9; pipeline v2 decisions 12, 14, 19, 20; Section 9 item 7): the same
per-trace request, all traces of the collection submitted as one Message Batch
(client.messages.batches.create, one entry per trace, custom_id = the trace id made safe),
polled every 60 seconds until processing_status == "ended" (request_counts printed each time;
after 3 hours the batch id is saved to batch_state.json and the run stops, resumable with
--resume-batch <id>), results streamed and parsed (thinking blocks stored under replies/,
text blocks parsed), one follow-up batch for the failures (errored, expired, canceled or a
parse error) with the retry message as in ordinary mode, anything still failing logged as
failed.  Costs at batch prices (half of the ordinary ones).

  python scripts/s1_judge.py --collection sweep44 --sentences <sentences_sweep44.jsonl> \
      --model sonnet --prompt-version v3 --thinking low --mode batch --out runs/experiments/judge_sweep44_<stamp>/

Continuation collections (archived500; step 8/9 later): every trace id found in the archived
continuation file (--archived) is judged as a continuation of its cut: the user message shows
"Prefix, already labeled (do not relabel):" with the source sentences of old_s <= cut and their
reviewed label codes (labels_source_reviewed_v4.jsonl, exported from listing v4 into the run
folder), then "Continuation to label:" with the continuation's sentences c0 ... c<N-1>; the
reply's indices refer to the continuation.  The derivation runs on prefix plus continuation.

Outputs in the run folder: labels_<collection>_judge.jsonl, blocks_<collection>_judge.jsonl,
traces_<collection>_judge.jsonl (one record per trace: attempts, usage, cost, failure), replies/,
requests/, config.json, _log.txt, summary.md; batch mode adds custom_ids.json and
batch_state.json; with --reviewed: agreement_, residue_, confusions_<collection>.csv; whole-trace
collections: pcorpus_L1.csv (+ _rownorm); continuation collections: pnext_archived.csv,
psource_c004.csv, psource_e036.csv.  Keys are read from .env (CLAUDE_API_KEY) and never
printed, logged or written.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import derivation as D  # noqa: E402
import judge_codec as J  # noqa: E402
import transitions as T  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
PROMPT_FILE = REPO / "prompts" / "judge_prompt_v1.md"
LABELS_FILE = REPO / "prompts" / "labels_v1.json"
ENV_FILE = REPO / ".env"
ARCHIVED_CONTINUATIONS = REPO / "archive" / "decided-mid-thought" / "runs" / "resample_cuts_2026-08-25_1503.jsonl"
SENTENCES_SOURCE = D.SENTENCES_SOURCE
REVIEWED_SOURCE = "reviewed_v4"
MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 8000
TEMPERATURE = 0
PRICES = {"input": 1.0, "output": 5.0, "cache_read": 0.10, "cache_write": 1.25}  # USD per million tokens
LEVEL_NAMES = {1: "Level 1", 2: "Level 1 > Level 2", 3: "full path"}
PROMPT_VERSIONS = ("v1", "v2", "v3")
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
# Batch prices: half of the ordinary ones (Sonnet 5: input $1, output $5, cache read $0.10, cache
# write $1.25 per million; thinking billed as output).
BATCH_PRICES = {k: {kk: vv / 2 for kk, vv in m["prices"].items()} for k, m in MODELS.items()}


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
# Long documents (2026-09-17): the measured output rate of Sonnet 5 x thinking low is about 30
# tokens per sentence (20-26 thinking, 4-7 label tokens), so a 24,000-token cap truncates the
# reply of a document beyond about 800 sentences; 63 archived continuations exceed 1,000
# sentences.  Documents over LONG_DOCUMENT_SENTENCES get twice the cap; a retry after a
# max_tokens stop doubles the cap once more (up to MAX_TOKENS_CAP).  The cap is a ceiling, not a
# budget: adaptive thinking at low effort does not think more because the ceiling is higher.
LONG_DOCUMENT_SENTENCES = 600
MAX_TOKENS_THINKING_LONG = 48000
MAX_TOKENS_CAP = 96000
# "none" (Kian, 2026-09-17): thinking disabled as in "off" AND the user message ends with this
# extra line, recorded in config.json as reply_instruction.
REPLY_INSTRUCTION = ("Reply with the run-length labels only: no reasoning, no commentary, no tags of any kind, "
                     "nothing before the first run line.")
BATCH_POLL_SECONDS = 60
BATCH_MAX_WAIT_SECONDS = 3 * 3600
CUSTOM_ID_RE = re.compile(r"[^A-Za-z0-9_-]")
# --retry-failed (Kian, 2026-09-17): the documents still failed after the follow-up batch are
# resubmitted once more, fresh, with this line at the end of the user message.
FORMAT_CHECK = ("Format check before you answer: every index from 0 to N−1 exactly once, runs in increasing order, "
                "one code per run (two codes joined by + only on a single-index line), codes only from the table.")


def thinking_params(model_key: str, mode: str) -> dict:
    if mode not in THINKING_MODES:
        raise ValueError(f"unknown thinking mode {mode!r}; known: {THINKING_MODES}")
    if mode in ("off", "none"):
        return {}
    if model_key != "sonnet":
        raise ValueError("thinking modes low/medium are implemented for Sonnet 5 only (adaptive thinking)")
    return {"thinking": {"type": "adaptive", "display": "summarized"}, "output_config": {"effort": mode}}


def max_tokens_for(n_sentences: int, model_key: str, thinking_mode: str) -> int:
    if not thinking_params(model_key, thinking_mode):
        return MAX_TOKENS
    return MAX_TOKENS_THINKING if n_sentences <= LONG_DOCUMENT_SENTENCES else MAX_TOKENS_THINKING_LONG


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


def load_archived_meta(path: Path | str = ARCHIVED_CONTINUATIONS) -> dict[str, dict]:
    """{continuation id: {prefix_id, trace_arm, cut, seq}} from the archived continuation file
    (pipeline v2, Section 3 item 2); the text is not read."""
    out: dict[str, dict] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                out[r["id"]] = {"prefix_id": r["prefix_id"], "trace_arm": r["trace_arm"], "cut": int(r["cut"]), "seq": r.get("seq")}
    return out


def export_reviewed_labels(out_path: Path, listing_path: Path | str = D.LISTING, sentences_source: Path | str = SENTENCES_SOURCE,
                           inventory=None, source: str = REVIEWED_SOURCE) -> dict[str, list[dict]]:
    """labels_source_reviewed_v4.jsonl (pipeline v2, step 1b/9): one record per source sentence
    with the reviewed labels, old_s and part; every path checked against the inventory."""
    listing = D.parse_listing(listing_path)
    sents = load_sentences(Path(sentences_source))
    out: dict[str, list[dict]] = {}
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        for tid in ("c004", "e036"):
            if len(listing[tid]["labels"]) != len(sents[tid]):
                raise ValueError(f"{tid}: {len(listing[tid]['labels'])} listing rows vs {len(sents[tid])} sentences")
            for s, paths in enumerate(listing[tid]["labels"]):
                if inventory is not None:
                    for p in paths:
                        if p not in inventory.path_to_code:
                            raise ValueError(f"{tid} s{s}: reviewed path not in the inventory: {p!r}")
                r = sents[tid][s]
                if r.get("old_s") != listing[tid]["old_s"][s]:
                    raise ValueError(f"{tid} s{s}: old_s {r.get('old_s')} in the sentence file vs {listing[tid]['old_s'][s]} in the listing")
                rec = {"trace_id": tid, "s": s, "old_s": r.get("old_s"), "part": r.get("part"), "labels": label_dicts(paths),
                       "combined": len(paths) == 2, "source": source}
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                out.setdefault(tid, []).append(rec)
    return out


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


def continuation_message(trace_id: str, prefix: list[tuple[str, str]], cont: list[dict], extra_line: str | None = None) -> str:
    """The two-part user message of a continuation (pipeline v2, step 8b/9): (i) the prefix
    sentences with their reviewed label codes after a tab, (ii) the continuation's sentences
    c0 ... c<N-1>; the reply's indices refer to the continuation, 0 to N-1.  An empty prefix
    (cut 0) omits part (i)."""
    n = len(cont)
    if prefix:
        lines = [f"Continuation {trace_id}: a prefix of {len(prefix)} sentences already labeled (shown for context, with its label code after a tab), "
                 f"then {n} continuation sentences c0 to c{n - 1}. Label only the continuation sentences; your indices 0 to {n - 1} refer to c0 to c{n - 1}."]
        lines.append("Prefix, already labeled (do not relabel):")
        lines += [f"s{i}: {text}\t{code}" for i, (text, code) in enumerate(prefix)]
    else:
        lines = [f"Continuation {trace_id} from an empty prefix: {n} sentences c0 to c{n - 1}. Label every sentence; your indices 0 to {n - 1} refer to c0 to c{n - 1}."]
    lines.append("Continuation to label:")
    lines += [f"c{r['s']}: {r['text']}" for r in cont]
    lines.append(f"Output the run-length labels for c0 to c{n - 1} now (indices 0 to {n - 1}), nothing else.")
    if extra_line:
        lines.append(extra_line)
    return "\n".join(lines)


def build_request(trace_id: str, sents: list[dict], prompt_text: str, model_key: str = "haiku",
                  thinking_mode: str = "off", message: str | None = None) -> dict:
    m = MODELS[model_key]
    tp = thinking_params(model_key, thinking_mode)
    extra = REPLY_INSTRUCTION if thinking_mode == "none" else None
    req = {
        "model": m["id"],
        "max_tokens": max_tokens_for(len(sents), model_key, thinking_mode),
        "system": [{"type": "text", "text": prompt_text, "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": message if message is not None else user_message(trace_id, sents, extra)}],
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


def label_code(paths: list[str], inventory) -> str:
    return "+".join(inventory.path_to_code[p] for p in paths)


def safe_custom_id(trace_id: str, taken: set[str] | None = None) -> str:
    """The trace id made safe for the batch API: letters, digits, '_' and '-' only, at most 64
    characters, unique among `taken`."""
    base = CUSTOM_ID_RE.sub("_", trace_id)[:64] or "trace"
    cid = base
    k = 1
    while taken is not None and cid in taken:
        suffix = f"_{k}"
        cid = base[:64 - len(suffix)] + suffix
        k += 1
    if taken is not None:
        taken.add(cid)
    return cid


def batch_params(request: dict) -> dict:
    """The Messages params of a batch entry: the ordinary request with extra_body flattened."""
    params = {k: v for k, v in request.items() if k != "extra_body"}
    params.update(request.get("extra_body", {}))
    return params


# ----------------------------------------------------------------------------
# Documents: a whole trace, or a continuation with its labeled prefix
# ----------------------------------------------------------------------------

def make_documents(all_sents: dict[str, list[dict]], order: list[str], cont_meta: dict[str, dict] | None = None,
                   reviewed: dict[str, list[dict]] | None = None, source_texts: dict[str, list[str]] | None = None,
                   inventory=None) -> list[dict]:
    docs = []
    for tid in order:
        sents = all_sents[tid]
        doc = {"trace_id": tid, "n": len(sents), "sents": sents, "texts": [r["text"] for r in sents], "continuation": False,
               "meta": None, "prefix_labels": [], "prefix_texts": [], "prefix_codes": [], "prefix_s": []}
        if cont_meta is not None and tid in cont_meta:
            m = cont_meta[tid]
            doc["continuation"] = True
            doc["meta"] = m
            if m["trace_arm"] != "shared":
                if reviewed is None or source_texts is None or inventory is None:
                    raise ValueError("continuation documents need the reviewed labels, the source texts and the inventory")
                recs = [r for r in reviewed[m["trace_arm"]] if r["old_s"] <= m["cut"]]
                doc["prefix_labels"] = [[path_of(l) for l in r["labels"]] for r in recs]
                doc["prefix_texts"] = [source_texts[m["trace_arm"]][r["s"]] for r in recs]
                doc["prefix_codes"] = [label_code(paths, inventory) for paths in doc["prefix_labels"]]
                doc["prefix_s"] = [r["s"] for r in recs]
        docs.append(doc)
    return docs


def document_request(doc: dict, prompt_text: str, model_key: str, thinking_mode: str) -> dict:
    message = None
    if doc["continuation"]:
        extra = REPLY_INSTRUCTION if thinking_mode == "none" else None
        message = continuation_message(doc["trace_id"], list(zip(doc["prefix_texts"], doc["prefix_codes"])), doc["sents"], extra)
    return build_request(doc["trace_id"], doc["sents"], prompt_text, model_key, thinking_mode, message)


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


def cost_usd(usage: dict, model_key: str = "haiku", batch: bool = False) -> float:
    prices = BATCH_PRICES[model_key] if batch else MODELS[model_key]["prices"]
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


def store_reply(replies_dir: Path | None, trace_id: str, attempt: int, text: str, think: str, thinking_mode: str) -> None:
    if replies_dir is None:
        return
    replies_dir.mkdir(parents=True, exist_ok=True)
    (replies_dir / f"{trace_id}_attempt{attempt}.txt").write_text(text, encoding="utf-8")
    if think or thinking_mode != "off":
        (replies_dir / f"{trace_id}_attempt{attempt}_thinking.txt").write_text(think, encoding="utf-8")


def judge_trace(create, trace_id: str, sents: list[dict], prompt_text: str, inventory,
                replies_dir: Path | None = None, model_key: str = "haiku", thinking_mode: str = "off",
                request: dict | None = None) -> dict:
    """One trace: the call, the parse, one retry in the same conversation (after a max_tokens
    stop the retry doubles the cap).  `create` is client.messages.create (or a stub with the
    same interface); `request` a prebuilt request (a continuation document)."""
    n = len(sents)
    request = request or build_request(trace_id, sents, prompt_text, model_key, thinking_mode)
    messages = list(request["messages"])
    fixed = {k: v for k, v in request.items() if k != "messages"}
    usage_total: dict = {}
    replies: list[str] = []
    result = {"trace_id": trace_id, "n": n, "attempts": 0, "valid": False, "labels": None,
              "warnings": [], "retry_message": None, "error": None, "model": None,
              "stop_reasons": [], "usage": {}, "cost_usd": 0.0, "replies": replies,
              "thinking_mode": thinking_mode, "thinking_tokens": 0, "leaks": [], "thinking_chars": [],
              "max_tokens": [], "batch_ids": [], "custom_id": None}
    for attempt in (1, 2):
        result["attempts"] = attempt
        result["max_tokens"].append(fixed["max_tokens"])
        response = create(**fixed, messages=messages)
        text = reply_text(response)
        think = thinking_text(response)
        replies.append(text)
        result["leaks"].append("<think>" in text)
        result["thinking_chars"].append(len(think))
        store_reply(replies_dir, trace_id, attempt, text, think, thinking_mode)
        result["model"] = getattr(response, "model", None)
        stop = getattr(response, "stop_reason", None)
        result["stop_reasons"].append(stop)
        usage_total = add_usage(usage_total, usage_dict(getattr(response, "usage", None)))
        try:
            labels, warnings = J.parse_reply_with_warnings(text, n, inventory)
            result["labels"], result["warnings"], result["valid"] = labels, warnings, True
            break
        except J.ReplyError as err:
            result["error"] = f"{err.kind}: {err.detail} at line {err.line_no}: {err.line}"
            if attempt == 1:
                result["retry_message"] = rejection_message(err, n)
                if text.strip():
                    messages = messages + [{"role": "assistant", "content": text},
                                           {"role": "user", "content": result["retry_message"]}]
                if stop == "max_tokens" or not text.strip():
                    fixed["max_tokens"] = min(2 * fixed["max_tokens"], MAX_TOKENS_CAP)
    result["usage"] = usage_total
    result["cost_usd"] = cost_usd(usage_total, model_key)
    result["model_key"] = model_key
    result["thinking_tokens"] = usage_total.get("thinking_tokens", 0)
    result["final_stop_reason"] = result["stop_reasons"][-1] if result["stop_reasons"] else None
    return result


# ----------------------------------------------------------------------------
# Batch mode
# ----------------------------------------------------------------------------

def request_counts_dict(batch) -> dict:
    rc = getattr(batch, "request_counts", None)
    return {k: int(getattr(rc, k, 0) or 0) for k in ("processing", "succeeded", "errored", "canceled", "expired")}


def submit_batch(client, entries: list[dict]):
    """entries: [{"custom_id", "params"}].  Returns the MessageBatch object."""
    return client.messages.batches.create(requests=entries)


def poll_batch(client, batch_id: str, log=print, poll_seconds: int = BATCH_POLL_SECONDS,
               max_wait_seconds: int = BATCH_MAX_WAIT_SECONDS, sleep=time.sleep):
    """Poll until processing_status == "ended"; returns the final batch object, or None when the
    wait exceeds max_wait_seconds."""
    start = time.monotonic()
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        elapsed = time.monotonic() - start
        rc = request_counts_dict(batch)
        log(f"batch {batch_id}: {batch.processing_status}; request_counts {json.dumps(rc)}; elapsed {elapsed:.0f}s")
        if batch.processing_status == "ended":
            return batch
        if elapsed >= max_wait_seconds:
            return None
        sleep(poll_seconds)


def fetch_results(client, batch_id: str) -> dict[str, object]:
    """{custom_id: result} streamed from the batch (results arrive in any order)."""
    out = {}
    for r in client.messages.batches.results(batch_id):
        out[r.custom_id] = r.result
    return out


def error_summary(result) -> str:
    err = getattr(result, "error", None)
    if err is None:
        return ""
    inner = getattr(err, "error", None)
    if inner is not None:
        return f"{getattr(inner, 'type', '')}: {getattr(inner, 'message', '')}"[:500]
    return str(err)[:500]


def classify_result(result, n: int, inventory, model_key: str) -> dict:
    """One batch result -> what the ordinary path would have recorded for one attempt."""
    out = {"type": getattr(result, "type", None), "ok": False, "text": None, "thinking": None, "usage": {}, "stop_reason": None,
           "model": None, "labels": None, "warnings": [], "error": None, "error_kind": None, "cost_usd": 0.0, "leak": False}
    if out["type"] == "succeeded":
        msg = result.message
        out["text"] = reply_text(msg)
        out["thinking"] = thinking_text(msg)
        out["usage"] = usage_dict(getattr(msg, "usage", None))
        out["cost_usd"] = cost_usd(out["usage"], model_key, batch=True)
        out["stop_reason"] = getattr(msg, "stop_reason", None)
        out["model"] = getattr(msg, "model", None)
        out["leak"] = "<think>" in out["text"]
        try:
            out["labels"], out["warnings"] = J.parse_reply_with_warnings(out["text"], n, inventory)
            out["ok"] = True
        except J.ReplyError as err:
            out["error_kind"] = err.kind
            out["error"] = f"{err.kind}: {err.detail} at line {err.line_no}: {err.line}"
            out["retry_message"] = rejection_message(err, n)
    else:
        out["error_kind"] = out["type"] or "unknown"
        out["error"] = f"{out['type']}: {error_summary(result)}"
    return out


def follow_up_request(request: dict, first: dict) -> dict:
    """The attempt-2 request of a failed batch entry: after a parse error the conversation
    continues with the reply and the retry message (the cap doubled after a max_tokens stop);
    after an API-level failure the same request is resubmitted.  An empty reply (the cap was
    exhausted inside the thinking; the API rejects an empty assistant turn) is resubmitted fresh
    with the cap doubled."""
    req = {k: v for k, v in request.items()}
    text = first.get("text")
    if text is not None and not text.strip():
        req["max_tokens"] = min(2 * request["max_tokens"], MAX_TOKENS_CAP)
        return req
    if text is not None and first.get("retry_message"):
        req["messages"] = list(request["messages"]) + [{"role": "assistant", "content": text},
                                                       {"role": "user", "content": first["retry_message"]}]
        if first.get("stop_reason") == "max_tokens":
            req["max_tokens"] = min(2 * request["max_tokens"], MAX_TOKENS_CAP)
    return req


def judge_batch(client, docs: list[dict], requests: dict[str, dict], cid_of: dict[str, str], out_dir: Path, inventory,
                model_key: str, thinking_mode: str, log=print, resume_batch: str | None = None,
                poll_seconds: int = BATCH_POLL_SECONDS, max_wait_seconds: int = BATCH_MAX_WAIT_SECONDS,
                sleep=time.sleep, first_attempt: int = 1, n_attempts: int = 2, state_name: str = "batch_state.json") -> dict:
    """Submit (or resume), poll, download, parse, one follow-up batch (n_attempts = 2; a single
    batch with n_attempts = 1).  Attempts are numbered from first_attempt (replies/<trace>_attempt<k>).
    Returns {"results": {trace_id: result-dict as judge_trace}, "batches": [...], "stopped": None | str}."""
    state_path = out_dir / state_name
    last_attempt = first_attempt + n_attempts - 1
    tid_of = {cid: tid for tid, cid in cid_of.items()}
    docs_by_tid = {d["trace_id"]: d for d in docs}
    state = {"collection": None, "batches": [], "custom_ids": tid_of, "status": "in_progress",
             "started": datetime.now().isoformat(timespec="seconds")}

    def save_state():
        state_path.write_text(json.dumps(state, indent=1) + "\n", encoding="utf-8")

    per: dict[str, dict] = {}
    for tid, d in docs_by_tid.items():
        per[tid] = {"trace_id": tid, "n": d["n"], "attempts": 0, "valid": False, "labels": None, "warnings": [],
                    "retry_message": None, "error": None, "model": None, "stop_reasons": [], "usage": {}, "cost_usd": 0.0,
                    "replies": [], "thinking_mode": thinking_mode, "thinking_tokens": 0, "leaks": [], "thinking_chars": [],
                    "max_tokens": [], "batch_ids": [], "custom_id": cid_of[tid], "model_key": model_key, "error_kinds": []}
    pending = {cid: requests[cid] for cid in requests}
    first_outcomes: dict[str, dict] = {}
    stopped = None
    for attempt in range(first_attempt, last_attempt + 1):
        if not pending:
            break
        entries = [{"custom_id": cid, "params": batch_params(req)} for cid, req in pending.items()]
        if attempt == first_attempt and resume_batch:
            batch_id = resume_batch
            log(f"resuming batch {batch_id} with {len(entries)} entries")
        else:
            submitted = submit_batch(client, entries)
            batch_id = submitted.id
            log(f"submitted batch {batch_id} (attempt {attempt}, {len(entries)} entries); status {submitted.processing_status}; "
                f"request_counts {json.dumps(request_counts_dict(submitted))}")
        binfo = {"batch_id": batch_id, "attempt": attempt, "n_entries": len(entries), "custom_ids": sorted(pending),
                 "submitted": datetime.now().isoformat(timespec="seconds"), "ended": None, "request_counts": None, "poll_seconds": poll_seconds}
        state["batches"].append(binfo)
        save_state()
        for cid in pending:
            per[tid_of[cid]]["batch_ids"].append(batch_id)
            per[tid_of[cid]]["max_tokens"].append(pending[cid]["max_tokens"])
        batch = poll_batch(client, batch_id, log, poll_seconds, max_wait_seconds, sleep)
        if batch is None:
            stopped = f"batch {batch_id} not ended after {max_wait_seconds} s; resume with --resume-batch {batch_id}"
            state["status"] = "timeout"
            save_state()
            log("STOP: " + stopped)
            break
        binfo["ended"] = datetime.now().isoformat(timespec="seconds")
        binfo["request_counts"] = request_counts_dict(batch)
        binfo["api_created_at"] = str(getattr(batch, "created_at", ""))
        binfo["api_ended_at"] = str(getattr(batch, "ended_at", ""))
        save_state()
        results = fetch_results(client, batch_id)
        missing = [cid for cid in pending if cid not in results]
        if missing:
            log(f"batch {batch_id}: {len(missing)} entries without a result (treated as errored)")
        next_pending: dict[str, dict] = {}
        for cid, req in pending.items():
            tid = tid_of[cid]
            r = per[tid]
            r["attempts"] = attempt
            n = docs_by_tid[tid]["n"]
            if cid in results:
                oc = classify_result(results[cid], n, inventory, model_key)
            else:
                oc = {"type": "missing", "ok": False, "text": None, "thinking": None, "usage": {}, "stop_reason": None, "model": None,
                      "labels": None, "warnings": [], "error": "missing: no result for this custom_id", "error_kind": "missing", "cost_usd": 0.0, "leak": False}
            if oc["text"] is not None:
                r["replies"].append(oc["text"])
                store_reply(out_dir / "replies", tid, attempt, oc["text"], oc["thinking"] or "", thinking_mode)
                r["leaks"].append(oc["leak"])
                r["thinking_chars"].append(len(oc["thinking"] or ""))
            r["stop_reasons"].append(oc["stop_reason"])
            r["model"] = oc["model"] or r["model"]
            r["usage"] = add_usage(r["usage"], oc["usage"])
            r["cost_usd"] += oc["cost_usd"]
            if oc["ok"]:
                r["labels"], r["warnings"], r["valid"], r["error"] = oc["labels"], oc["warnings"], True, None
            else:
                r["error"] = oc["error"]
                r["error_kinds"].append(oc["error_kind"])
                if attempt < last_attempt:
                    r["retry_message"] = oc.get("retry_message")
                    first_outcomes[cid] = oc
                    next_pending[cid] = follow_up_request(req, oc)
        n_ok = sum(1 for cid in pending if per[tid_of[cid]]["valid"])
        log(f"batch {batch_id} (attempt {attempt}): {n_ok} of {len(pending)} parsed; failures {len(pending) - n_ok}: "
            + json.dumps(Counter(per[tid_of[cid]]['error_kinds'][-1] for cid in pending if not per[tid_of[cid]]['valid'])))
        pending = next_pending
    for r in per.values():
        r["thinking_tokens"] = r["usage"].get("thinking_tokens", 0)
        r["final_stop_reason"] = r["stop_reasons"][-1] if r["stop_reasons"] else None
    if stopped is None:
        state["status"] = "ended"
        state["ended"] = datetime.now().isoformat(timespec="seconds")
        save_state()
    return {"results": per, "batches": state["batches"], "stopped": stopped}


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


def label_records(res: dict, run_id: str, prompt_sha: str, timestamp: str, prompt_version: str = "v1",
                  extra: dict | None = None, lean: bool = False) -> list[dict]:
    """One record per sentence.  res["labels"] are the R4-enforced labels when res carries
    "r4_notes" (from finalize_document); `extra` fields (continuation meta) go on every record.
    lean=True (batch mode, large collections): the run-constant fields, raw_reply, usage and
    model sit on the s = 0 record only; every record still carries batch_id, custom_id, attempt,
    stop_reason, thinking_tokens and cost_usd."""
    recs = []
    model_key = res.get("model_key", "haiku")
    notes = res.get("r4_notes") or [None] * len(res["labels"])
    batch_id = res.get("batch_ids", [None])[-1] if res.get("batch_ids") else None
    for s, paths in enumerate(res["labels"]):
        first = s == 0
        rec = {"trace_id": res["trace_id"], "s": s, "labels": label_dicts(paths), "combined": len(paths) == 2,
               "r4_applied": bool(notes[s])}
        if notes[s] and notes[s]["changed"]:
            rec["labels_before_r4"] = label_dicts(notes[s]["before"])
        head = {"raw_reply": res["replies"][-1] if res.get("replies") else None,
                "model": res["model"], "model_key": model_key, "prompt_version": prompt_sha, "prompt_file": f"judge_prompt_{prompt_version}.md",
                "temperature": MODELS[model_key]["temperature"], "thinking_mode": res.get("thinking_mode", "off"),
                "run_id": run_id, "timestamp": timestamp, "usage": res["usage"], "max_tokens": res.get("max_tokens")}
        tail = {"thinking_tokens": res.get("thinking_tokens", 0), "stop_reason": res.get("final_stop_reason"),
                "cost_usd": res["cost_usd"], "attempt": res["attempts"], "valid": res["valid"],
                "batch_id": batch_id, "custom_id": res.get("custom_id")}
        if lean:
            if first:
                rec.update(head)
            rec.update(tail)
        else:
            rec.update({k: (v if first else None) for k, v in head.items() if k in ("raw_reply", "usage")})
            rec.update({k: v for k, v in head.items() if k not in ("raw_reply", "usage")})
            rec.update(tail)
            if not first:
                rec["cost_usd"] = None
        if extra:
            rec.update(extra)
        recs.append(rec)
    return recs


def finalize_document(doc: dict, res: dict) -> dict:
    """R4 enforcement on the judge labels, then the derivation on prefix plus continuation (or
    the whole trace).  Adds r4_notes, labels_raw and derived to res; returns the blocks record."""
    labels_raw = res["labels"]
    labels, notes = D.apply_r4_labels(labels_raw, doc["texts"])
    res["labels_raw"], res["labels"], res["r4_notes"] = labels_raw, labels, notes
    all_labels = doc["prefix_labels"] + labels
    all_texts = doc["prefix_texts"] + doc["texts"]
    source = "reviewed_v4+judge" if doc["continuation"] and doc["prefix_labels"] else "judge"
    der = D.derive(all_labels, doc["trace_id"], source, all_texts)
    rec = {"trace_id": doc["trace_id"], "label_source": source, "r4": True, "nodes": der["nodes"], "blocks": der["blocks"]}
    if doc["continuation"]:
        p = len(doc["prefix_labels"])
        m = doc["meta"]
        node = next(n for n in der["nodes"] if n["s_start"] <= p <= n["s_end"])
        block = next(b for b in der["blocks"] if b["s_start"] <= p <= b["s_end"])
        opens = block["s_start"] == p
        last_prefix = None
        if p:
            pre = D.derive(doc["prefix_labels"], doc["trace_id"], REVIEWED_SOURCE, doc["prefix_texts"])
            last_prefix = D.node_level1(pre["nodes"][-1])
        cont_nodes = [n for n in der["nodes"] if n["s_end"] >= p]
        rec.update({"prefix_id": m["prefix_id"], "trace_arm": m["trace_arm"], "cut": m["cut"], "seq": m.get("seq"),
                    "prefix_n": p, "n_cont": doc["n"], "last_prefix_node_label": last_prefix,
                    "first_new_node": {"name": node["name"], "L1": D.node_level1(node), "s_start": node["s_start"], "s_end": node["s_end"],
                                       "opens_block": opens, "opener_rule": block["opener_rule"] if opens else None,
                                       "spans_cut": node["s_start"] < p},
                    "first_sentence_r4": D.is_r4(doc["texts"][0]) if doc["texts"] else False,
                    "cont_node_sequence": [D.node_level1(n) for n in cont_nodes],
                    "cont_node_names": [n["name"] for n in cont_nodes],
                    "cont_blocks": [{"m": b["m"], "s_start": b["s_start"], "s_end": b["s_end"], "opener_rule": b["opener_rule"], "opener_label": b["opener_label"]}
                                    for b in der["blocks"] if b["s_end"] >= p]})
    res["derived"] = rec
    return rec


def block_sequence_text(rec: dict) -> str:
    """A readable block sequence of a continuation: 'B7: Pl₇ Re₇(3) | B8: ...' from the cut on."""
    if "cont_blocks" not in rec:
        return " ".join(n["name"] for n in rec["nodes"])
    parts = []
    for b in rec["cont_blocks"]:
        names = [n["name"] for n in rec["nodes"] if n["block"] == b["m"] and n["s_end"] >= rec["prefix_n"]]
        parts.append(f"B{b['m']} ({b['opener_rule']}): " + " ".join(names))
    return " | ".join(parts)


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
# Derived tables and the summary of a run folder
# ----------------------------------------------------------------------------

def write_outputs(out_dir: Path, run_id: str, collection: str, is_cont: bool, mode: str, model_id: str, prompt_version: str,
                  prompt_sha: str, thinking_mode: str, n_docs: int, n_valid: int, n_all: int, n_labeled: int, usage_sum: dict,
                  total_cost: float, batches: list[dict], failures: dict[str, dict], blocks_records: list[dict],
                  listing_path: Path | str, source_texts: dict[str, list[str]] | None, notes: list[str] | None = None) -> dict:
    """summary.md and the transition tables of a run folder (pcorpus for whole traces; pnext and
    psource for continuations).  Returns the summary fields derived here."""
    out_dir = Path(out_dir)
    out: dict = {}
    md = [f"# {run_id} — summary", "",
          f"Collection `{collection}` ({'continuations' if is_cont else 'whole traces'}), mode {mode}, model `{model_id}`, prompt {prompt_version} (sha256 `{prompt_sha}`), thinking {thinking_mode}. "
          f"{n_docs} documents, {n_valid} labeled, {len(failures)} failed. Cost ${total_cost:.4f} at {'batch' if mode == 'batch' else 'ordinary'} prices.", ""]
    for note in notes or []:
        md += [note, ""]
    out["thinking_tokens_per_labeled_sentence"] = usage_sum.get("thinking_tokens", 0) / n_labeled if n_labeled else None
    md += ["## Usage", "", "| input | cache read | cache write | output (thinking included) | thinking | labeled sentences | thinking tokens per labeled sentence | cost |", "|---|---|---|---|---|---|---|---|",
           f"| {usage_sum.get('input_tokens', 0)} | {usage_sum.get('cache_read_input_tokens', 0)} | {usage_sum.get('cache_creation_input_tokens', 0)} | {usage_sum.get('output_tokens', 0)} | "
           f"{usage_sum.get('thinking_tokens', 0)} | {n_labeled} of {n_all} | {out['thinking_tokens_per_labeled_sentence'] or float('nan'):.1f} | ${total_cost:.4f} |", ""]
    if mode == "batch":
        md += ["## Batches", "", "| batch id | attempt | entries | submitted | ended | request_counts |", "|---|---|---|---|---|---|"]
        for b in batches:
            md.append(f"| {b['batch_id']} | {b['attempt']} | {b['n_entries']} | {b['submitted']} | {b['ended']} | {json.dumps(b['request_counts'])} |")
        md.append("")
    if failures:
        md += ["## Failures", "", "| trace | attempts | error |", "|---|---|---|"]
        for tid, f in failures.items():
            md.append(f"| {tid} | {f['attempts']} | {str(f['error']).replace('|', '\\|')[:200]} |")
        md.append("")
    if blocks_records:
        if not is_cont:
            pc = T.pcorpus(blocks_records)
            T.write_pcorpus(out_dir, pc)
            out["pcorpus"] = {k: pc[k] for k in ("counts", "rownorm", "marginal", "pairs", "traces", "blocks_per_trace", "nodes_per_trace")}
            md.append(T.markdown_pcorpus(pc, f"P_corpus at Level 1 ({collection}, judge labels under R4)"))
            md.append("")
        else:
            rows = T.pnext(blocks_records, failures)
            pn_path = out_dir / ("pnext_archived.csv" if collection == "archived500" else f"pnext_{collection}.csv")
            T.write_pnext(pn_path, rows)
            out["pnext_path"] = str(pn_path)
            out["pnext_rows"] = rows
            md.append(T.markdown_pnext(rows, f"P(next | cut) after the archived cuts ({collection}; first new node after the cut, judge labels under R4)"))
            md.append("")
            listing = D.parse_listing(listing_path)
            for tid in ("c004", "e036"):
                der = D.derive(listing[tid]["labels"], tid, REVIEWED_SOURCE, source_texts[tid])
                ps = T.psource(der)
                T.write_psource(out_dir / f"psource_{tid}.csv", ps)
                md.append(T.markdown_psource(ps, f"P_source for {tid} (reviewed labels under R4; {len(ps)} block-end cuts)"))
                md.append("")
    (out_dir / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return out


def read_jsonl(path: Path | str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def retry_failed(run_dir: Path | str, client=None, log=print, extra_line: str = FORMAT_CHECK,
                 poll_seconds: int = BATCH_POLL_SECONDS, max_wait_seconds: int = BATCH_MAX_WAIT_SECONDS, sleep=time.sleep) -> dict:
    """--retry-failed (Kian, 2026-09-17): the traces of a finished batch run that are still
    failed are resubmitted once more as one batch (no further follow-up), fresh, with
    `extra_line` appended to the user message and the largest cap they were given before.
    Parsed results are merged into the run's labels_, blocks_ and traces_ files (attempt 3;
    replies/<trace>_attempt3.txt; batch_state_retry.json); summary.md and the transition
    tables are recomputed from the files."""
    run_dir = Path(run_dir)
    config = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))
    collection, is_cont, mode = config["collection"], config.get("continuations", False), config["mode"]
    model_key, prompt_version, thinking_mode = config["model_key"], config["prompt_version"], config["thinking_mode"]
    if mode != "batch":
        raise ValueError("--retry-failed applies to a batch run folder")
    prompt_file, labels_file = prompt_files(prompt_version)
    prompt_text = prompt_file.read_text(encoding="utf-8")
    prompt_sha = sha256_of_file(prompt_file)
    if prompt_sha != config["prompt_sha256"]:
        raise ValueError("the prompt file changed since the run")
    inventory = J.Inventory.load(labels_file)
    traces_path = run_dir / f"traces_{collection}_judge.jsonl"
    labels_path = run_dir / f"labels_{collection}_judge.jsonl"
    blocks_path = run_dir / f"blocks_{collection}_judge.jsonl"
    traces = read_jsonl(traces_path)
    failed = [t for t in traces if not t["valid"]]
    result = {"run_dir": str(run_dir), "collection": collection, "retried": [t["trace_id"] for t in failed], "parsed": [], "failed": [],
              "cost_usd": 0.0, "batches": [], "stopped": None, "extra_line": extra_line}
    if not failed:
        log("nothing to retry: every trace is valid")
        return result
    all_sents = load_sentences(Path(config["sentences"]))
    order = [t["trace_id"] for t in failed]
    cont_meta = reviewed_records = source_texts = None
    if is_cont:
        meta_all = load_archived_meta(config["archived_meta"])
        cont_meta = {t: meta_all[t] for t in order}
        reviewed_records = {}
        for r in read_jsonl(run_dir / f"labels_source_{REVIEWED_SOURCE}.jsonl"):
            reviewed_records.setdefault(r["trace_id"], []).append(r)
        source_texts = D.load_sentence_texts(config["sentences_source"])
    docs = make_documents(all_sents, order, cont_meta, reviewed_records, source_texts, inventory)
    cid_map = json.loads((run_dir / "custom_ids.json").read_text(encoding="utf-8"))
    cid_of = {tid: cid for cid, tid in cid_map.items()}
    prior = {t["trace_id"]: t for t in failed}
    requests: dict[str, dict] = {}
    for doc in docs:
        tid = doc["trace_id"]
        req = document_request(doc, prompt_text, model_key, thinking_mode)
        req["messages"][0]["content"] = req["messages"][0]["content"] + "\n" + extra_line
        caps = prior[tid].get("max_tokens") or []
        req["max_tokens"] = max([req["max_tokens"]] + caps)
        requests[cid_of[tid]] = req
        written = dict(req)
        written["system"] = [{"type": "text", "text": f"<prompt {prompt_file.name} sha256 {prompt_sha}>", "cache_control": {"type": "ephemeral"}}]
        (run_dir / "requests" / f"{cid_of[tid]}_retry.json").write_text(json.dumps(written, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    first_attempt = max(t["attempts"] for t in failed) + 1
    log(f"retrying {len(docs)} failed traces as one batch (attempt {first_attempt}) with the format-check line")
    if client is None:
        client = make_client()
    with open(run_dir / "_log.txt", "a", encoding="utf-8", newline="\n") as lg:
        lg.write(f"# retry_failed {datetime.now().isoformat(timespec='seconds')}: {len(docs)} traces, attempt {first_attempt}, extra line: {extra_line}\n")

        def both(msg: str):
            lg.write(msg.rstrip("\n") + "\n")
            lg.flush()
            log(msg)

        out = judge_batch(client, docs, requests, cid_of, run_dir, inventory, model_key, thinking_mode, both, None, poll_seconds,
                          max_wait_seconds, sleep, first_attempt=first_attempt, n_attempts=1, state_name="batch_state_retry.json")
        result["batches"] = out["batches"]
        if out["stopped"]:
            result["stopped"] = out["stopped"]
            return result
        timestamp = datetime.now().isoformat(timespec="seconds")
        merged: dict[str, dict] = {}
        with open(labels_path, "a", encoding="utf-8", newline="\n") as lf, open(blocks_path, "a", encoding="utf-8", newline="\n") as bf:
            for doc in docs:
                tid = doc["trace_id"]
                res = out["results"][tid]
                p = prior[tid]
                result["cost_usd"] += res["cost_usd"]
                usage = add_usage(p.get("usage") or {}, res["usage"])
                rec = {**p, "attempts": res["attempts"], "valid": res["valid"], "batch_ids": (p.get("batch_ids") or []) + res["batch_ids"],
                       "max_tokens": (p.get("max_tokens") or []) + res["max_tokens"], "stop_reasons": (p.get("stop_reasons") or []) + res["stop_reasons"],
                       "usage": usage, "thinking_tokens": usage.get("thinking_tokens", 0), "cost_usd": (p.get("cost_usd") or 0.0) + res["cost_usd"],
                       "model": res["model"] or p.get("model"), "leaks": (p.get("leaks") or []) + res["leaks"], "warnings": res["warnings"],
                       "error": res["error"], "timestamp": timestamp, "retry_extra_line": extra_line}
                lg.write(f"{tid}\t{res['attempts']}\t{res['valid']}\t{res['usage'].get('input_tokens', 0)}\t{res['usage'].get('cache_read_input_tokens', 0)}\t"
                         f"{res['usage'].get('cache_creation_input_tokens', 0)}\t{res['usage'].get('output_tokens', 0)}\t{res['cost_usd']:.6f}\t{res['stop_reasons']}\t"
                         f"{res['thinking_tokens']}\t{res['leaks']}\t{res['batch_ids']}\t{res.get('error') or ''}\n")
                if res["valid"]:
                    bl = finalize_document(doc, res)
                    res["usage"], res["cost_usd"] = usage, rec["cost_usd"]
                    extra = None
                    if doc["continuation"]:
                        extra = {"prefix_id": doc["meta"]["prefix_id"], "trace_arm": doc["meta"]["trace_arm"], "cut": doc["meta"]["cut"], "prefix_n": len(doc["prefix_labels"])}
                    for lrec in label_records(res, run_dir.name, prompt_sha, timestamp, prompt_version, extra, lean=True):
                        lf.write(json.dumps(lrec, ensure_ascii=False, separators=(",", ":")) + "\n")
                    bf.write(json.dumps(bl, ensure_ascii=False) + "\n")
                    rec.update({"nodes": len(bl["nodes"]), "blocks": len(bl["blocks"]), "r4_changed": sum(1 for x in res["r4_notes"] if x and x["changed"]),
                                "first_new_node": bl.get("first_new_node"), "block_sequence": block_sequence_text(bl)})
                    result["parsed"].append(tid)
                else:
                    result["failed"].append({"trace_id": tid, "error": res["error"]})
                merged[tid] = rec
    with open(traces_path, "w", encoding="utf-8", newline="\n") as tf:
        for t in traces:
            tf.write(json.dumps(merged.get(t["trace_id"], t), ensure_ascii=False) + "\n")
    config.setdefault("batches", []).extend(out["batches"])
    config["retry_failed"] = {"extra_line": extra_line, "traces": order, "attempt": first_attempt, "timestamp": timestamp,
                              "parsed": result["parsed"], "failed": [f["trace_id"] for f in result["failed"]], "cost_usd": result["cost_usd"]}
    (run_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    # recompute summary.md and the transition tables from the files
    traces = read_jsonl(traces_path)
    blocks_records = read_jsonl(blocks_path)
    failures = {t["trace_id"]: {k: t.get(k) for k in ("prefix_id", "trace_arm", "cut", "prefix_n")} | {"error": t["error"], "attempts": t["attempts"]}
                for t in traces if not t["valid"]}
    usage_sum: dict = {}
    for t in traces:
        if t.get("usage"):
            usage_sum = add_usage(usage_sum, t["usage"])
    total_cost = sum(t.get("cost_usd") or 0.0 for t in traces)
    n_labeled = sum(t["n"] for t in traces if t["valid"])
    n_all = sum(t["n"] for t in traces)
    note = (f"Retry of the failed traces on {timestamp} (attempt {first_attempt}, one batch, the format-check line appended): "
            f"{len(result['parsed'])} parsed, {len(result['failed'])} still failed, cost ${result['cost_usd']:.4f}; tables below recomputed from the files.")
    outputs = write_outputs(run_dir, run_dir.name, collection, is_cont, mode, config["model"], prompt_version, prompt_sha, thinking_mode,
                            len(traces), sum(1 for t in traces if t["valid"]), n_all, n_labeled, usage_sum, total_cost, config["batches"],
                            failures, blocks_records, config.get("reviewed_listing") or D.LISTING, source_texts, notes=[note])
    result.update({k: v for k, v in outputs.items() if k != "pnext_rows"})
    result["pnext_rows"] = outputs.get("pnext_rows")
    result["total_cost_usd"] = total_cost
    return result


# ----------------------------------------------------------------------------
# The run
# ----------------------------------------------------------------------------

def run_judge(sentences_path: Path, out_dir: Path, traces: list[str] | None = None, dry_run: bool = False,
              client=None, reviewed_path: Path | None = None, run_id: str | None = None, log=print,
              model_key: str = "haiku", prompt_version: str = "v1", thinking_mode: str = "off",
              mode: str = "ordinary", collection: str | None = None, archived_meta_path: Path | None = ARCHIVED_CONTINUATIONS,
              listing_path: Path | str = D.LISTING, sentences_source: Path | str = SENTENCES_SOURCE,
              resume_batch: str | None = None, poll_seconds: int = BATCH_POLL_SECONDS,
              max_wait_seconds: int = BATCH_MAX_WAIT_SECONDS, sleep=time.sleep) -> dict:
    """The whole step for one collection.  Returns a summary dict (per trace results, paths)."""
    if model_key not in MODELS:
        raise ValueError(f"unknown model {model_key!r}; known: {tuple(MODELS)}")
    if mode not in ("ordinary", "batch"):
        raise ValueError(f"unknown mode {mode!r}")
    tparams = thinking_params(model_key, thinking_mode)
    sentences_path, out_dir = Path(sentences_path), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    file_collection = collection_name(sentences_path)
    collection = collection or file_collection
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
    # continuation collections: every trace id known to the archived continuation file
    cont_meta = None
    reviewed_records = None
    source_texts = None
    if archived_meta_path is not None and Path(archived_meta_path).exists():
        meta_all = load_archived_meta(archived_meta_path)
        known = [t for t in order if t in meta_all]
        if known and len(known) != len(order):
            raise ValueError(f"{len(known)} of {len(order)} traces are archived continuations; a collection must be all continuations or none")
        if known:
            cont_meta = {t: meta_all[t] for t in order}
            reviewed_records = export_reviewed_labels(out_dir / f"labels_source_{REVIEWED_SOURCE}.jsonl", listing_path, sentences_source, inventory)
            source_texts = D.load_sentence_texts(sentences_source)
    docs = make_documents(all_sents, order, cont_meta, reviewed_records, source_texts, inventory)
    is_cont = cont_meta is not None
    summary = {"collection": collection, "run_id": run_id, "out_dir": str(out_dir), "traces": {}, "stopped": None,
               "total_cost_usd": 0.0, "dry_run": dry_run, "model_key": model_key, "model_id": model["id"],
               "prompt_version": prompt_version, "thinking_mode": thinking_mode, "mode": mode, "continuations": is_cont,
               "batches": []}
    # build and write every request (the system prompt replaced by its hash in batch mode)
    req_dir = out_dir / "requests"
    req_dir.mkdir(exist_ok=True)
    taken: set[str] = set()
    cid_of: dict[str, str] = {}
    requests: dict[str, dict] = {}
    for doc in docs:
        tid = doc["trace_id"]
        req = document_request(doc, prompt_text, model_key, thinking_mode)
        cid = safe_custom_id(tid, taken)
        cid_of[tid] = cid
        requests[cid] = req
        est = estimate_input_tokens(req)
        written = dict(req)
        if mode == "batch":
            written["system"] = [{"type": "text", "text": f"<prompt {prompt_file.name} sha256 {prompt_sha}>", "cache_control": {"type": "ephemeral"}}]
        (req_dir / f"{cid}.json").write_text(json.dumps(written, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        summary["traces"][tid] = {"n": doc["n"], "estimated_input_tokens": est, "custom_id": cid, "prefix_n": len(doc["prefix_labels"]),
                                  "max_tokens": req["max_tokens"]}
        if len(docs) <= 50:
            log(f"request {tid}: {doc['n']} sentences" + (f" after a prefix of {len(doc['prefix_labels'])}" if doc["continuation"] else "")
                + f", about {est} input tokens (characters/4), max_tokens {req['max_tokens']}")
    if mode == "batch":
        (out_dir / "custom_ids.json").write_text(json.dumps({cid: tid for tid, cid in cid_of.items()}, indent=1) + "\n", encoding="utf-8")
    log(f"{len(docs)} documents, {sum(d['n'] for d in docs)} sentences to label" + (f" ({sum(len(d['prefix_labels']) for d in docs)} prefix sentences shown)" if is_cont else ""))
    import anthropic
    import requests as requests_lib
    import pytest
    config = {
        "run_id": run_id, "collection": collection, "mode": "dry-run" if dry_run else mode,
        "continuations": is_cont, "archived_meta": str(archived_meta_path) if is_cont else None,
        "reviewed_listing": str(listing_path) if is_cont else None, "sentences_source": str(sentences_source) if is_cont else None,
        "model_key": model_key, "model": model["id"], "model_echoed": {},
        "max_tokens": {"default": MAX_TOKENS_THINKING if tparams else MAX_TOKENS, "long_documents": MAX_TOKENS_THINKING_LONG if tparams else MAX_TOKENS,
                       "long_document_sentences": LONG_DOCUMENT_SENTENCES, "retry_after_max_tokens": "doubled", "cap": MAX_TOKENS_CAP},
        "temperature": model["temperature"],
        "temperature_via": "extra_body" if model["temperature"] is not None else "not sent (the model rejects sampling parameters)",
        "thinking_mode": thinking_mode,
        "thinking_params": tparams if tparams else (model["thinking"] if model["thinking"] is not None else "omitted (the model runs without thinking by default)"),
        "reply_instruction": REPLY_INSTRUCTION if thinking_mode == "none" else None,
        "thinking_tokens": {}, "final_stop_reason": {},
        "prompt_version": prompt_version, "prompt": prompt_file.name, "prompt_sha256": prompt_sha,
        "inventory": labels_file.name, "inventory_sha256": sha256_of_file(labels_file),
        "sentences": str(sentences_path), "sentences_sha256": sha256_of_file(sentences_path),
        "traces": order if len(order) <= 100 else f"{len(order)} traces (see custom_ids.json)", "n_traces": len(order),
        "r4": {"regex": D.R4_RE.pattern, "enforced_on_judge_labels": True},
        "git_commit": git_head(), "python": sys.version.split()[0],
        "anthropic": anthropic.__version__, "requests": requests_lib.__version__, "pytest": pytest.__version__,
        "prices_usd_per_million": BATCH_PRICES[model_key] if mode == "batch" else model["prices"],
        "batch": {"poll_seconds": poll_seconds, "max_wait_seconds": max_wait_seconds, "resume_batch": resume_batch} if mode == "batch" else None,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
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
    traces_path = out_dir / f"traces_{collection}_judge.jsonl"
    log_path = out_dir / "_log.txt"
    judge_labels: dict[str, list[list[str]]] = {}
    blocks_records: list[dict] = []
    failures: dict[str, dict] = {}
    lean = mode == "batch"
    with open(labels_path, "w", encoding="utf-8", newline="\n") as lf, open(blocks_path, "w", encoding="utf-8", newline="\n") as bf, \
            open(traces_path, "w", encoding="utf-8", newline="\n") as tf, open(log_path, "a", encoding="utf-8", newline="\n") as lg:
        lg.write(f"# s1_judge run_id={run_id} mode={mode} model={model['id']} ({model_key}) prompt={prompt_version} thinking={thinking_mode} {config['timestamp']}\n")
        lg.write("# trace_id\tattempts\tvalid\tinput\tcache_read\tcache_write\toutput\tcost_usd\tstop_reasons\tthinking_tokens\tleaks\tbatch_ids\terror\n")

        def both(msg: str):
            lg.write(msg.rstrip("\n") + "\n")
            lg.flush()
            log(msg)

        def record(doc: dict, res: dict, timestamp: str):
            tid = doc["trace_id"]
            u = res["usage"]
            config["model_echoed"][tid] = res["model"]
            config["thinking_tokens"][tid] = res["thinking_tokens"]
            config["final_stop_reason"][tid] = res["final_stop_reason"]
            lg.write(f"{tid}\t{res['attempts']}\t{res['valid']}\t{u.get('input_tokens', 0)}\t{u.get('cache_read_input_tokens', 0)}\t"
                     f"{u.get('cache_creation_input_tokens', 0)}\t{u.get('output_tokens', 0)}\t{res['cost_usd']:.6f}\t{res['stop_reasons']}\t"
                     f"{res['thinking_tokens']}\t{res['leaks']}\t{res.get('batch_ids')}\t{res.get('error') or ''}\n")
            lg.flush()
            summary["total_cost_usd"] += res["cost_usd"]
            t = summary["traces"][tid]
            t.update({"attempts": res["attempts"], "valid": res["valid"], "usage": u, "cost_usd": res["cost_usd"],
                      "model": res["model"], "stop_reasons": res["stop_reasons"], "retry_message": res["retry_message"],
                      "error": res["error"], "warnings": res["warnings"], "thinking_tokens": res["thinking_tokens"],
                      "leaks": res["leaks"], "final_stop_reason": res["final_stop_reason"], "thinking_chars": res["thinking_chars"],
                      "batch_ids": res.get("batch_ids"), "max_tokens_used": res.get("max_tokens")})
            extra = None
            if doc["continuation"]:
                extra = {"prefix_id": doc["meta"]["prefix_id"], "trace_arm": doc["meta"]["trace_arm"], "cut": doc["meta"]["cut"], "prefix_n": len(doc["prefix_labels"])}
            trace_rec = {"trace_id": tid, "custom_id": res.get("custom_id"), "n": doc["n"], "continuation": doc["continuation"],
                         **(extra or {}), "attempts": res["attempts"], "valid": res["valid"], "batch_ids": res.get("batch_ids"),
                         "max_tokens": res.get("max_tokens"), "stop_reasons": res["stop_reasons"], "usage": u,
                         "thinking_tokens": res["thinking_tokens"], "cost_usd": res["cost_usd"], "model": res["model"],
                         "leaks": res["leaks"], "warnings": res["warnings"], "error": res["error"], "timestamp": timestamp}
            if res["valid"]:
                bl = finalize_document(doc, res)
                for rec in label_records(res, run_id, prompt_sha, timestamp, prompt_version, extra, lean):
                    lf.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":") if lean else None) + "\n")
                judge_labels[tid] = res["labels"]
                blocks_records.append(bl)
                t.update({"nodes": len(bl["nodes"]), "blocks": len(bl["blocks"]), "r4_changed": sum(1 for x in res["r4_notes"] if x and x["changed"])})
                trace_rec.update({"nodes": len(bl["nodes"]), "blocks": len(bl["blocks"]), "r4_changed": t["r4_changed"],
                                  "first_new_node": bl.get("first_new_node"), "block_sequence": block_sequence_text(bl)})
                bf.write(json.dumps(bl, ensure_ascii=False) + "\n")
            else:
                failures[tid] = {**(extra or {}), "error": res["error"], "attempts": res["attempts"]}
            tf.write(json.dumps(trace_rec, ensure_ascii=False) + "\n")
            tf.flush()

        if mode == "ordinary":
            for doc in docs:
                tid = doc["trace_id"]
                timestamp = datetime.now().isoformat(timespec="seconds")
                res = judge_trace(streaming_create(client), tid, doc["sents"], prompt_text, inventory, out_dir / "replies",
                                  model_key, thinking_mode, request=requests[cid_of[tid]])
                res["custom_id"] = None
                record(doc, res, timestamp)
                write_config()
                log(f"{tid}: attempts {res['attempts']}, valid {res['valid']}, usage {res['usage']}, cost ${res['cost_usd']:.6f}")
                if not res["valid"]:
                    summary["stopped"] = f"{tid}: {res['error']}"
                    both(f"# STOP: {tid} failed after {res['attempts']} attempts: {res['error']}")
                    break
        else:
            t0 = time.monotonic()
            out = judge_batch(client, docs, requests, cid_of, out_dir, inventory, model_key, thinking_mode, both, resume_batch,
                              poll_seconds, max_wait_seconds, sleep)
            summary["batches"] = out["batches"]
            summary["batch_seconds"] = round(time.monotonic() - t0)
            config["batches"] = out["batches"]
            if out["stopped"]:
                summary["stopped"] = out["stopped"]
            else:
                timestamp = datetime.now().isoformat(timespec="seconds")
                for doc in docs:
                    record(doc, out["results"][doc["trace_id"]], timestamp)
                write_config()
    summary["labels_path"], summary["blocks_path"], summary["traces_path"] = str(labels_path), str(blocks_path), str(traces_path)
    summary["failures"] = failures
    summary["n_valid"] = len(judge_labels)
    if summary["stopped"] and mode == "batch":
        log(f"run stopped: {summary['stopped']}")
        return summary
    # derived tables and the summary
    usage_sum: dict = {}
    for t in summary["traces"].values():
        if t.get("usage"):
            usage_sum = add_usage(usage_sum, t["usage"])
    n_labeled = sum(summary["traces"][t]["n"] for t in judge_labels)
    n_all = sum(d["n"] for d in docs)
    summary["usage"] = usage_sum
    summary.update(write_outputs(out_dir, run_id, collection, is_cont, mode, model["id"], prompt_version, prompt_sha, thinking_mode,
                                 len(docs), summary["n_valid"], n_all, n_labeled, usage_sum, summary["total_cost_usd"], summary["batches"],
                                 failures, blocks_records, listing_path, source_texts))
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
    ap = argparse.ArgumentParser(description="Pipeline steps (4/9) and (5/9): the judge on a collection.")
    ap.add_argument("--sentences", required="--retry-failed" not in (argv if argv is not None else sys.argv[1:]))
    ap.add_argument("--collection", help="collection name (default: from the sentences file name)")
    ap.add_argument("--mode", choices=["ordinary", "batch"], default="ordinary")
    ap.add_argument("--out", help="run folder (default runs/experiments/judge_<collection>_<model>_<version>_<date>_<hhmm>)")
    ap.add_argument("--trace", action="append", help="run this trace only (repeatable)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--reviewed", help="the reviewed listing; writes the agreement and residue files (source traces)")
    ap.add_argument("--model", choices=tuple(MODELS), default="haiku")
    ap.add_argument("--prompt-version", choices=PROMPT_VERSIONS, default="v1")
    ap.add_argument("--thinking", choices=THINKING_MODES, default="off",
                    help="off (default): current behaviour; none: thinking disabled plus the labels-only closing line; "
                         "low/medium: adaptive thinking at that effort (Sonnet 5 only)")
    ap.add_argument("--archived", default=str(ARCHIVED_CONTINUATIONS), help="archived continuation file giving prefix_id, trace_arm and cut per continuation id")
    ap.add_argument("--listing", default=str(D.LISTING), help="reviewed listing exported as the prefix labels of continuations")
    ap.add_argument("--sentences-source", default=str(SENTENCES_SOURCE), help="sentences_source.jsonl (prefix texts, old_s)")
    ap.add_argument("--resume-batch", help="batch mode: continue with this batch id instead of submitting")
    ap.add_argument("--poll-seconds", type=int, default=BATCH_POLL_SECONDS)
    ap.add_argument("--max-wait-hours", type=float, default=BATCH_MAX_WAIT_SECONDS / 3600)
    ap.add_argument("--retry-failed", metavar="RUN_DIR", help="resubmit the still-failed traces of this batch run once more (format-check line appended) and merge")
    args = ap.parse_args(argv)
    if args.retry_failed:
        res = retry_failed(args.retry_failed, poll_seconds=args.poll_seconds, max_wait_seconds=int(args.max_wait_hours * 3600))
        print(json.dumps({k: v for k, v in res.items() if k != "pnext_rows"}, indent=2, default=str))
        return 0 if not res["stopped"] else 1
    collection = args.collection or collection_name(Path(args.sentences))
    tag = f"_think{args.thinking}" if args.thinking != "off" else ""
    out_dir = Path(args.out) if args.out else REPO / "runs" / "experiments" / f"judge_{collection}_{args.model}_{args.prompt_version}{tag}_{datetime.now():%Y-%m-%d_%H%M}"
    prompt_file, _ = prompt_files(args.prompt_version)
    print(f"s1_judge: sentences={args.sentences} collection={collection} mode={args.mode} out={out_dir} model={MODELS[args.model]['id']} ({args.model}) "
          f"thinking={args.thinking} prompt={prompt_file.name} sha256={sha256_of_file(prompt_file)[:12]} dry_run={args.dry_run} git={git_head()}")
    summary = run_judge(Path(args.sentences), out_dir, args.trace, args.dry_run,
                        reviewed_path=Path(args.reviewed) if args.reviewed else None,
                        model_key=args.model, prompt_version=args.prompt_version, thinking_mode=args.thinking,
                        mode=args.mode, collection=collection, archived_meta_path=Path(args.archived) if args.archived else None,
                        listing_path=args.listing, sentences_source=args.sentences_source, resume_batch=args.resume_batch,
                        poll_seconds=args.poll_seconds, max_wait_seconds=int(args.max_wait_hours * 3600))
    print(json.dumps({k: v for k, v in summary.items() if k not in ("agreement", "pnext_rows", "pcorpus", "traces")}, indent=2, default=str))
    if summary.get("traces") and len(summary["traces"]) <= 10:
        print(json.dumps(summary["traces"], indent=2, default=str))
    return 0 if not summary["stopped"] else 1


if __name__ == "__main__":
    sys.exit(main())
