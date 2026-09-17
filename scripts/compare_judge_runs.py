#!/usr/bin/env python3
"""compare_judge_runs.py -- the judge comparisons.

Reads every judge run (runs/experiments/judge_source_*), recomputes the agreement against the
reviewed listing per trace and pooled from each run's labels_source_judge.jsonl, takes blocks
and nodes from blocks_source_judge.jsonl and attempts/cost/thinking tokens from _log.txt, and
writes runs/experiments/judge_compare_2x2_<stamp>/comparison.md with
  (i)   the 2x2 (prompt v1/v2 x Haiku/Sonnet, thinking off) per trace and pooled;
  (ii)  the six confusion classes per 2x2 cell;
  (iii) the ten most frequent Level 2 confusions of each 2x2 cell;
  (iv)  the structural metrics (scripts/structural_agreement.py) for every run, per trace and
        pooled, also written as structural_<run>.csv;
  (v)   the reasoning curve over the Sonnet x v2 cells (none, leaked, low r1, low r2, medium):
        thinking tokens per sentence, attempts, sentence-level exact-match and kappa at the three
        levels, block F1, next-node agreement, node F1, Level 1 share of the disagreement, cost
        per trace, and the projected judge-side cost per collection at batch prices.
Usage: python scripts/compare_judge_runs.py [--run DIR ...] [--out DIR]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import derivation as D  # noqa: E402
import s1_judge as S  # noqa: E402
import structural_agreement as SA  # noqa: E402

REPO = S.REPO
REVIEWED = {"c004": {"blocks": 46, "nodes": 193}, "e036": {"blocks": 37, "nodes": 146}}
CELL_ORDER = [("haiku", "v1"), ("haiku", "v2"), ("sonnet", "v1"), ("sonnet", "v2")]
# Cost projection (same arithmetic as the report of 2026-09-17): Sonnet batch prices, thinking
# billed as output, the system prompt (8,109 tokens as counted by the API) cached once and read
# per document; collections as given by Kian.
BATCH = {"in": 1.0, "out": 5.0, "cr": 0.10, "cw": 1.25}  # USD per million tokens
SYS_TOKENS = 8109
SONNET_SINGLE_PASS_INPUT = 5635 + 9403  # uncached input of one clean pass over e036 + c004 (Sonnet tokenizer)
COLLECTIONS = [  # (name, docs, text tokens, prefix tokens, sentences)
    ("sweep44", 44, 187_000, 0, 15_295),
    ("archived500", 500, 3_550_000, 424_000 * 1.6, 240_620),
    ("new continuations (n = 40)", 720, 5_900_000, 720 * ((4740 + 2890) / 4) * 1.6, 5_900_000 / 23.91),
]


def cell_of(config: dict) -> tuple[str, str]:
    """(model, prompt version); runs with a thinking mode other than off get a suffixed model key
    ("sonnet+thinklow") so that they never overwrite a 2x2 cell."""
    model_key = config.get("model_key") or ("sonnet" if "sonnet" in config.get("model", "") else "haiku")
    version = config.get("prompt_version") or config.get("prompt", "judge_prompt_v1.md").replace("judge_prompt_", "").replace(".md", "")
    mode = config.get("thinking_mode", "off")
    if mode and mode != "off":
        model_key = f"{model_key}+think{mode}"
    return model_key, version


def load_run(run_dir: Path) -> dict:
    config = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))
    labels = SA.judge_labels_from_file(run_dir / "labels_source_judge.jsonl")
    blocks = {}
    with open(run_dir / "blocks_source_judge.jsonl", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            blocks[r["trace_id"]] = {"blocks": len(r["blocks"]), "nodes": len(r["nodes"])}
    log = {}
    for line in (run_dir / "_log.txt").read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        f = line.split("\t")
        log[f[0]] = {"attempts": int(f[1]), "valid": f[2] == "True", "input": int(f[3]), "cache_read": int(f[4]),
                     "cache_write": int(f[5]), "output": int(f[6]), "cost": float(f[7]),
                     "thinking": int(f[9]) if len(f) > 9 else 0, "leaks": f[10] if len(f) > 10 else ""}
    mode = config.get("thinking_mode", "off")
    repeat = ""
    for part in run_dir.name.split("_"):
        if len(part) >= 2 and part[0] == "r" and part[1:].isdigit():
            repeat = f" r{part[1:]}"
    label = mode
    if mode == "off" and any(v["attempts"] > 1 for v in log.values()):
        label = "leaked"
    return {"dir": run_dir, "name": run_dir.name, "config": config, "cell": cell_of(config), "labels": labels, "blocks": blocks,
            "log": log, "model_echoed": config.get("model_echoed") or config.get("model"),
            "model_key": config.get("model_key") or ("sonnet" if "sonnet" in config.get("model", "") else "haiku"),
            "version": config.get("prompt_version") or config.get("prompt", "judge_prompt_v1.md").replace("judge_prompt_", "").replace(".md", ""),
            "mode": mode, "curve_label": label + repeat}


def primaries(labels: list[list[str]], level: int) -> list[str]:
    return [S.truncate(p[0], level) for p in labels]


def confusion_classes(judge: dict, reviewed: dict) -> dict:
    rev2, jud2, rev_sets2, jud_sets2 = [], [], [], []
    for t in judge:
        rev2 += primaries(reviewed[t], 2)
        jud2 += primaries(judge[t], 2)
        rev_sets2 += [{S.truncate(p, 2) for p in paths} for paths in reviewed[t]]
        jud_sets2 += [{S.truncate(p, 2) for p in paths} for paths in judge[t]]
    OE = "Reasoning > option evaluation"
    return {
        "global plan -> local plan": sum(1 for a, b in zip(rev2, jud2) if a == "Planning > global plan" and b == "Planning > local plan"),
        "rephrasing an earlier sentence -> anything else": sum(1 for a, b in zip(rev2, jud2) if a == "Restatement > rephrasing an earlier sentence" and b != a),
        "branching -> anything else": sum(1 for a, b in zip(rev2, jud2) if a == "Assumption > branching (case split)" and b != a),
        "option evaluation n_judge vs n_reviewed": (sum(1 for s in jud_sets2 if OE in s), sum(1 for s in rev_sets2 if OE in s)),
        "meta-evaluation -> emotion or impression": sum(1 for a, b in zip(rev2, jud2) if a == "Reflection > meta-evaluation of a step" and b == "Reflection > emotion or impression"),
        "announce output -> emotion or impression": sum(1 for a, b in zip(rev2, jud2) if a == "Planning > announce output" and b == "Reflection > emotion or impression"),
    }


def projection(run: dict, sentences_judged: int) -> dict:
    """Judge-side cost per collection at batch prices from the run's measured rates:
    input = collection text tokens x (run's uncached input / one clean pass) + prefixes;
    output = run's output tokens per judged sentence (thinking and any leaked reasoning
    included) x collection sentences; cache reads one system prompt per document."""
    inp_total = sum(v["input"] for v in run["log"].values())
    out_total = sum(v["output"] for v in run["log"].values())
    factor = inp_total / SONNET_SINGLE_PASS_INPUT if run["model_key"] == "sonnet" else 1.0
    out_ps = out_total / sentences_judged
    costs = {}
    for name, docs, text, prefix, sents in COLLECTIONS:
        inp = text * factor + prefix
        out = out_ps * sents
        cr = docs * SYS_TOKENS
        costs[name] = (inp * BATCH["in"] + out * BATCH["out"] + cr * BATCH["cr"] + SYS_TOKENS * BATCH["cw"]) / 1e6
    costs["total"] = sum(costs.values())
    costs["_input_factor"] = factor
    costs["_output_per_sentence"] = out_ps
    return costs


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", help="a judge run folder (repeatable); default: all runs/experiments/judge_source_*")
    ap.add_argument("--out", help="output folder (default runs/experiments/judge_compare_2x2_<stamp>)")
    args = ap.parse_args(argv)
    run_dirs = [Path(r) for r in args.run] if args.run else sorted((REPO / "runs" / "experiments").glob("judge_source_*"))
    runs = [load_run(d) for d in run_dirs
            if (d / "labels_source_judge.jsonl").exists() and (d / "labels_source_judge.jsonl").stat().st_size > 0]
    runs = [r for r in runs if r["labels"]]
    by_cell: dict[tuple[str, str], dict] = {}
    for r in runs:
        by_cell[r["cell"]] = r  # the latest run of a cell wins (sorted by name = by time)
    listing = D.parse_listing()
    reviewed = {t: listing[t]["labels"] for t in listing}
    texts = {t: listing[t]["texts"] for t in listing}
    stamp = datetime.now()
    out_dir = Path(args.out) if args.out else REPO / "runs" / "experiments" / f"judge_compare_2x2_{stamp:%Y-%m-%d_%H%M}"
    out_dir.mkdir(parents=True, exist_ok=True)
    md = [f"# Judge comparison — prompt v1/v2 x Haiku 4.5/Sonnet 5, thinking modes — {stamp:%Y-%m-%d %H:%M}", "",
          "Reviewed labels: docs/shared/2026-09-16_source_traces_labeled_v3.md. Exact-match rate on label sets, kappa on the primary label (reviewed as reference). "
          "Judge blocks and nodes from the derivation on the judge's labels, against the reviewed 46/193 (c004) and 37/146 (e036).", "", "Runs:", ""]
    for r in runs:
        md.append(f"- `{r['name']}`: model {r['model_key']} (echoed {r['model_echoed']}), prompt {r['version']}, thinking {r['mode']} ({r['curve_label']})")
    md.append("")
    # agreement per run (all runs)
    results = {}
    for r in runs:
        res = {}
        for t in ("c004", "e036"):
            if t in r["labels"]:
                res[t] = S.agreement({t: r["labels"][t]}, {t: reviewed[t]}, {t: texts[t]})
        res["pooled"] = S.agreement(r["labels"], reviewed, texts)
        results[r["name"]] = res

    def table(scope: str):
        rows = ["| cell | L1 exact | L1 kappa | L2 exact | L2 kappa | L3 exact | L3 kappa | blocks (reviewed) | nodes (reviewed) | attempts | cost |",
                "|---|---|---|---|---|---|---|---|---|---|---|"]
        for cell in CELL_ORDER:
            r = by_cell.get(cell)
            if not r or scope not in results[r["name"]]:
                rows.append(f"| {cell[0]} × {cell[1]} | — | — | — | — | — | — | — | — | — | — |")
                continue
            lv = {x["level"]: x for x in results[r["name"]][scope]["levels"]}
            traces = [scope] if scope != "pooled" else [t for t in ("c004", "e036") if t in r["labels"]]
            b = sum(r["blocks"][t]["blocks"] for t in traces)
            n = sum(r["blocks"][t]["nodes"] for t in traces)
            rb = sum(REVIEWED[t]["blocks"] for t in traces)
            rn = sum(REVIEWED[t]["nodes"] for t in traces)
            att = "+".join(str(r["log"][t]["attempts"]) for t in traces)
            cost = sum(r["log"][t]["cost"] for t in traces)
            rows.append(f"| {cell[0]} × {cell[1]} | {lv[1]['exact_match']:.3f} | {lv[1]['kappa']:.3f} | {lv[2]['exact_match']:.3f} | {lv[2]['kappa']:.3f} | "
                        f"{lv[3]['exact_match']:.3f} | {lv[3]['kappa']:.3f} | {b} ({rb}) | {n} ({rn}) | {att} | ${cost:.4f} |")
        return rows

    for scope, title in (("c004", "C-trace c004 (375 sentences)"), ("e036", "E-trace e036 (254 sentences)"), ("pooled", "Pooled (629 sentences)")):
        md += [f"## 2x2, thinking off: {title}", ""] + table(scope) + [""]
    md += ["## Confusion classes per 2x2 cell (pooled over both traces; reviewed → judge on the Level 2 primary label; option evaluation as n_judge vs n_reviewed of the Level 2 label set)", "",
           "| class | " + " | ".join(f"{c[0]} × {c[1]}" for c in CELL_ORDER) + " |", "|---|" + "---|" * len(CELL_ORDER)]
    classes = {cell: confusion_classes(by_cell[cell]["labels"], reviewed) for cell in by_cell if cell in CELL_ORDER}
    if classes:
        for name in next(iter(classes.values())):
            cells = []
            for cell in CELL_ORDER:
                v = classes.get(cell, {}).get(name, "—")
                cells.append(f"{v[0]} vs {v[1]}" if isinstance(v, tuple) else str(v))
            md.append(f"| {name} | " + " | ".join(cells) + " |")
    md.append("")
    for cell in CELL_ORDER:
        if cell not in by_cell:
            continue
        r = by_cell[cell]
        md += [f"## Ten most frequent Level 2 confusions, {cell[0]} × {cell[1]} (reviewed → judge, primary label, pooled)", "", "| reviewed | judge | count |", "|---|---|---|"]
        for (a, b), c in results[r["name"]]["pooled"]["confusions"][2][:10]:
            md.append(f"| {a} | {b} | {c} |")
        md.append("")
    # structural metrics for every run
    structural = {}
    md += ["## Structural metrics (scripts/structural_agreement.py), every run", ""]
    for r in runs:
        st = SA.compute(r["labels"], {t: reviewed[t] for t in r["labels"]})
        structural[r["name"]] = st
        SA.write_csv(out_dir / f"structural_{r['name']}.csv", st)
        md += [SA.markdown(st, f"{r['name']} ({r['model_key']} × {r['version']}, thinking {r['curve_label']})"), ""]
    # reasoning curve over the Sonnet x v2 cells
    curve = [r for r in runs if r["model_key"] == "sonnet" and r["version"] == "v2"]
    order = {"none": 0, "leaked": 1, "off": 1, "low": 2, "medium": 3}
    curve.sort(key=lambda r: (order.get(r["curve_label"].split()[0], 9), r["curve_label"], r["name"]))
    md += ["## Reasoning curve, Sonnet 5 × prompt v2", "",
           "Thinking tokens per sentence from usage.output_tokens_details (0 where thinking was disabled; the leaked cell's reasoning sits in its output tokens instead); "
           "structural metrics pooled over both traces; projected judge-side cost per collection at Sonnet batch prices ($1/$5 per million input/output, cache read $0.10, cache write $1.25): "
           "input = collection text tokens × (the cell's uncached input ÷ one clean pass of 15,038 tokens) + prefix tokens (archived500: 424k × 1.6; new continuations: 720 × 1,908 × 1.6), "
           "output = the cell's output tokens per judged sentence × collection sentences (sweep44 15,295; archived500 240,620; new continuations 5.9M ÷ 23.91 = 246,781), one cached system prompt read per document.", "",
           "| cell | run | thinking tokens / sentence | attempts | L1 exact / kappa | L2 exact / kappa | full exact / kappa | block F1 | next-node agreement | node F1 | L1 share of disagreements | cost e036 / c004 | output tokens / sentence | input factor | projected sweep44 | projected archived500 | projected new continuations | projected total |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in curve:
        sents = sum(len(v) for v in r["labels"].values())
        th = sum(v["thinking"] for v in r["log"].values()) / sents
        lv = {x["level"]: x for x in results[r["name"]]["pooled"]["levels"]}
        st = structural[r["name"]]["pooled"]
        pj = projection(r, sents)
        att = "+".join(str(r["log"][t]["attempts"]) for t in ("e036", "c004") if t in r["log"])
        md.append(f"| {r['curve_label']} | `{r['name']}` | {th:.2f} | {att} | {lv[1]['exact_match']:.3f} / {lv[1]['kappa']:.3f} | {lv[2]['exact_match']:.3f} / {lv[2]['kappa']:.3f} | "
                  f"{lv[3]['exact_match']:.3f} / {lv[3]['kappa']:.3f} | {st['blocks']['f1']:.3f} | {st['next_node']['rate']:.3f} | {st['nodes']['f1']:.3f} | {st['sentences']['l1_share_of_disagreements']:.3f} | "
                  f"${r['log'].get('e036', {}).get('cost', 0):.4f} / ${r['log'].get('c004', {}).get('cost', 0):.4f} | {pj['_output_per_sentence']:.2f} | {pj['_input_factor']:.2f} | "
                  f"${pj['sweep44']:.2f} | ${pj['archived500']:.2f} | ${pj['new continuations (n = 40)']:.2f} | ${pj['total']:.2f} |")
    md.append("")
    for r in curve:
        md += [f"### Ten most frequent Level 2 confusions, {r['curve_label']} (`{r['name']}`, reviewed → judge, pooled)", "", "| reviewed | judge | count |", "|---|---|---|"]
        for (a, b), c in results[r["name"]]["pooled"]["confusions"][2][:10]:
            md.append(f"| {a} | {b} | {c} |")
        md.append("")
    (out_dir / "comparison.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    summary = {r["name"]: {"cell": r["cell"], "curve_label": r["curve_label"], "pooled_levels": results[r["name"]]["pooled"]["levels"],
                           "structural_pooled": {g: {k: v for k, v in structural[r["name"]]["pooled"][g].items() if k not in ("confusions", "misses_idx", "extras_idx")} for g in ("blocks", "next_node", "nodes", "sentences")}}
               for r in runs}
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"\nWritten: {out_dir / 'comparison.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
