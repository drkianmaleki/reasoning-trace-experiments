"""
make_id_sidecar.py -- generate a read-only ID sidecar for a frozen sweep jsonl.

Assigns each record a stable, self-describing ID:
    s0819_{condition-with-underscore-removed}_{seq:03d}
where seq is the 1-indexed order of appearance WITHIN its condition cell,
i.e. line order in the jsonl. The jsonl itself is never modified.

Output CSV columns: id, jsonl_line (1-indexed), condition, seq_in_condition, letters

Re-running on the same file always produces the identical mapping.
"""
import json, csv, sys, collections

SRC = sys.argv[1] if len(sys.argv) > 1 else "runs/sweep_items_batball_2026-08-19_1623.jsonl"
DST = SRC.replace(".jsonl", "_ids.csv")
RUNTAG = "s0819"

counts = collections.Counter()
rows = []
with open(SRC, encoding="utf-8") as f:
    for lineno, line in enumerate(f, start=1):
        r = json.loads(line)
        cond = r["condition"]
        counts[cond] += 1
        seq = counts[cond]
        letters = r.get("letters")
        letters = ",".join(letters) if isinstance(letters, list) else ("" if letters is None else str(letters))
        rows.append({
            "id": f"{RUNTAG}_{cond.replace('_','')}_{seq:03d}",
            "jsonl_line": lineno,
            "condition": cond,
            "seq_in_condition": seq,
            "letters": letters,
        })

with open(DST, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["id","jsonl_line","condition","seq_in_condition","letters"])
    w.writeheader()
    w.writerows(rows)

print(f"wrote {DST}: {len(rows)} ids")
for cond in sorted(counts):
    print(f"  {cond}: {counts[cond]}")
