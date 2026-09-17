#!/usr/bin/env python3
"""large_files_index.py -- rewrites runs/LARGE_FILES_INDEX.md from the git-ignored data files
present under runs/ that exceed 20 MB (Kian, 2026-09-17: large files stay local; the index is
committed in their place).

  python scripts/large_files_index.py [--threshold-mb 20] [--dry-run]

For every such file: path, size, record count (lines), sha256, how it was produced (script, run
folder, batch ids, cost, from the run folder's config.json, batch_state*.json and traces_ file),
whether it can be regenerated (the sentence files yes, with the command; judge labels no), and
the availability line "held locally by Kian; available on request".  Standard library plus git.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INDEX = REPO / "runs" / "LARGE_FILES_INDEX.md"
THRESHOLD_MB = 20
AVAILABILITY = "held locally by Kian; available on request"


def ignored_files(root: Path = REPO, subdir: str = "runs") -> list[Path]:
    """The files git ignores under `subdir` (git ls-files --others --ignored --exclude-standard)."""
    out = subprocess.run(["git", "ls-files", "--others", "--ignored", "--exclude-standard", "--", subdir],
                         cwd=root, capture_output=True, text=True, check=True).stdout
    return [root / line.strip() for line in out.splitlines() if line.strip()]


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def count_lines(path: Path) -> int:
    n = 0
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            n += chunk.count(b"\n")
    return n


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def provenance(path: Path, root: Path = REPO) -> dict:
    """{produced_by, regenerable, regenerate} from the run folder's config.json and batch states."""
    folder = path.parent
    rel_folder = folder.relative_to(root).as_posix() if folder.is_relative_to(root) else str(folder)
    config = load_json(folder / "config.json") or {}
    name = path.name
    if config.get("script") == "scripts/s0_split.py" or name.startswith("sentences_"):
        collection = name[len("sentences_"):-len(".jsonl")] if name.startswith("sentences_") and name.endswith(".jsonl") else "?"
        cinfo = (config.get("collections") or {}).get(collection, {})
        inputs = "; ".join(f"{i['path']} (sha256 {i['sha256'][:12]}…)" for i in cinfo.get("inputs", []))
        produced = (f"scripts/s0_split.py, run folder {rel_folder}, git {str(config.get('git_commit'))[:12]}"
                    + (f", records {cinfo['records']}, traces {cinfo['traces']}" if cinfo else "") + (f", inputs {inputs}" if inputs else "") + "; no API cost")
        return {"produced_by": produced, "regenerable": "yes",
                "regenerate": f"python scripts/s0_split.py --collection {collection} --out {rel_folder}/"}
    if config.get("run_id") and config.get("model"):
        batches = [b["batch_id"] for b in config.get("batches", []) if b.get("batch_id")]
        for extra in ("batch_state.json", "batch_state_retry.json"):
            st = load_json(folder / extra) or {}
            for b in st.get("batches", []):
                if b.get("batch_id") and b["batch_id"] not in batches:
                    batches.append(b["batch_id"])
        cost = None
        traces_file = next(iter(folder.glob("traces_*_judge.jsonl")), None)
        if traces_file is not None:
            cost = 0.0
            with open(traces_file, encoding="utf-8") as fh:
                for line in fh:
                    if line.strip():
                        cost += json.loads(line).get("cost_usd") or 0.0
        produced = (f"scripts/s1_judge.py ({config.get('mode')} mode), run folder {rel_folder}, model {config.get('model')}, prompt {config.get('prompt_version')} "
                    f"(sha256 {str(config.get('prompt_sha256'))[:12]}…), thinking {config.get('thinking_mode')}, git {str(config.get('git_commit'))[:12]}"
                    + (f", batch ids {', '.join(batches)}" if batches else "") + (f", cost ${cost:.2f} at {config.get('mode')} prices" if cost is not None else ""))
        return {"produced_by": produced, "regenerable": "no (judge labels: a new run is a new labeling at the same cost)", "regenerate": ""}
    return {"produced_by": f"unknown (run folder {rel_folder}, no recognized config.json)", "regenerable": "unknown", "regenerate": ""}


def describe(path: Path, root: Path = REPO) -> dict:
    size = path.stat().st_size
    return {"path": path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path), "bytes": size,
            "mb": size / 1048576, "records": count_lines(path), "sha256": sha256_of_file(path), **provenance(path, root)}


def render(entries: list[dict], threshold_mb: float, stamp: datetime | None = None) -> str:
    stamp = stamp or datetime.now()
    out = ["# Large data files held locally (not in git)", "",
           f"Generated by `scripts/large_files_index.py` on {stamp:%Y-%m-%d %H:%M}: every git-ignored data file under runs/ larger than {threshold_mb:g} MB. "
           f"Rule (Kian, 2026-09-17): large files stay local; this index is committed in their place. Every file listed is {AVAILABILITY}. "
           "Re-run the script after a run that produces such a file.", ""]
    if not entries:
        out += ["(no ignored file over the threshold is present)", ""]
        return "\n".join(out)
    out += ["| file | size | records | sha256 | produced by | regenerable | availability |", "|---|---|---|---|---|---|---|"]
    for e in sorted(entries, key=lambda x: x["path"]):
        regen = e["regenerable"] + (f" — `{e['regenerate']}`" if e["regenerate"] else "")
        out.append(f"| `{e['path']}` | {e['mb']:.1f} MB ({e['bytes']} bytes) | {e['records']} | `{e['sha256']}` | {e['produced_by']} | {regen} | {AVAILABILITY} |")
    out.append("")
    return "\n".join(out)


def build(root: Path = REPO, threshold_mb: float = THRESHOLD_MB) -> list[dict]:
    limit = threshold_mb * 1048576
    return [describe(p, root) for p in ignored_files(root) if p.is_file() and p.stat().st_size > limit]


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="rewrite runs/LARGE_FILES_INDEX.md from the ignored data files present")
    ap.add_argument("--threshold-mb", type=float, default=THRESHOLD_MB)
    ap.add_argument("--dry-run", action="store_true", help="print the index instead of writing it")
    args = ap.parse_args(argv)
    entries = build(REPO, args.threshold_mb)
    text = render(entries, args.threshold_mb)
    if args.dry_run:
        print(text)
    else:
        INDEX.write_text(text, encoding="utf-8", newline="\n")
        print(f"{INDEX.relative_to(REPO).as_posix()}: {len(entries)} files listed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
