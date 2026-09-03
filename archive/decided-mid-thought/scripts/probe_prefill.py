"""
Probe which prefill strategy makes Qwen 3.6 27B (DeepInfra via OpenRouter) CONTINUE
a truncated thinking trace instead of restarting. One call per strategy (~$0.10 total).

Run:  python scripts/probe_prefill.py
Then read each verdict + continuation start. A strategy PASSES only if the
continuation picks up the argument mid-stream (here: right after "This is
logically the most accurate description." at c004 cut-62, i.e. it should move
on to justifications/other options, NOT restart with fresh problem analysis).
"""
import collections, json, os, re
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

MODEL = "qwen/qwen3.6-27b"
PROVIDER_ROUTING = {"order": ["DeepInfra"], "allow_fallbacks": False}
SOURCE = "runs/sweep_items_batball_2026-08-19_1623.jsonl"

def split_sentences(text):                      # verbatim reading-pack splitter
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
prompt = src["prompt"]
prefix = " ".join(split_sentences(src["trace"])[:63])          # s0..s62 = cut-62

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OpenRouter_API_KEY"])
RESTART_MARKERS = ["the user wants", "let me analyze", "analyze the user", "thinking process",
                   "the user is asking", "first, "]

def verdict(cont):
    head = (cont or "")[:250].lower()
    flags = [m for m in RESTART_MARKERS if m in head]
    return ("LOOKS LIKE RESTART: " + ", ".join(flags)) if flags else "no restart markers (verify by eye)"

def show(name, fn):
    print("=" * 90); print(name)
    try:
        r = fn()
        ch = r.choices[0]; msg = ch.message if hasattr(ch, "message") else None
        if msg is not None:
            reasoning = getattr(msg, "reasoning", None) or (getattr(msg, "model_extra", None) or {}).get("reasoning") \
                        or (getattr(msg, "model_extra", None) or {}).get("reasoning_content") or ""
            content = msg.content or ""
        else:                                   # completions endpoint
            reasoning, content = "", ch.text or ""
        print("finish:", ch.finish_reason, "| provider:", getattr(r, "provider", None))
        cont = reasoning if reasoning else content
        print("VERDICT:", verdict(cont))
        print("continuation[:400]:", cont[:400].replace("\n", " | "))
        if reasoning and content: print("content[:150]:", content[:150].replace("\n", " | "))
    except Exception as e:
        print("ERROR:", str(e)[:300])

kw = dict(temperature=1.0, max_tokens=8000, timeout=600)

show("S1  chat, assistant content='<think>\\n'+prefix  (current approach — expected FAIL)",
     lambda: client.chat.completions.create(model=MODEL, **kw,
        messages=[{"role": "user", "content": prompt},
                  {"role": "assistant", "content": "<think>\n" + prefix}],
        extra_body={"reasoning": {"enabled": True}, "provider": PROVIDER_ROUTING}))

show("S2  chat, assistant reasoning-field prefill (documented reasoning pass-back)",
     lambda: client.chat.completions.create(model=MODEL, **kw,
        messages=[{"role": "user", "content": prompt},
                  {"role": "assistant", "content": "", "reasoning": prefix}],
        extra_body={"reasoning": {"enabled": True}, "provider": PROVIDER_ROUTING}))

show("S3  chat, assistant reasoning-field + partial=true (vLLM/Kimi-style continuation flag)",
     lambda: client.chat.completions.create(model=MODEL, **kw,
        messages=[{"role": "user", "content": prompt},
                  {"role": "assistant", "content": "", "reasoning": prefix, "partial": True}],
        extra_body={"reasoning": {"enabled": True}, "provider": PROVIDER_ROUTING}))

show("S4  raw /completions, manual Qwen template + open <think> (token-level continuation)",
     lambda: client.completions.create(model=MODEL, **kw,
        prompt=(f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n<think>\n{prefix}"),
        extra_body={"provider": PROVIDER_ROUTING}))

print("=" * 90)
print("Pick the FIRST passing strategy in order S4 > S3 > S2 (S4 is cleanest: true token-level")
print("continuation). Report results back before we patch resample_cuts.py.")
