import json, re, statistics

rows = [json.loads(l) for l in open('runs/sweep_items_batball_2026-08-19_1623.jsonl', encoding='utf-8')]

hits = sum(1 for r in rows if re.search(r"1\.00\s+more", r["trace"]))

pos = [r["trace"].find("1.00")/len(r["trace"]) for r in rows if "1.00" in r["trace"]]

print(hits, "/", len(rows), " median position:", round(statistics.median(pos), 3))