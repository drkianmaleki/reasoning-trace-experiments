"""Unit tests for scripts/s3_judge_continuations.py with a stubbed batch client: the split of
continuations (thinking part only), the registered labeling order (cut-0, then the traces
interleaved by m) in waves, the documents with the reviewed prefix (block-end index), the merged
pnext, the ceiling, the noise subset.  No API call.
Run: python -m pytest -q scripts/tests/test_s3_judge_continuations.py"""
import csv
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import s0_split as S0  # noqa: E402
import s3_judge_continuations as S3  # noqa: E402
from test_s1_judge_batch import stub_client  # noqa: E402

CONT = {  # plain sentences (an equation would be split further by the equation rule)
    "rb_cut0_000": ("cut0", "shared", None, None, "Here's a plan:\nStart simple.</think>\nAnswer: E"),
    "rb_c004_B00_000": ("cut", "c004", 7, 0, "Wait, re-read.\nThe prompt says ten cents.</think>\nAnswer: C"),
    "rb_c004_B00_001": ("cut", "c004", 7, 0, "So the ball is cheap.\nAnswer: C (no tag: cap hit)"),
    "rb_e036_B00_000": ("cut", "e036", 11, 0, "Let me restate.\nThe bat costs more.</think>\nAnswer: E"),
    "rb_c004_B01_000": ("cut", "c004", 12, 1, "1.\n**Check:**\nThe sum is right.</think>\nAnswer: C"),
    "rb_nothink_000": ("nothink", "shared", None, None, "Answer: E"),
}
N_SENT = {cid: len(S0.split_records(cid, text, continuation=True)) for cid, (_, _, _, _, text) in CONT.items()}


def run_of(code: str, n: int) -> str:
    return f"0 {code}" if n == 1 else f"0-{n - 1} {code}"


REPLIES = {"rb_cut0_000": run_of("Pl.gp", N_SENT["rb_cut0_000"]),
           "rb_c004_B00_000": "0 Pl.iv.wdm" + (f"\n1-{N_SENT['rb_c004_B00_000'] - 1} Re.lr.al" if N_SENT["rb_c004_B00_000"] > 2 else "\n1 Re.lr.al"),
           "rb_c004_B00_001": run_of("Co.ic", N_SENT["rb_c004_B00_001"]),
           "rb_e036_B00_000": run_of("Rs.rtp.qt", N_SENT["rb_e036_B00_000"]),
           "rb_c004_B01_000": run_of("Pl.gp", N_SENT["rb_c004_B01_000"])}


def write_run(folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    with open(folder / "continuations.jsonl", "w", encoding="utf-8") as fh:
        for cid, (cond, arm, cut, m, text) in CONT.items():
            pid = cid.rsplit("_", 1)[0]
            fh.write(json.dumps({"id": cid, "prefix_id": pid, "trace_arm": arm, "condition": cond, "cut": cut, "block": m, "seq": int(cid[-3:]),
                                 "letters": ["C"], "answer": "C", "cont_text": text, "usage": {"prompt_tokens": 1, "completion_tokens": 1}, "cost_usd": 0.0}) + "\n")
    rows = [{"trace_id": "shared", "m": "cut0", "condition": "cut0", "prefix_id": "rb_cut0", "n": 1, "count_C": 0, "p_hat": ""},
            {"trace_id": "c004", "m": 0, "condition": "cut", "prefix_id": "rb_c004_B00", "n": 2, "count_C": 2, "p_hat": "1.0"},
            {"trace_id": "c004", "m": 1, "condition": "cut", "prefix_id": "rb_c004_B01", "n": 1, "count_C": 1, "p_hat": "1.0"},
            {"trace_id": "e036", "m": 0, "condition": "cut", "prefix_id": "rb_e036_B00", "n": 1, "count_C": 0, "p_hat": "1.0"}]
    with open(folder / "pcut.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (folder / "DEPARTURES.md").write_text("", encoding="utf-8")
    return folder


def test_order_split_and_projection(tmp_path):
    run = write_run(tmp_path / "run")
    recs, pcut = S3.load_run(run)
    assert len(recs) == 5 and len(pcut) == 4  # the no-think record is not a continuation to label
    groups = S3.cut_groups(recs)
    assert [g for g, _ in groups] == ["cut0", "c004_B00", "e036_B00", "c004_B01"]  # v2, 8.1: cut-0, then interleaved by m
    waves = S3.waves_of(groups, 2)
    assert [[g for g, _ in w] for w in waves] == [["cut0", "c004_B00"], ["e036_B00", "c004_B01"]]
    path, meta, n_sent = S3.split_collection("continuations_w00", groups[1][1], tmp_path)
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]
    assert n_sent == N_SENT["rb_c004_B00_000"] + N_SENT["rb_c004_B00_001"] and all("think_end" in r for r in rows)
    texts = [r["text"] for r in rows if r["trace_id"] == "rb_c004_B00_000"]
    assert texts[0] == "Wait, re-read." and not any("Answer" in t for t in texts)  # thinking part only
    assert any("Answer" in r["text"] for r in rows if r["trace_id"] == "rb_c004_B00_001")  # no tag: the whole text is split
    assert meta["rb_c004_B00_000"] == {"prefix_id": "rb_c004_B00", "trace_arm": "c004", "cut": 7, "prefix_end_s": 7, "m": 0, "seq": 0}
    proj = S3.project_cost([{"collection": "x", "documents": 3, "sentences": 7, "prefix_sentences": 29}])
    assert proj["total_cost_est_usd"] > 0 and proj["collections"][0]["output_tokens_est"] == round(7 * 41)
    assert S3.noise_cuts_from_pcut(pcut) == {"c004": 0, "e036": 6}  # Delta_0 = 1.0 - 0.0 is the largest


def test_run_dry_real_ceiling_and_noise(tmp_path):
    run = write_run(tmp_path / "run")
    d = S3.run(run, tmp_path / "dry", dry_run=True, log=lambda s: None, wave_size=2)
    assert d["dry_run"] and d["order"] == ["cut0", "c004_B00", "e036_B00", "c004_B01"] and len(d["projection"]["waves"]) == 2
    req = json.loads((tmp_path / "dry" / "continuations_w00" / "requests" / "rb_c004_B00_000.json").read_text(encoding="utf-8"))
    msg = req["messages"][0]["content"]
    assert "a prefix of 8 sentences" in msg.split("\n")[0] and msg.split("\n")[2].startswith("s0: Here's a thinking process") and "\nc0: Wait, re-read.\n" in msg
    client = stub_client(lambda cid, attempt: ("succeeded", REPLIES[cid]))
    s = S3.run(run, tmp_path / "judge", client=client, log=lambda s: None, noise_cuts={"c004": 0}, sleep=lambda x: None, wave_size=2)
    assert s.get("stopped") is None and [w["collection"] for w in s["waves"]] == ["continuations_w00", "continuations_w01"]
    assert s["waves"][0]["valid"] == 3 and s["waves"][1]["valid"] == 2 and s["labeled_cut_groups"] == ["cut0", "c004_B00", "e036_B00", "c004_B01"]
    pn = list(csv.DictReader(open(tmp_path / "judge" / "pnext_run.csv", encoding="utf-8")))
    assert [(r["trace_id"], r["m"]) for r in pn] == [("shared", "cut0"), ("c004", "0"), ("c004", "1"), ("e036", "0")]
    r0 = next(r for r in pn if r["trace_id"] == "c004" and r["m"] == "0")
    assert r0["n"] == "2" and r0["next_Planning"] == "1" and r0["next_Conclusion"] == "1" and r0["first_is_wait"] == "1" and r0["block_end_s"] == "7" and r0["last_node_label"] == "Restatement"
    nz = s["noise"]["collections"]["noise_c004_B00"]
    assert nz["documents"] == 2 and nz["first_node"]["n"] == 2 and nz["first_node"]["agree"] == 2 and nz["level1_kappa"] == pytest.approx(1.0)
    assert (tmp_path / "judge" / "noise_subset.csv").exists() and (tmp_path / "judge" / "unlabeled_cuts.csv").read_text(encoding="utf-8").strip() == "cut_group,reason"
    assert (tmp_path / "judge" / "continuations_w00" / "s3_wave_done.json").exists()
    # a re-run skips the finished waves
    s2 = S3.run(run, tmp_path / "judge", client=stub_client(lambda cid, attempt: ("succeeded", REPLIES[cid])), log=lambda s: None, no_noise=True, sleep=lambda x: None, wave_size=2)
    assert s2["cost_usd"] == pytest.approx(s["cost_usd"] - sum(c["cost_usd"] for c in s["noise"]["collections"].values())) and all(w["valid"] for w in s2["waves"])
    # the ceiling stops labeling in order and lists the unlabeled cuts
    s3 = S3.run(run, tmp_path / "judge_ceiling", client=stub_client(lambda cid, attempt: ("succeeded", REPLIES[cid])), log=lambda s: None, sleep=lambda x: None,
                wave_size=2, claude_ceiling=0.0005)
    assert s3["stopped"].startswith("Claude ceiling") and s3["unlabeled_cuts"] == ["e036_B00", "c004_B01"] and len(s3["waves"]) == 1
    assert "judge: Claude ceiling" in (run / "DEPARTURES.md").read_text(encoding="utf-8") and s3["noise"]["skipped"]
    un = list(csv.DictReader(open(tmp_path / "judge_ceiling" / "unlabeled_cuts.csv", encoding="utf-8")))
    assert [(r["cut_group"], r["reason"]) for r in un] == [("e036_B00", "Claude ceiling (v2, 8.1)"), ("c004_B01", "Claude ceiling (v2, 8.1)")]
