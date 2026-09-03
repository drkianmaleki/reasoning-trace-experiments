"""
2x2 sweep for ONE (or more) CSV-defined items: eval-frame on/off x multi-select on/off.

CSV format (header row required, options separated by '>'):
  Question part 1 (eval-statement),Question part 2 (main question),Options

Usage:
    python sweep_2x2.py items.csv --smoke          # 1 sample per condition, first item only
    python sweep_2x2.py items.csv -n 50            # full run: 4 conditions x n per item
    python sweep_2x2.py items.csv -n 50 --resume runs/sweep_batball_2026-08-20_1432   # continue

Outputs (per run, under runs/):
  sweep_<stem>_<timestamp>.jsonl      every sample: condition, letters, option texts, trace, reply
  sweep_<stem>_<timestamp>_summary.csv  one row per (item, condition) with the answer-set distribution
"""
import argparse, collections, csv, datetime, json, os, re, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

MODEL = "qwen/qwen3.6-27b"
PROVIDER_ROUTING = {"order": ["DeepInfra"], "allow_fallbacks": False}
LETTERS = "ABCDEFGHIJ"

MULTI_INSTR = ("Choose every option that applies (you may pick more than one):\n{opts}\n\n"
               "Explain your reasoning, then end your reply with a single line of the form "
               "\"Answer: X\" where X is one or more option letters separated by commas.")
SINGLE_INSTR = ("Choose the single best option:\n{opts}\n\n"
                "Explain your reasoning, then end your reply with a single line of the form "
                "\"Answer: X\" where X is exactly one option letter.")

def load_items(path):
    items = []
    with open(path, encoding="utf-8-sig") as f:
        for i, row in enumerate(csv.reader(f)):
            if i == 0 and "eval" in row[0].lower(): continue   # header
            if not row or not any(c.strip() for c in row): continue
            frame, question, opts = row[0].strip(), row[1].strip(), [o.strip() for o in row[2].split(">") if o.strip()]
            items.append(dict(idx=len(items), frame=frame, question=question,
                              options={LETTERS[k]: o for k, o in enumerate(opts)}))
    return items

def build_prompt(item, eval_on, multi_on):
    opts = "\n".join(f"({k}) {v}" for k, v in item["options"].items())
    instr = (MULTI_INSTR if multi_on else SINGLE_INSTR).format(opts=opts)
    head = (item["frame"] + "\n\n") if eval_on and item["frame"] else ""
    return f"{head}{item['question']}\n\n{instr}"

def get_trace_and_reply(msg):
    for field in ("reasoning", "reasoning_content"):
        val = getattr(msg, field, None) or (getattr(msg, "model_extra", None) or {}).get(field)
        if val: return val, (msg.content or "").strip()
    text = msg.content or ""
    if "</think>" in text:
        a, b = text.split("</think>", 1); return a.replace("<think>", "").strip(), b.strip()
    return "", text.strip()

def extract_letters(reply, valid):
    m = re.findall(r"Answer:\s*([A-J](?:\s*[,/&and]+\s*[A-J])*)", reply, re.I)
    if not m: return ()
    return tuple(sorted(set(L for L in re.findall(r"[A-J]", m[-1].upper()) if L in valid)))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("items_csv")
    ap.add_argument("-n", type=int, default=50)
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--smoke", action="store_true", help="1 sample per condition, first item only")
    ap.add_argument("--resume", default=None, help="path prefix of an earlier run to continue")
    a = ap.parse_args()

    items = load_items(a.items_csv)
    if not items: raise SystemExit("no items found in CSV")
    if a.smoke: items, n = items[:1], 1
    else: n = a.n

    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    stem = Path(a.items_csv).stem
    Path("runs").mkdir(exist_ok=True)
    prefix = Path(a.resume) if a.resume else Path("runs") / f"sweep_{stem}_{stamp}"
    raw_path = Path(str(prefix) + ".jsonl"); sum_path = Path(str(prefix) + "_summary.csv")

    done = set()
    if raw_path.exists():
        for line in open(raw_path, encoding="utf-8"):
            try:
                r = json.loads(line); done.add((r["item_idx"], r["condition"], r["sample"]))
            except Exception: pass
        print(f"resume: {len(done)} samples already on disk")

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OpenRouter_API_KEY"])
    lock = threading.Lock(); cost = [0.0]

    conditions = [("eval1_multi1", True, True), ("eval1_multi0", True, False),
                  ("eval0_multi1", False, True), ("eval0_multi0", False, False)]

    def work(item, cond, eval_on, multi_on, s):
        prompt = build_prompt(item, eval_on, multi_on)
        for attempt in range(4):
            try:
                r = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}],
                    temperature=a.temperature, max_tokens=a.max_tokens, timeout=600,
                    extra_body={"reasoning": {"enabled": True}, "provider": PROVIDER_ROUTING})
                ch = r.choices[0]; trace, reply = get_trace_and_reply(ch.message)
                if ch.finish_reason is None or not reply.strip(): raise RuntimeError("dropped/blank")
                letters = extract_letters(reply, item["options"])
                u = r.usage and r.usage.model_dump() or {}
                rec = dict(item_idx=item["idx"], condition=cond, sample=s, letters=list(letters),
                           chosen=[item["options"][L] for L in letters],
                           eval_frame=eval_on, multi=multi_on, finish=ch.finish_reason,
                           provider=getattr(r, "provider", None), trace_len=len(trace),
                           options=item["options"], prompt=prompt, trace=trace, reply=reply, usage=u)
                with lock:
                    open(raw_path, "a", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False) + "\n")
                    cost[0] += u.get("cost", 0) or 0
                return cond, s, letters, len(trace)
            except Exception as e:
                err = str(e)[:90]; time.sleep(4 * (attempt + 1))
        return cond, s, ("ERR",), err

    t0 = time.time()
    tasks = [(item, cond, e, m, s) for item in items for cond, e, m in conditions
             for s in range(n) if (item["idx"], cond, s) not in done]
    print(f"{len(tasks)} calls to make -> {raw_path}")
    tallies = collections.defaultdict(collections.Counter)
    with ThreadPoolExecutor(a.workers) as ex:
        futs = [ex.submit(work, *t) for t in tasks]
        for fut in as_completed(futs):
            cond, s, letters, tl = fut.result()
            key = ",".join(letters) if letters and letters[0] != "ERR" else ("ERR" if letters and letters[0]=="ERR" else "?")
            tallies[cond][key] += 1
            print(f"[{time.strftime('%H:%M:%S')}] {cond} s{s}: {key:10s} trace_len={tl}  ${cost[0]:.2f}", flush=True)
    # replay resumed samples into tallies
    if done:
        for line in open(raw_path, encoding="utf-8"):
            r = json.loads(line)
            if (r["item_idx"], r["condition"], r["sample"]) in done:
                tallies[r["condition"]][",".join(r["letters"]) or "?"] += 1

    print("\n=== SUMMARY ===")
    rows = []
    for item in items:
        for cond, _, _ in conditions:
            c = tallies[cond]
            print(f"item {item['idx']} {cond}: {dict(c.most_common())}")
            rows.append(dict(item_idx=item["idx"], condition=cond, n=sum(c.values()),
                             distribution=json.dumps(dict(c.most_common())),
                             options=json.dumps(item["options"])))
    with open(sum_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    print(f"\ndone in {(time.time()-t0)/60:.1f} min, ${cost[0]:.2f}. raw={raw_path} summary={sum_path}")

if __name__ == "__main__": main()
