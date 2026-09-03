"""
Baseline distribution for ONE underspecified famous-puzzle item, scored by a multi-select option menu.
Saves every sample (prompt, thinking trace, reply, chosen letters) to runs/<NAME>_baseline.jsonl.

Usage: python baseline_levels.py -n 20 --workers 5
"""
import argparse, collections, json, os, re, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

NAME = "batball_underspec_multi"
QUESTION = "A bat and a ball cost $1.10 in total. The bat costs more than the ball. How much does the ball cost?"
OPTIONS = {
    "A": "It is $0.05",
    "B": "It is probably $0.05",
    "C": "I am not sure",
    "E": "There is not enough information, but the answer is most likely $0.05",
    "F": "The answer depends on some other factor",
    "G": "None of the above",
}
PROMPT = (QUESTION + "\n\nChoose every option that applies (you may pick more than one):\n" +
          "\n".join(f"({k}) {v}" for k, v in OPTIONS.items()) +
          "\n\nExplain your reasoning, then end your reply with a single line of the form "
          "\"Answer: X\" where X is one or more option letters separated by commas.")
MODEL = "qwen/qwen3.6-27b"
PROVIDERS = {"order": ["DeepInfra"], "allow_fallbacks": False}

def get_trace_and_reply(msg):
    """Thinking may arrive in a separate field (DeepInfra 'reasoning') or inline with </think>."""
    for field in ("reasoning", "reasoning_content"):
        val = getattr(msg, field, None)
        if val:
            return val, (msg.content or "").strip()
    extra = getattr(msg, "model_extra", None) or {}
    for field in ("reasoning", "reasoning_content"):
        if extra.get(field):
            return extra[field], (msg.content or "").strip()
    text = msg.content or ""
    if "</think>" in text:
        a, b = text.split("</think>", 1); return a.replace("<think>", "").strip(), b.strip()
    return "", text.strip()

def extract_letters(reply):
    m = re.findall(r"Answer:\s*([A-G](?:\s*[,/&and]+\s*[A-G])*)", reply, re.I)
    if not m: return ()
    return tuple(sorted(set(re.findall(r"[A-G]", m[-1].upper()))))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("-n", type=int, default=20)
    ap.add_argument("--workers", type=int, default=5); ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=8000); a = ap.parse_args()
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OpenRouter_API_KEY"])
    Path("runs").mkdir(exist_ok=True); out = Path("runs") / f"{NAME}_baseline.jsonl"; lock = threading.Lock()
    print("=== PROMPT ===\n" + PROMPT + "\n")
    def work(s):
        err = ""
        for attempt in range(4):
            try:
                r = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": PROMPT}],
                    temperature=a.temperature, max_tokens=a.max_tokens, timeout=600,
                    extra_body={"reasoning": {"enabled": True}, "provider": PROVIDERS})
                ch = r.choices[0]; trace, reply = get_trace_and_reply(ch.message)
                if ch.finish_reason is None or not reply: raise RuntimeError("dropped/blank response")
                letters = extract_letters(reply)
                rec = dict(sample=s, letters=list(letters), finish=ch.finish_reason, provider=getattr(r, "provider", None),
                           trace_len=len(trace), prompt=PROMPT, trace=trace, reply=reply,
                           usage=r.usage and r.usage.model_dump())
                with lock, open(out, "a", encoding="utf-8") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                return s, letters, len(trace)
            except Exception as e:
                err = str(e)[:80]; time.sleep(4 * (attempt + 1))
        return s, ("ERR",), err
    counts = collections.Counter(); single = collections.Counter()
    with ThreadPoolExecutor(a.workers) as ex:
        for fut in as_completed([ex.submit(work, s) for s in range(a.n)]):
            s, letters, tl = fut.result(); counts[",".join(letters) or "?"] += 1
            for L in OPTIONS: print(f"{L} {OPTIONS[L][:45]:47s} {single[L]}")
            print(f"sample {s:2d}: {','.join(letters) or '?':10s} trace_len={tl}", flush=True)
    print("\n=== TALLY (answer sets) ===")
    for k, v in counts.most_common(): print(f"{k:12s} {v}")
    print("\n=== per-letter counts ===")
    for L in "ABCDEFG": print(f"{L} {OPTIONS[L][:45]:47s} {single[L]}")
    print(f"\ntraces saved to {out}")

if __name__ == "__main__": main()
