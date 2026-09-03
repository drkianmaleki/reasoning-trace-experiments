import json, re
for r in map(json.loads, open('runs/resample_cuts_2026-08-25_1503_rescored.jsonl', encoding='utf-8')):
    if r["letters"] in (["A"], ["A","C"]):
        seg = r["cont_text"].split("</think>",1)[1] if r["think_closed"] and "</think>" in r["cont_text"] else r["cont_text"]
        line = re.findall(r"Answer:[^\n]*", seg, re.I)[-1]
        print(r["id"], r["letters"], "->", line[:90])