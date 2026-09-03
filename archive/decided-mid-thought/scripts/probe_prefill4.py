"""
Round 4: DeepInfra DIRECT (no OpenRouter). Their /v1/openai/completions is documented
as raw prompt continuation. Needs DEEPINFRA_API_KEY in .env.

Step 1: list available models matching 'qwen3.6' (exact slug unknown a priori).
Step 2: mid-word mechanism test + full-prefix behavior test with the Qwen template.
"""
import collections, json, os, re, time
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

SOURCE = "runs/sweep_items_batball_2026-08-19_1623.jsonl"
client = OpenAI(base_url="https://api.deepinfra.com/v1/openai", api_key=os.environ["DEEPINFRA_API_KEY"])

# ---- step 1: find the model slug ----
cands = []
try:
    for m in client.models.list():
        if "qwen3.6" in m.id.lower().replace("-", "").replace("_", "").replace(".", ".") or "qwen3.6" in m.id.lower():
            cands.append(m.id)
except Exception as e:
    print("model list failed:", str(e)[:150])
print("qwen3.6 candidates on DeepInfra:", cands or "NONE FOUND — check the DeepInfra model catalog by hand")
MODEL = next((c for c in cands if "27" in c), cands[0] if cands else None)
if MODEL is None:
    raise SystemExit("No Qwen 3.6 model found on direct DeepInfra — report back before proceeding.")
print("using:", MODEL)

# ---- prefixes (identical construction to round 3) ----
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
TPL = "<|im_start|>user\n{p}<|im_end|>\n<|im_start|>assistant\n<think>\n{pre}"

def call(prefix):
    last = None
    for attempt in range(5):
        try:
            return client.completions.create(model=MODEL, prompt=TPL.format(p=prompt, pre=prefix),
                temperature=1.0, max_tokens=12000, timeout=600, stop=["<|im_end|>"])
        except Exception as e:
            last = e; wait = 20 * (attempt + 1)
            print(f"  retry {attempt+1} in {wait}s: {str(e)[:110]}")
            time.sleep(wait)
    raise last

def show(name, prefix, expect_start=None):
    print("=" * 90); print(name)
    print("prefix tail:", repr(prefix[-70:]))
    try:
        r = call(prefix)
        ch = r.choices[0]; t = ch.text or ""
        extra = getattr(ch, "model_extra", None) or {}
        reasoning = extra.get("reasoning") or extra.get("reasoning_content") or ""
        u = r.usage and r.usage.model_dump() or {}
        print("finish:", ch.finish_reason, "| usage:", {k: u.get(k) for k in ("prompt_tokens","completion_tokens","estimated_cost")})
        print("channels: text_len =", len(t), "| reasoning_len =", len(reasoning))
        cont = t if t else reasoning
        if expect_start is not None:
            print("MECHANISM:", "PASS — completes the cut word" if cont.startswith(expect_start)
                  or cont.lstrip().startswith(expect_start) else f"FAIL — starts {repr(cont[:40])}")
        k = cont.find("</think>")
        print("</think> at char:", k if k >= 0 else "ABSENT")
        print("head[:700]:", cont[:700].replace("\n", " | "))
        print("tail[-300:]:", cont[-300:].replace("\n", " | "))
        m = re.findall(r"Answer:\s*[A-J].*", cont)
        print("Answer line:", m[-1][:60] if m else "NONE")
    except Exception as e:
        print("ERROR (after retries):", str(e)[:200])
    time.sleep(5)

show("D1  RAW-formatting prefix, cut at end of s62", raw62)
show("D2  RAW prefix cut MID-WORD ('...accurate desc')", midword, expect_start="ription")
print("=" * 90)
print("If D2 PASSES: the harness question is solved; resample_cuts.py gets patched to this")
print("endpoint. Check D1 for: continues the option analysis, emits </think>, has an Answer line.")
