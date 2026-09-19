#!/usr/bin/env python3
"""s5_rescore.py -- the strict reading of the answer letter, and the registered analysis rerun on it.

Why.  The scorer of pre-registration stage one, Section 3 item 7 (scripts/scorer.py, the archived
`extract_letters`) has two defects on the stage-one run (docs/shared/2026-09-19_scorer_audit_v1.md):
it misses an answer written "Answer: (C)", and in a continuation that hit the token cap before it
closed its thinking it scans the thinking text and reads the first letter of ordinary words
("Answer: Cannot be determined" -> C).  Decision P6 (Kian, 2026-09-19): the strict reading is
canonical; the registered reading and the archived v2.1 reading are reported next to it.  This is a
departure from the registration and is logged in the run folder's DEPARTURES.md.

The strict reading.  A continuation has an answer only if it finished: finish == "stop" and its
thinking is closed.  The reply is the text after the first </think> (the whole text when the tag is
absent, as in the no-think condition).  The answer is read from the LAST NONBLANK LINE of the reply,
which must contain "Answer:".  After Markdown emphasis and backticks are removed, the text after
"Answer:" must be one of:
  (a) one option letter A-F, optionally in parentheses or brackets, optionally followed by . or !
      ("Answer: C", "Answer: (C)", "**Answer:** C.", "Therefore, Answer: C.");
  (b) one option letter followed by that option's own text ("Answer: (E) The question is not well posed.");
  (c) the text of exactly one option, without a letter ("Answer: The question is not well posed").
Anything else is "?", and so is every continuation that did not finish.  "?" stays in the denominator.
On the stage-one run forms (b) and (c) do not occur; the reading then equals the rule of Kian's own
check (scripts/result_verification.py) on all 625 records.

What it writes (nothing of the registered run is touched).  --out, default <run>_strict next to the run:
  continuations.jsonl   every record of the run with `letters` and `answer` replaced by the strict
                        reading, the registered values kept as `letters_v1` and `answer_v1`, `scorer`
                        and `score_reason` added, and `cont_text` and `prompt` replaced by their sha256
                        (the texts stay in the registered file; the analysis needs neither)
  pcut.csv              the run's pcut.csv with the counts, p_hat, the Wilson interval and `stopped`
                        recomputed; every other column copied
  rescore_changes.csv   one row per record whose answer changed
  rescore_summary.json  counts per cut under both readings, the first all-target cut per trace under
                        both, and the checks made
  README.md             what the folder is
and then, unless --no-analysis, the registered analysis (scripts/s4_analyze.py, unchanged) run on the
derived folder with the run's own judge folder: the mediation and transition tables, stage1_summary.md
and the figures figures/<out folder name>_<trace>_*.png.  The transition tables use no letters, so they
must come out identical to the registered ones; rescore_summary.json records that comparison.

  python scripts/s5_rescore.py --run runs/experiments/resample_blocks_<stamp>/ [--out <dir>] [--judge <dir>] [--no-analysis]

Standard library only for the rescoring; the analysis needs numpy and matplotlib as before.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stats_utils as ST  # noqa: E402

SCORER_NAME = "strict_v1"
LETTERS = "ABCDEF"
A_T = {"c004": "C", "e036": "E"}
THINK_END_TAG = "</think>"
OPTIONS = {"A": "it is $0.05", "B": "it is probably $0.05",
           "C": "there is not enough information, but the answer is most likely $0.05",
           "D": "i am not sure", "E": "the question is not well posed", "F": "none of the above"}

_ANSWER = re.compile(r"answer\s*:\s*(.*)$", re.I)
_BARE = re.compile(r"^[\(\[]?\s*([A-F])\s*[\)\]]?\s*[.!]?$", re.I)
_LETTER_THEN_TEXT = re.compile(r"^[\(\[]?\s*([A-F])\s*[\)\]]?\s*[.:,\-\u2013\u2014]?\s+(\S.*)$", re.I)


def _norm(s: str) -> str:
    s = s.lower().replace("\u201c", '"').replace("\u201d", '"').replace("\u2019", "'").replace("\\$", "$")
    s = re.sub(r"\s+", " ", s).strip().strip('"').strip("'").strip()
    return s.rstrip(".!").strip()


def reply_of(cont_text: str) -> str:
    """The reply: the text after the first </think>, or the whole text when the tag is absent."""
    return cont_text.split(THINK_END_TAG, 1)[1] if THINK_END_TAG in cont_text else cont_text


def last_nonblank_line(text: str) -> str:
    lines = [l for l in text.splitlines() if l.strip()]
    return lines[-1].strip() if lines else ""


def read_answer_line(line: str) -> tuple[str, str]:
    """(answer, reason) for one line; the answer is a letter A-F or "?"."""
    clean = re.sub(r"[*_`]", "", line).strip()
    m = _ANSWER.search(clean)
    if not m:
        return "?", "last line is not an answer line"
    tail = m.group(1).strip()
    b = _BARE.match(tail)
    if b:
        return b.group(1).upper(), "letter"
    t = _LETTER_THEN_TEXT.match(tail)
    if t and _norm(t.group(2)) == OPTIONS[t.group(1).upper()]:
        return t.group(1).upper(), "letter with its option text"
    hits = [L for L, text in OPTIONS.items() if _norm(tail) == text]
    if len(hits) == 1:
        return hits[0], "option text"
    return "?", "answer line not readable"


def strict_score(cont_text: str, finish: str, think_closed: bool) -> dict:
    """{"answer", "letters", "reason", "line"} under the strict reading."""
    if finish != "stop" or not think_closed:
        return {"answer": "?", "letters": [], "reason": "did not finish", "line": ""}
    line = last_nonblank_line(reply_of(cont_text))
    answer, reason = read_answer_line(line)
    return {"answer": answer, "letters": [] if answer == "?" else [answer], "reason": reason, "line": line}


# ----------------------------------------------------------------------------
# files
# ----------------------------------------------------------------------------

def read_jsonl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def cut_name(rec: dict) -> str:
    if rec["condition"] != "cut":
        return rec["condition"]
    return f"{rec['trace_arm']}_B{int(rec['block']):02d}"


def v1_answer(rec: dict) -> str:
    letters = rec.get("letters") or []
    return letters[0] if len(letters) == 1 else "?"


def rescore_records(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """(derived records, change rows)."""
    out, changes = [], []
    for r in records:
        sc = strict_score(r["cont_text"], r.get("finish"), bool(r.get("think_closed")))
        old = v1_answer(r)
        d = {k: v for k, v in r.items() if k not in ("cont_text", "prompt")}
        d.update({"letters_v1": r.get("letters") or [], "answer_v1": old, "letters": sc["letters"], "answer": sc["answer"],
                  "scorer": SCORER_NAME, "score_reason": sc["reason"], "cont_text_sha256": sha256(r["cont_text"]),
                  "prompt_sha256": sha256(r.get("prompt") or "")})
        out.append(d)
        if old != sc["answer"]:
            changes.append({"id": r["id"], "cut": cut_name(r), "finish": r.get("finish"), "think_closed": bool(r.get("think_closed")),
                            "letters_v1": ",".join(r.get("letters") or []), "answer_v1": old, "answer_strict": sc["answer"],
                            "reason": sc["reason"], "last_line": sc["line"][:160]})
    return out, changes


def rescore_pcut(rows: list[dict], derived: list[dict]) -> list[dict]:
    by_prefix: dict[str, list[str]] = defaultdict(list)
    for d in derived:
        by_prefix[d["prefix_id"]].append(d["answer"])
    out = []
    for row in rows:
        answers = by_prefix[row["prefix_id"]]
        n = int(row["n"])
        if len(answers) != n:
            raise SystemExit(f"{row['prefix_id']}: {len(answers)} records for n = {n}")
        c = Counter(answers)
        new = dict(row)
        for L in LETTERS:
            new[f"count_{L}"] = c.get(L, 0)
        new["count_unresolved"] = c.get("?", 0)
        new["count_other"] = n - c.get("?", 0) - c.get("C", 0) - c.get("E", 0)
        target = A_T.get(row["trace_id"]) if row["condition"] == "cut" else None
        if target:
            k = c.get(target, 0)
            lo, hi = ST.wilson(k, n)
            new.update({"p_hat": round(k / n, 4), "ci_low": round(lo, 4), "ci_high": round(hi, 4), "stopped": bool(n and k == n)})
        out.append(new)
    return out


def first_all_target(pcut_rows: list[dict]) -> dict:
    res = {}
    for tid, letter in A_T.items():
        cuts = sorted((int(r["m"]), int(r[f"count_{letter}"]), int(r["n"])) for r in pcut_rows if r["trace_id"] == tid and r["condition"] == "cut")
        res[tid] = next((m for m, k, n in cuts if k == n), None)
    return res


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)


README = """# {name}

Derived from `{run}` by `scripts/s5_rescore.py` on {stamp}. Nothing in the registered run folder was changed.

This folder holds the stage-one run read with the strict rule (decision P6, 2026-09-19; departure from
pre-registration 3.7, logged in the run's DEPARTURES.md; reasons in docs/shared/2026-09-19_scorer_audit_v1.md):
a continuation has an answer only if it finished, and the answer is the letter on the last line of its reply.

- `continuations.jsonl`: the run's records with `letters` and `answer` under the strict rule, the registered
  values kept as `letters_v1` and `answer_v1`. The continuation texts are not repeated here; `cont_text_sha256`
  ties each record to its text in the registered file.
- `pcut.csv`: the run's table with the counts, P-hat, its interval and `stopped` recomputed.
- `rescore_changes.csv`: the {n_changed} records whose answer changed. `rescore_summary.json`: counts under both
  readings and the checks made.
- The remaining tables, `stage1_summary.md` and the figures `figures/{name}_*.png` are the registered analysis
  (`scripts/s4_analyze.py`, unchanged) run on this folder with the run's own judge folder. The transition tables
  use no letters and are identical to the registered ones.
"""


def rescore_run(run_dir: Path, out_dir: Path, log=print) -> dict:
    run_dir, out_dir = Path(run_dir), Path(out_dir)
    if out_dir.resolve() == run_dir.resolve():
        raise SystemExit("--out must not be the registered run folder")
    records = read_jsonl(run_dir / "continuations.jsonl")
    with open(run_dir / "pcut.csv", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fields = list(reader.fieldnames)
        pcut_rows = list(reader)
    ids = [r["id"] for r in records]
    if len(set(ids)) != len(ids):
        raise SystemExit("duplicate record ids in continuations.jsonl")
    out_dir.mkdir(parents=True, exist_ok=True)
    derived, changes = rescore_records(records)
    new_pcut = rescore_pcut(pcut_rows, derived)
    with open(out_dir / "continuations.jsonl", "w", encoding="utf-8", newline="\n") as fh:
        for d in derived:
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")
    write_csv(out_dir / "pcut.csv", new_pcut, fields)
    write_csv(out_dir / "rescore_changes.csv", changes,
              ["id", "cut", "finish", "think_closed", "letters_v1", "answer_v1", "answer_strict", "reason", "last_line"])

    per_cut = {}
    for old, new in zip(pcut_rows, new_pcut):
        per_cut[old["prefix_id"]] = {"n": int(old["n"]),
                                     "registered": {k: int(old[f"count_{k}"]) for k in LETTERS} | {"?": int(old["count_unresolved"])},
                                     "strict": {k: int(new[f"count_{k}"]) for k in LETTERS} | {"?": int(new["count_unresolved"])}}
    finished = [d for d, r in zip(derived, records) if r.get("finish") == "stop" and r.get("think_closed")]
    summary = {"run": str(run_dir), "out": str(out_dir), "scorer": SCORER_NAME, "generated": datetime.now().isoformat(timespec="seconds"),
               "records": len(records), "changed": len(changes),
               "changed_by_kind": dict(Counter(f"{c['answer_v1']} -> {c['answer_strict']}" if c["answer_strict"] != "?" else "letter -> ?" for c in changes)),
               "finished": len(finished), "finished_without_answer": sum(1 for d in finished if d["answer"] == "?"),
               "unfinished": len(records) - len(finished),
               "answer_forms": dict(Counter(d["score_reason"] for d in derived)),
               "first_all_target_cut": {"registered": first_all_target(pcut_rows), "strict": first_all_target(new_pcut)},
               "per_cut": per_cut}
    (out_dir / "README.md").write_text(README.format(name=out_dir.name, run=run_dir.as_posix(), stamp=summary["generated"][:10],
                                                     n_changed=len(changes)), encoding="utf-8")
    (out_dir / "rescore_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    log(f"rescored {len(records)} records: {len(changes)} answers changed; first all-target cut {summary['first_all_target_cut']}")
    return summary


def _norm_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def compare_transition_tables(run_dir: Path, out_dir: Path) -> dict:
    res = {}
    for p in sorted(Path(out_dir).glob("transition_*.csv")):
        ref = Path(run_dir) / p.name
        res[p.name] = (_norm_bytes(p) == _norm_bytes(ref)) if ref.exists() else None
    return res


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="The strict reading of the answer letter (decision P6) and the registered analysis rerun on it.")
    ap.add_argument("--run", required=True, help="the registered run folder (read only)")
    ap.add_argument("--out", help="derived folder; default: <run>_strict next to the run")
    ap.add_argument("--judge", help="judge folder of the run; default: the run's newest judge_* folder")
    ap.add_argument("--no-analysis", action="store_true", help="rescore only; do not run s4_analyze")
    ap.add_argument("--draws", type=int, default=10000)
    ap.add_argument("--perms", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)
    run_dir = Path(args.run)
    out_dir = Path(args.out) if args.out else run_dir.parent / (run_dir.name.rstrip("/\\") + "_strict")
    summary = rescore_run(run_dir, out_dir)
    if not args.no_analysis:
        import s4_analyze as S4  # imported late: needs numpy and matplotlib
        judge = Path(args.judge) if args.judge else next(iter(sorted(run_dir.glob("judge_*"), reverse=True)), None)
        S4.analyze(out_dir, judge, out_dir, draws=args.draws, perms=args.perms, seed=args.seed)
        same = compare_transition_tables(run_dir, out_dir)
        summary["transition_tables_identical_to_registered"] = same
        (out_dir / "rescore_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print("transition tables identical to the registered ones:", same)
        if not all(v for v in same.values()):
            print("WARNING: a transition table differs from the registered one; the letters should not enter it")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
