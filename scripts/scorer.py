#!/usr/bin/env python3
"""scorer.py -- the archived scorer, verbatim (pre-registration stage one, Section 3 item 7;
pipeline v2, Section 5 item 5).

extract_letters is copied character for character from
archive/decided-mid-thought/scripts/sweep_2x2.py (also in resample_cuts.py of the archived
study).  score() applies it as the archived resampling script did: to the reply after the first
</think> tag when the tag is present, to the whole text otherwise; exactly one letter is the
answer, no letter or several letters is "?" (kept in the denominator).

archived_table() recomputes the per-prefix table of the archived run
(runs/resample_cuts_2026-08-25_1503_summary.csv) from its raw records with the archived
formulas (p_C counts every combination containing C, p_E the single letter E, as that script
did); the module test scripts/tests/test_scorer.py requires it to be identical.  Standard
library only.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict

VALID = "ABCDEF"
THINK_END_TAG = "</think>"


def extract_letters(reply, valid):                 # verbatim from sweep_2x2.py
    m = re.findall(r"Answer:\s*([A-J](?:\s*[,/&and]+\s*[A-J])*)", reply, re.I)
    if not m: return ()
    return tuple(sorted(set(L for L in re.findall(r"[A-J]", m[-1].upper()) if L in valid)))


def split_reply(text: str) -> tuple[str, str, bool]:
    """(thinking part, reply after the first </think> stripped, closed?).  Without the tag the
    whole text is the thinking part and the reply is empty."""
    if THINK_END_TAG in text:
        cont, reply = text.split(THINK_END_TAG, 1)
        return cont, reply.strip(), True
    return text, "", False


def score(text: str, valid: str = VALID) -> dict:
    """{"letters": [...], "answer": one letter or "?", "think_closed": bool} for one completion
    (pre-registration 3.7)."""
    _, reply, closed = split_reply(text)
    letters = list(extract_letters(reply if closed else text, valid))
    return {"letters": letters, "answer": letters[0] if len(letters) == 1 else "?", "think_closed": closed}


def archived_table(records: list[dict], valid: str = VALID, order: list[str] | None = None) -> list[dict]:
    """The archived summary rows (prefix_id, trace, cut, attempted, succeeded, err, p_C, p_E,
    distribution) recomputed from raw archived records with the archived formulas."""
    per: dict[str, Counter] = defaultdict(Counter)
    meta: dict[str, tuple[str, int]] = {}
    for r in records:
        if r.get("seq", 0) >= 900:
            continue
        letters = extract_letters(split_reply(r["cont_text"])[1] if THINK_END_TAG in r["cont_text"] else r["cont_text"], valid)
        per[r["prefix_id"]][",".join(letters) or "?"] += 1
        meta.setdefault(r["prefix_id"], (r["trace_arm"], r["cut"]))
    rows = []
    for pid in (order or list(per)):
        c = per[pid]
        ok = sum(c.values())
        p_c = sum(v for k, v in c.items() if "C" in k.split(",")) / ok if ok else None
        p_e = c.get("E", 0) / ok if ok else None
        rows.append({"prefix_id": pid, "trace": meta[pid][0], "cut": meta[pid][1], "attempted": ok, "succeeded": ok, "err": 0,
                     "p_C": None if p_c is None else round(p_c, 3), "p_E": None if p_e is None else round(p_e, 3),
                     "distribution": json.dumps(dict(c.most_common()))})
    return rows
