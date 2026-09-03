"""
Truncation-and-resampling for hyp 3.1 — v2, DeepInfra DIRECT raw completions.
(v1 targeted OpenRouter chat prefill; probes 2026-08-23 showed OpenRouter drops/rewraps
thinking prefill on every route. DeepInfra's raw /completions continues the prefix
verbatim — verified by mid-sentence continuation + inline </think>. See plan amendment.)

Design (docs/plan_amendment.md, Amendment 1 — commit BEFORE running):
  Source: runs/sweep_items_batball_2026-08-19_1623.jsonl  (frozen; never modified)
  E-trace s0819_eval0multi0_036: cuts after sentences 60,61,62,63,64,65
  C-trace s0819_eval0multi0_004: cuts after sentences 15,29,44 (Amendment 2 bisection
  of the s0-s58 span) + 58,59,60,61,62,63,64,67,68,69
  Shared cut-0 (empty prefix, open <think>), run FIRST as harness gate:
  |P(E) - 39/44| <= 0.15 or the run aborts.
  n = 25 per prefix, temperature 1.0. Prefix = RAW trace text (original formatting)
  up to the end char-offset of the cut sentence.

Usage:
    python scripts/resample_cuts.py --dry     # build/verify prefixes, no API calls
    python scripts/resample_cuts.py --smoke   # T=0 mid-word mechanism check + 3 eye-check calls
    python scripts/resample_cuts.py --yes     # full run (425 calls, ~$9-10)
    python scripts/resample_cuts.py --yes --resume runs/resample_cuts_<stamp>

Outputs under runs/: .jsonl, _prefixes.json, _log.txt (all failures + per-prefix
attempted/succeeded), _summary.csv (P(C), P(E), distribution per prefix).
"""
import argparse, collections, csv, datetime, hashlib, json, os, re, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "https://api.deepinfra.com/v1/openai"
MODEL = "Qwen/Qwen3.6-27B"   # pinned 2026-08-26 (catalog-resolved unambiguously on 08-25)
SOURCE = Path("runs/sweep_items_batball_2026-08-19_1623.jsonl")
RUNTAG = "rs0823"
TPL = "<|im_start|>user\n{p}<|im_end|>\n<|im_start|>assistant\n<think>\n{pre}"

DESIGN = {
    "e036": ("s0819_eval0multi0_036", [60, 61, 62, 63, 64, 65]),
    "c004": ("s0819_eval0multi0_004", [15, 29, 44, 58, 59, 60, 61, 62, 63, 64, 67, 68, 69]),  # 15/29/44: Amendment 2 bisection
}
N_PER_PREFIX = 25
CUT0_BASELINE_PE = 39 / 44
CUT0_GATE = 0.15
EXPECT = {
    "e036": (253, {63: 'The "most likely" part is not mathematically justified.'}),
    "c004": (366, {60: "However, in the context of riddles,",
                   62: "This is logically the most accurate description."}),
}

def split_sentences(text):
    # VERBATIM reading-pack splitter; indices frozen in the amendment and §5 blanks.
    sents = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = re.split(r'(?<=[.!?:])\s+', line)
        sents.extend(p for p in parts if p.strip())
    return sents

def extract_letters(reply, valid):                 # verbatim from sweep_2x2.py
    m = re.findall(r"Answer:\s*([A-J](?:\s*[,/&and]+\s*[A-J])*)", reply, re.I)
    if not m: return ()
    return tuple(sorted(set(L for L in re.findall(r"[A-J]", m[-1].upper()) if L in valid)))

def sha(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()

def load_sources():
    counts, byid = collections.Counter(), {}
    for line in open(SOURCE, encoding="utf-8"):
        r = json.loads(line)
        counts[r["condition"]] += 1
        byid[f"s0819_{r['condition'].replace('_','')}_{counts[r['condition']]:03d}"] = r
    out = {}
    for short, (rid, cuts) in DESIGN.items():
        r = byid[rid]
        sents = split_sentences(r["trace"])
        n_exp, texts = EXPECT[short]
        assert len(sents) == n_exp, f"{rid}: {len(sents)} sentences, expected {n_exp}"
        for k, frag in texts.items():
            assert sents[k].startswith(frag), f"{rid} s{k} mismatch: {sents[k][:80]}"
        # sentence index -> end offset in the RAW trace (original formatting)
        pos, ends = 0, []
        for s in sents:
            i = r["trace"].find(s, pos)
            assert i >= 0, f"{rid}: sentence not found in raw trace: {s[:60]}"
            pos = i + len(s); ends.append(pos)
        out[short] = dict(rid=rid, rec=r, sents=sents, ends=ends, cuts=cuts)
    a, b = (out[s]["rec"]["prompt"] for s in out)
    assert a == b, "source prompts differ — cut-0 cannot be shared"
    return out

def build_prefixes(src):
    prefixes = {f"{RUNTAG}_cut000": dict(trace="shared", cut=0, prefill="",
                                         source_id=None, n_sents=0, sha=None)}
    for short, d in src.items():
        for k in d["cuts"]:
            text = d["rec"]["trace"][: d["ends"][k]]        # RAW text, original formatting
            prefixes[f"{RUNTAG}_{short}_cut{k:03d}"] = dict(
                trace=short, cut=k, prefill=text, source_id=d["rid"],
                n_sents=k + 1, sha=sha(text))
    return prefixes

def resolve_model(client):
    global MODEL
    if MODEL: return MODEL
    cands = sorted({m.id for m in client.models.list()
                    if "qwen3.6" in m.id.lower() and "27" in m.id})
    assert cands, "no qwen3.6-27b model found in the DeepInfra catalog"
    assert len(cands) == 1, f"ambiguous model slugs, pin MODEL by hand: {cands}"
    MODEL = cands[0]
    return MODEL

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--resume", default=None)
    ap.add_argument("--skip-gate", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=16000)
    a = ap.parse_args()

    src = load_sources()
    prompt = next(iter(src.values()))["rec"]["prompt"]
    options = next(iter(src.values()))["rec"]["options"]
    prefixes = build_prefixes(src)
    total = len(prefixes) * N_PER_PREFIX

    print(f"source {SOURCE}  sha256 {sha(open(SOURCE, encoding='utf-8').read())[:16]}...")
    for pid, p in prefixes.items():
        span = "  (empty) " if not p["prefill"] else f"s0..s{p['cut']:<3d}"
        tail = "(open <think>, fresh thinking)" if not p["prefill"] else "... " + repr(p["prefill"][-60:])
        print(f"  {pid:26s} {span} chars={len(p['prefill']):6d}  {tail}")
    print(f"{len(prefixes)} prefixes x {N_PER_PREFIX} = {total} calls; est ~${total*0.022:.0f} at probe rates")
    if a.dry:
        print("--dry: no API calls made."); return

    from openai import OpenAI
    client = OpenAI(base_url=BASE_URL, api_key=os.environ["DEEPINFRA_API_KEY"])
    model = resolve_model(client)
    print("model:", model)

    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    prefix_path = Path(a.resume) if a.resume else Path("runs") / f"resample_cuts_{stamp}"
    raw_path = Path(str(prefix_path) + ".jsonl")
    log_path = Path(str(prefix_path) + "_log.txt")
    sum_path = Path(str(prefix_path) + "_summary.csv")
    pfx_path = Path(str(prefix_path) + "_prefixes.json")
    Path("runs").mkdir(exist_ok=True)
    json.dump(dict(endpoint=BASE_URL + "/completions", model=model, template=TPL,
                   source=str(SOURCE), source_sha256=sha(open(SOURCE, encoding="utf-8").read()),
                   n_per_prefix=N_PER_PREFIX, temperature=a.temperature, prompt=prompt,
                   prefixes=prefixes),
              open(pfx_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    lock = threading.Lock(); cost = [0.0]
    def log(msg):
        with lock:
            open(log_path, "a", encoding="utf-8").write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")

    done = set()
    if raw_path.exists():
        for line in open(raw_path, encoding="utf-8"):
            try: done.add(json.loads(line)["id"])
            except Exception: pass
        print(f"resume: {len(done)} continuations already on disk")

    def parse_completion(text, prefill):
        """Raw completion = rest-of-thinking + '</think>' + reply. Returns (full_trace, reply, closed)."""
        if "</think>" in text:
            cont, reply = text.split("</think>", 1)
            return prefill + cont, reply.strip(), True
        return prefill + text, "", False

    def work(pid, seq, temperature=None, max_tokens=None):
        rid = f"{pid}_{seq:03d}"
        p = prefixes[pid]
        last_err = "?"
        for attempt in range(5):
            try:
                r = client.completions.create(model=model,
                        prompt=TPL.format(p=prompt, pre=p["prefill"]),
                        temperature=a.temperature if temperature is None else temperature,
                        max_tokens=a.max_tokens if max_tokens is None else max_tokens,
                        timeout=600, stop=["<|im_end|>"])
                ch = r.choices[0]; text = ch.text or ""
                if ch.finish_reason is None or not text.strip(): raise RuntimeError("dropped/blank")
                full_trace, reply, closed = parse_completion(text, p["prefill"])
                letters = extract_letters(reply if closed else text, options)
                u = r.usage and r.usage.model_dump() or {}
                rec = dict(id=rid, prefix_id=pid, trace_arm=p["trace"], cut=p["cut"],
                           source_id=p["source_id"], prefix_sha=p["sha"], seq=seq,
                           letters=list(letters), chosen=[options[L] for L in letters],
                           think_closed=closed, finish=ch.finish_reason,
                           cont_len=len(text), cont_text=text, usage=u)
                with lock:
                    open(raw_path, "a", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False) + "\n")
                    cost[0] += u.get("estimated_cost", 0) or 0
                if not closed: log(f"NOCLOSE {rid}: finish={ch.finish_reason} len={len(text)}")
                return pid, seq, letters, len(text)
            except Exception as e:
                last_err = str(e)[:120]
                log(f"RETRY {rid} attempt {attempt+1}: {last_err}")
                time.sleep(15 * (attempt + 1))
        log(f"FAIL {rid}: {last_err}")
        return pid, seq, ("ERR",), last_err

    tallies = collections.defaultdict(collections.Counter)
    def run_batch(tasks, label):
        with ThreadPoolExecutor(a.workers) as ex:
            futs = [ex.submit(work, *t) for t in tasks]
            for fut in as_completed(futs):
                pid, seq, letters, tl = fut.result()
                key = ",".join(letters) if letters and letters[0] != "ERR" else ("ERR" if letters else "?")
                tallies[pid][key] += 1
                print(f"[{time.strftime('%H:%M:%S')}] {label} {pid} #{seq}: {key:8s} len={tl}  ${cost[0]:.2f}", flush=True)

    if a.smoke:
        # 1) mechanism assertion at T=0: mid-word prefix must complete deterministically
        d = src["c004"]
        mid = d["rec"]["trace"][: d["ends"][62]][:-len("ription.")]
        r = client.completions.create(model=model, prompt=TPL.format(p=prompt, pre=mid),
                temperature=0.0, max_tokens=8, timeout=600, stop=["<|im_end|>"])
        head = (r.choices[0].text or "")
        # A true continuation of "...the most accurate desc" begins in lowercase,
        # completing the word (possibly with off-token-boundary misspellings, e.g.
        # 'rtiption'); a restart begins with a fresh capitalized/structured opening.
        h = head.lstrip()
        restart = any(m in head[:150].lower() for m in
                      ("the user wants", "here's a thinking", "let me analyze", "analyze the user"))
        okc = bool(h) and h[0].islower() and not restart
        print(f"MECHANISM (T=0 mid-word): {'PASS' if okc else 'FAIL'} — continuation starts {repr(head[:20])}")
        if not okc:
            print("Raw continuation NOT verified — stop and report back."); return
        # 2) behavior eye-check at T=1
        run_batch([(f"{RUNTAG}_cut000", 900), (f"{RUNTAG}_e036_cut063", 900), (f"{RUNTAG}_c004_cut062", 900)], "SMOKE")
        for line in open(raw_path, encoding="utf-8"):
            rec = json.loads(line)
            if rec["seq"] == 900:
                print(f"\n--- {rec['id']} letters={rec['letters']} closed={rec['think_closed']} len={rec['cont_len']}")
                print("starts:", rec["cont_text"][:350].replace("\n", " | "))
        print("\nVerify by eye: mid-cut continuations continue the option analysis (no restart).")
        return

    if not a.yes:
        raise SystemExit("refusing full run without --yes (use --dry / --smoke first)")

    gate_pid = f"{RUNTAG}_cut000"
    gate_tasks = [(gate_pid, s) for s in range(N_PER_PREFIX) if f"{gate_pid}_{s:03d}" not in done]
    if gate_tasks: run_batch(gate_tasks, "GATE")
    else:
        for line in open(raw_path, encoding="utf-8"):
            rec = json.loads(line)
            if rec["prefix_id"] == gate_pid and rec["seq"] < 900:
                tallies[gate_pid][",".join(rec["letters"]) or "?"] += 1
    g = tallies[gate_pid]; n_ok = sum(v for k, v in g.items() if k != "ERR")
    pE = (g.get("E", 0) / n_ok) if n_ok else 0.0
    gate_ok = abs(pE - CUT0_BASELINE_PE) <= CUT0_GATE
    msg = (f"CUT-0 GATE: P(E)={pE:.3f} vs baseline {CUT0_BASELINE_PE:.3f} "
           f"(±{CUT0_GATE}) -> {'PASS' if gate_ok else 'FAIL'}  [{dict(g)}]")
    print(msg); log(msg)
    if not gate_ok and not a.skip_gate:
        raise SystemExit("cut-0 gate FAILED — endpoint does not reproduce baseline; aborting before spend.")

    tasks = [(pid, s) for pid in prefixes if pid != gate_pid
             for s in range(N_PER_PREFIX) if f"{pid}_{s:03d}" not in done]
    print(f"{len(tasks)} calls remaining -> {raw_path}")
    run_batch(tasks, "RUN")

    per = collections.defaultdict(collections.Counter)
    for line in open(raw_path, encoding="utf-8"):
        rec = json.loads(line)
        if rec["seq"] >= 900: continue
        per[rec["prefix_id"]][",".join(rec["letters"]) or "?"] += 1
    rows = []
    for pid, p in prefixes.items():
        c = per[pid]; ok = sum(c.values()); err = tallies[pid].get("ERR", 0)
        pC = sum(v for k, v in c.items() if "C" in k.split(",")) / ok if ok else None
        pE_ = c.get("E", 0) / ok if ok else None
        rows.append(dict(prefix_id=pid, trace=p["trace"], cut=p["cut"],
                         attempted=ok + err, succeeded=ok, err=err,
                         p_C=None if pC is None else round(pC, 3),
                         p_E=None if pE_ is None else round(pE_, 3),
                         distribution=json.dumps(dict(c.most_common()))))
        log(f"ACCOUNT {pid}: attempted={ok+err} succeeded={ok} err={err}")
    with open(sum_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    short = sum(1 for r_ in rows if r_["succeeded"] < N_PER_PREFIX)
    log(f"DONE cost=${cost[0]:.2f}; prefixes short of n={N_PER_PREFIX}: {short}")
    print(f"\ndone. ${cost[0]:.2f}. raw={raw_path} summary={sum_path} log={log_path}")
    if short: print(f"WARNING: {short} prefixes below n={N_PER_PREFIX} — rerun with --resume to top up.")

if __name__ == "__main__": main()
