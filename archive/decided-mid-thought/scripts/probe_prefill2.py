"""
Round 2: is the raw /completions route a TRUE token-level continuation?

P1  raw-text prefix (original trace formatting, cut at end of sentence 62) — behavior test
P2  same prefix truncated MID-WORD — mechanism test: a genuine continuation must
    complete the word ("...most accurate desc" -> "ription.")
P3  space-joined prefix (round-1 S4) — comparison, to see if reformatting caused the soft restart

Prints the FULL head of each completion, whether/where </think> occurs, the final
Answer line, and token usage.
"""
import collections, json, os, re
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

MODEL = "qwen/qwen3.6-27b"
PROVIDER_ROUTING = {"order": ["DeepInfra"], "allow_fallbacks": False}
SOURCE = "runs/sweep_items_batball_2026-08-19_1623.jsonl"

def split_sentences(text):
    sents = []
    for line in text.split("\n"):
        line = line.strip()
        if not line: continue
        parts = re.split(r'(?<=[.!?:])\s+', line)
        sents.extend(p for p in parts if p.strip())
    return sents

counts, byid = collections.Counter(), {}
for line in open(SOURCE, encoding="utf-8"):
    r = json.loads(line)
    counts[r["condition"]] += 1
    byid[f"s0819_{r['condition'].replace('_','')}_{counts[r['condition']]:03d}"] = r
src = byid["s0819_eval0multi0_004"]
prompt, trace = src["prompt"], src["trace"]
sents = split_sentences(trace)

# map sentence index -> end offset in the RAW trace (sequential exact-match search)
pos, ends = 0, []
for s in sents:
    i = trace.find(s, pos)
    assert i >= 0, f"sentence not found in raw trace: {s[:60]}"
    pos = i + len(s); ends.append(pos)

raw62 = trace[:ends[62]]                       # raw formatting, ends "...most accurate description."
midword = raw62[:-len("ription.")]             # ends "...the most accurate desc"
joined62 = " ".join(sents[:63])                # round-1 S4 prefix, for comparison

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OpenRouter_API_KEY"])
TPL = "<|im_start|>user\n{p}<|im_end|>\n<|im_start|>assistant\n<think>\n{pre}"

def show(name, prefix, expect_start=None):
    print("=" * 90); print(name)
    print("prefix tail:", repr(prefix[-80:]))
    try:
        r = client.completions.create(model=MODEL, prompt=TPL.format(p=prompt, pre=prefix),
                temperature=1.0, max_tokens=8000, timeout=600,
                extra_body={"provider": PROVIDER_ROUTING})
        t = r.choices[0].text or ""
        u = r.usage and r.usage.model_dump() or {}
        print("finish:", r.choices[0].finish_reason, "| usage:", {k: u.get(k) for k in ("prompt_tokens","completion_tokens")})
        if expect_start is not None:
            print("MECHANISM:", "PASS — completes the cut word" if t.lstrip().startswith(expect_start)
                  or t.startswith(expect_start) else f"FAIL — starts {repr(t[:40])}, expected {repr(expect_start)}")
        k = t.find("</think>")
        print("</think> at char:", k if k >= 0 else "ABSENT")
        print("completion[:900]:", t[:900].replace("\n", " | "))
        m = re.findall(r"Answer:\s*[A-J].*", t)
        print("Answer line:", m[-1][:60] if m else "NONE")
    except Exception as e:
        print("ERROR:", str(e)[:300])

show("P1  RAW-formatting prefix, cut at end of s62", raw62)
show("P2  RAW prefix cut MID-WORD ('...accurate desc')", midword, expect_start="ription")
show("P3  space-joined prefix (round-1 S4, for comparison)", joined62)
print("=" * 90)
print("P2 is decisive: if it completes 'desc'->'ription.', the endpoint is a true token-level")
print("continuation and any residual restart behavior is the MODEL's choice, not the harness.")
