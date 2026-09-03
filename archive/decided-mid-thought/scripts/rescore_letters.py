"""
rescore_letters.py — the single pre-registered scoring revision (log_2026-08-22 §5:
"regex is revised once at most"), designed 2026-08-29 after the A2 hand-check
(seed 20260830; agreement 19/20) and finalized after human validation of every
changed record.

Defects in the original extract_letters (sweep_2x2.py / resample_cuts.py):
  1. 'Answer: (C)' / 'Answer: **C**' scored as NONE (letter not directly after colon).
  2. Sub-word matches: 'Answer: Ball' -> B, etc.; produced every recorded B and
     most D,E draws (artifacts, withdrawn).
  3. Answers given as option TEXT, e.g. Answer: "The question is not well posed."
     scored as NONE (caught by the author during flip validation).

Revised scorer (v2.1):
  segment = reply if thinking closed else full text (unchanged);
  take the LAST line starting 'Answer:';
  (a) extract standalone UPPERCASE letters A-F from that line:
      (?<![A-Za-z])([A-F])(?![A-Za-z]);
  (b) if none: match the line against the six option texts (normalized,
      case-insensitive); exactly one hit -> that letter; zero or several -> NONE.

Writes *_rescored.jsonl with letters replaced; original kept as letters_v1;
raw text untouched. Sweep: zero changes (all registered sweep numbers stand).
"""
import json, re

ANS_LINE = re.compile(r"Answer:[^\n]*", re.I)
LETTER   = re.compile(r"(?<![A-Za-z])([A-F])(?![A-Za-z])")
OPTIONS  = {"A": "it is $0.05", "B": "it is probably $0.05",
            "C": "there is not enough information, but the answer is most likely $0.05",
            "D": "i am not sure", "E": "the question is not well posed",
            "F": "none of the above"}

def _norm(s):
    s = s.lower().replace("\u201c", '"').replace("\u201d", '"').replace("\\$", "$")
    return re.sub(r"\s+", " ", s)

def score_v21(segment):
    lines = ANS_LINE.findall(segment)
    if not lines:
        return []
    last = lines[-1]
    letters = sorted(set(LETTER.findall(last)))
    if letters:
        return letters
    ln = _norm(last)
    hits = [L for L, t in OPTIONS.items() if t in ln]
    return hits if len(hits) == 1 else []

def seg_resample(r):
    t = r["cont_text"]
    return t.split("</think>", 1)[1] if r["think_closed"] and "</think>" in t else t

if __name__ == "__main__":
    for src, segfn in [("runs/resample_cuts_2026-08-25_1503.jsonl", seg_resample),
                       ("runs/sweep_items_batball_2026-08-19_1623.jsonl", lambda r: r["reply"])]:
        dst = src.replace(".jsonl", "_rescored.jsonl")
        n_changed = 0
        with open(dst, "w", encoding="utf-8") as f:
            for line in open(src, encoding="utf-8"):
                r = json.loads(line)
                new = score_v21(segfn(r))
                if new != list(r["letters"]):
                    n_changed += 1
                r["letters_v1"] = r["letters"]
                r["letters"] = new
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"{dst}: {n_changed} records changed vs original scoring")
