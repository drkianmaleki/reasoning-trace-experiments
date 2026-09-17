#!/usr/bin/env python3
"""compare_judge_runs.py -- the 2x2 judge comparison (prompt v1/v2 x Haiku 4.5/Sonnet 5).

Reads the four judge runs (runs/experiments/judge_source_*), recomputes the agreement against the
reviewed listing per trace and pooled from each run's labels_source_judge.jsonl (so all cells use
the same arithmetic), takes blocks and nodes from blocks_source_judge.jsonl and attempts/cost from
_log.txt, and writes runs/experiments/judge_compare_2x2_<stamp>/comparison.md with
  (i)  a 2x2 table per trace and pooled: exact-match rate and kappa at Levels 1, 2, 3; judge
       blocks and nodes vs reviewed (46/193 c004, 37/146 e036); attempts; cost;
  (ii) the six confusion classes per cell;
  (iii) the ten most frequent Level 2 confusions of each cell.
Usage: python scripts/compare_judge_runs.py [--run DIR ...]   (default: every judge_source_* run)
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

REPO = S.REPO
REVIEWED = {"c004": {"blocks": 46, "nodes": 193}, "e036": {"blocks": 37, "nodes": 146}}
CELL_ORDER = [("haiku", "v1"), ("haiku", "v2"), ("sonnet", "v1"), ("sonnet", "v2")]


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
    labels: dict[str, list[list[str]]] = {}
    with open(run_dir / "labels_source_judge.jsonl", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            labels.setdefault(r["trace_id"], []).append([S.path_of(l) for l in r["labels"]])
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
                     "cache_write": int(f[5]), "output": int(f[6]), "cost": float(f[7])}
    return {"dir": run_dir, "config": config, "cell": cell_of(config), "labels": labels, "blocks": blocks, "log": log,
            "model_echoed": config.get("model_echoed") or config.get("model")}


def primaries(labels: list[list[str]], level: int) -> list[str]:
    return [S.truncate(p[0], level) for p in labels]


def confusion_classes(judge: dict, reviewed: dict) -> dict:
    """Pooled over the traces present in judge."""
    r1 = r2 = j1 = j2 = None
    rev2, jud2 = [], []
    rev_sets2, jud_sets2 = [], []
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
    by_cell: dict[tuple[str, str], dict] = {}
    for r in runs:
        if not r["labels"]:
            continue  # a run that stopped before any valid trace
        by_cell[r["cell"]] = r  # the latest run of a cell wins (sorted by name = by time)
    listing = D.parse_listing()
    reviewed = {t: listing[t]["labels"] for t in listing}
    texts = {t: listing[t]["texts"] for t in listing}
    stamp = datetime.now()
    out_dir = Path(args.out) if args.out else REPO / "runs" / "experiments" / f"judge_compare_2x2_{stamp:%Y-%m-%d_%H%M}"
    out_dir.mkdir(parents=True, exist_ok=True)
    md = [f"# Judge comparison 2x2 — prompt v1/v2 x Haiku 4.5/Sonnet 5 — {stamp:%Y-%m-%d %H:%M}", "",
          "Reviewed labels: docs/shared/2026-09-16_source_traces_labeled_v3.md. Exact-match rate on label sets, kappa on the primary label (reviewed as reference). "
          "Judge blocks and nodes from the derivation on the judge's labels, against the reviewed 46/193 (c004) and 37/146 (e036).", "", "Cells:", ""]
    for cell in CELL_ORDER:
        r = by_cell.get(cell)
        md.append(f"- {cell[0]} × {cell[1]}: " + (f"`{r['dir'].relative_to(REPO).as_posix()}` (model echoed {r['model_echoed']}, prompt {r['config'].get('prompt')})" if r else "MISSING"))
    md.append("")
    results = {}
    for cell, r in by_cell.items():
        res = {}
        for t in ("c004", "e036"):
            if t in r["labels"]:
                res[t] = S.agreement({t: r["labels"][t]}, {t: reviewed[t]}, {t: texts[t]})
        res["pooled"] = S.agreement(r["labels"], reviewed, texts)
        results[cell] = res

    def table(scope: str):
        rows = ["| cell | L1 exact | L1 kappa | L2 exact | L2 kappa | L3 exact | L3 kappa | blocks (reviewed) | nodes (reviewed) | attempts | cost |",
                "|---|---|---|---|---|---|---|---|---|---|---|"]
        for cell in CELL_ORDER:
            r = by_cell.get(cell)
            if not r or scope not in results[cell]:
                rows.append(f"| {cell[0]} × {cell[1]} | — | — | — | — | — | — | — | — | — | — |")
                continue
            lv = {x["level"]: x for x in results[cell][scope]["levels"]}
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
        md += [f"## {title}", ""] + table(scope) + [""]
    md += ["## Confusion classes per cell (pooled over both traces; reviewed → judge on the Level 2 primary label; option evaluation as n_judge vs n_reviewed of the Level 2 label set)", "",
           "| class | " + " | ".join(f"{c[0]} × {c[1]}" for c in CELL_ORDER) + " |", "|---|" + "---|" * len(CELL_ORDER)]
    classes = {cell: confusion_classes(by_cell[cell]["labels"], reviewed) for cell in by_cell}
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
        md += [f"## Ten most frequent Level 2 confusions, {cell[0]} × {cell[1]} (reviewed → judge, primary label, pooled)", "", "| reviewed | judge | count |", "|---|---|---|"]
        for (a, b), c in results[cell]["pooled"]["confusions"][2][:10]:
            md.append(f"| {a} | {b} | {c} |")
        md.append("")
    (out_dir / "comparison.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    summary = {f"{c[0]}_{c[1]}": {"dir": str(by_cell[c]["dir"]), "pooled_levels": results[c]["pooled"]["levels"],
                                  "classes": {k: (list(v) if isinstance(v, tuple) else v) for k, v in classes[c].items()}} for c in by_cell}
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"\nWritten: {out_dir / 'comparison.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
