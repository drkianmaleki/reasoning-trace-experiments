"""
Round 3 = round 2 + (a) reads BOTH channels of the completions choice (text AND the
reasoning field OpenRouter may normalize think-content into), (b) 429-aware retries,
(c) prints head AND tail of the continuation to detect repetition loops.
"""
import collections, json, os, re, time
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
        sents.extend(p for p in re.split(r'(?<=[.!?:])\s+', line) if p.strip())
    return sents

counts, byid = collections.Counter(), {}
for line in open(SOURCE, encoding="utf-8"):
    r = json.loads(line)
    counts[r["condition"]] += 1
    byid[f"s0819_{r['condition'].replace('_','')}_{counts[r['condition']]:03d}"] = r
src = byid["s0819_eval0multi0_004"]
prompt, trace = src["prompt"], src["trace"]
sents = split_sentences(trace)
pos, ends = 0, []
for s in sents:
    i = trace.find(s, pos); assert i >= 0
    pos = i + len(s); ends.append(pos)
raw62 = trace[:ends[62]]
midword = raw62[:-len("ription.")]
joined62 = " ".join(sents[:63])

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OpenRouter_API_KEY"])
TPL = "<|im_start|>user\n{p}<|im_end|>\n<|im_start|>assistant\n<think>\n{pre}"

def call(prefix):
    last = None
    for attempt in range(6):
        try:
            return client.completions.create(model=MODEL, prompt=TPL.format(p=prompt, pre=prefix),
                temperature=1.0, max_tokens=8000, timeout=600,
                extra_body={"provider": PROVIDER_ROUTING})
        except Exception as e:
            last = e
            wait = 20 * (attempt + 1)
            print(f"  retry {attempt+1} in {wait}s: {str(e)[:110]}")
            time.sleep(wait)
    raise last

def show(name, prefix, expect_start=None):
    print("=" * 90); print(name)
    print("prefix tail:", repr(prefix[-70:]))
    try:
        r = call(prefix)
        ch = r.choices[0]
        text = ch.text or ""
        extra = getattr(ch, "model_extra", None) or {}
        reasoning = extra.get("reasoning") or extra.get("reasoning_content") or ""
        u = r.usage and r.usage.model_dump() or {}
        print("finish:", ch.finish_reason, "| usage:", {k: u.get(k) for k in ("prompt_tokens","completion_tokens")})
        print("channels: text_len =", len(text), "| reasoning_len =", len(reasoning))
        cont = reasoning if reasoning else text
        if expect_start is not None:
            got = cont.lstrip()[:20]
            print("MECHANISM:", "PASS — completes the cut word" if cont.startswith(expect_start)
                  or cont.lstrip().startswith(expect_start) else f"FAIL — starts {repr(got)}")
        print("head[:700]:", cont[:700].replace("\n", " | "))
        print("tail[-300:]:", cont[-300:].replace("\n", " | "))
        if reasoning and text:
            print("text-channel head[:200]:", text[:200].replace("\n", " | "))
        m = re.findall(r"Answer:\s*[A-J].*", text + "\n" + reasoning)
        print("Answer line:", m[-1][:60] if m else "NONE")
    except Exception as e:
        print("ERROR (after retries):", str(e)[:200])
    time.sleep(10)          # stagger to stay under the upstream limit

show("P1  RAW-formatting prefix, cut at end of s62", raw62)
show("P2  RAW prefix cut MID-WORD ('...accurate desc')", midword, expect_start="ription")
show("P3  space-joined prefix (round-1 S4, comparison)", joined62)
print("=" * 90)
print("Reminder: P2 decides the mechanism. Also check P1's tail for loops (finish=length")
print("with repeating text = degenerate continuation, a different problem than restarts).")
