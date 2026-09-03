"""
analysis_cuts.py — independent re-derivation of the resampling numbers (A1).

Reads the raw resampling records and reconstructs, per prefix, the answer
distribution and the headline rates. Written from scratch against the raw jsonl;
does not import or reuse any tabulation code from the run scripts.

Conventions (stated once, used everywhere):
- P(C) uses CONTAINMENT ("C-involving", the registered convention): any letters
  tuple containing "C" counts, e.g. ("A","C"). Two such multi-letter draws exist
  after the 08/29 scoring revision (cuts 15 and 59); before it, exact-match was
  provably equivalent, which is why earlier versions used it.
- P(E) counts letters == ("E",) exactly: ("D","E") does not count as settling on E.
- Unparsed draws (letters == ()) stay in every denominator and are reported as
  counts ("None"); readers can renormalize from the full tables.

Outputs (repo root):
  probability_summary          — baseline + P(C|cut), P(E|cut) table
  plots (if SAVE_PLOTS): plot_cuts_c004.png, plot_cuts_e036.png, plot_cut0_pie.png
"""
import pandas as pd
import matplotlib.pyplot as plt

TARGET_KEYS = ["id", "prefix_id", "seq", "cut", "trace_arm", "letters"]
SHOW_PLOTS = False      # interactive windows
SAVE_PLOTS = True       # write PNGs next to the summaries
PRINT_Q = False         # verbose intermediate printing

def printer(*item):
    if PRINT_Q:
        print(*item)

df_raw = pd.read_json("runs/resample_cuts_2026-08-25_1503_rescored.jsonl", lines=True)
df = df_raw[df_raw.columns.intersection(TARGET_KEYS)].copy()
df["letters"] = df["letters"].apply(tuple)

# ---------------- sanity checks: the design invariant ----------------
print("*" * 50)
counts = df.groupby("prefix_id").size()
ok_sizes = counts.eq(25).all()
ok_groups = len(counts) == 20
multi_c = df["letters"].apply(lambda t: "C" in t and len(t) > 1).sum()   # informational
if ok_sizes and ok_groups:
    print(f"Sanity check: pass ({len(counts)} prefixes x 25 draws)")
else:
    print(f"Sanity check: NOT pass. groups={len(counts)} (expect 20); "
          f"sizes: {sorted(counts.unique())} (expect [25])")
print(f"multi-letter draws containing C: {multi_c} (counted as C-involving under containment)")
print("*" * 50)

# ---------------- full per-prefix answer distributions ----------------
df_trace_cut = (df.groupby(["trace_arm", "cut"])["letters"]
                  .value_counts().reset_index(name="count"))
print(df_trace_cut.to_string())

# ---------------- headline rates ----------------
summary_table = []

shared = df[df["trace_arm"] == "shared"]
n_shared = len(shared)
summary_table.append(["P(C) at cut-0 (shared baseline)",
                      float(shared["letters"].apply(lambda t: "C" in t).sum() / n_shared)])
summary_table.append(["P(E) at cut-0 (shared baseline)",
                      float((shared["letters"] == ("E",)).sum() / n_shared)])
summary_table.append(["P(other or None) at cut-0",
                      float(((shared["letters"] != ("C",)) &
                             (shared["letters"] != ("E",))).sum() / n_shared)])

for cut in sorted(df.loc[df["trace_arm"] == "c004", "cut"].unique()):
    mask = (df["trace_arm"] == "c004") & (df["cut"] == cut)
    total_occurrence = mask.sum()
    c_occurrence = (mask & (df["letters"].apply(lambda t: "C" in t))).sum()
    printer("cut", cut, "C =", c_occurrence, "/", total_occurrence)
    summary_table.append([f"P(C|C-trace, cut at {cut})",
                          float(c_occurrence / total_occurrence)])

for cut in sorted(df.loc[df["trace_arm"] == "e036", "cut"].unique()):
    mask = (df["trace_arm"] == "e036") & (df["cut"] == cut)
    total_occurrence = mask.sum()
    e_occurrence = (mask & (df["letters"] == ("E",))).sum()
    printer("cut", cut, "E =", e_occurrence, "/", total_occurrence)
    summary_table.append([f"P(E|E-trace, cut at {cut})",
                          float(e_occurrence / total_occurrence)])

df_summary = pd.DataFrame(summary_table, columns=["quantity", "probability"])
print(df_summary.to_string(index=False))
df_summary.to_csv("probability_summary", index=False)

# ---------------- plots ----------------
CATEGORY_ORDER = ["C", "A,C", "C,E", "E", "D,E", "B", "A", "F", "None"]
CATEGORY_COLOR = {"C": "#c0392b", "A,C": "#e74c3c", "C,E": "#e67e22", "E": "#2980b9",
                  "D,E": "#8e44ad", "B": "#f1c40f", "A": "#27ae60", "F": "#16a085",
                  "None": "#95a5a6"}
DEFAULT_COLOR = "#34495e"   # any category not listed above still renders

def format_letters(x):
    return "None" if len(x) == 0 else ",".join(x)

if SHOW_PLOTS or SAVE_PLOTS:
    dist = df_trace_cut.copy()
    dist["letters"] = dist["letters"].apply(format_letters)

    def plot_bar_chart(trace_str, title, fname):
        plot_df = (dist[dist["trace_arm"] == trace_str]
                   .pivot(index="cut", columns="letters", values="count")
                   .fillna(0))
        cols = [c for c in CATEGORY_ORDER if c in plot_df.columns]
        cols += [c for c in plot_df.columns if c not in cols]   # never drop a category
        plot_df = plot_df[cols]
        ax = plot_df.plot(kind="bar", stacked=True, width=0.65,
                          color=[CATEGORY_COLOR.get(c, DEFAULT_COLOR) for c in cols],
                          figsize=(8, 4.2), edgecolor="white", linewidth=0.5)
        ax.set_title(title)
        ax.set_xlabel("prefix ends after sentence k")
        ax.set_ylabel("continuations (n = 25 per cut)")
        ax.legend(title="final answer", bbox_to_anchor=(1.02, 1), loc="upper left")
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)
        plt.tight_layout()
        if SAVE_PLOTS:
            plt.savefig(fname, dpi=200)
        if SHOW_PLOTS:
            plt.show()
        plt.close()

    plot_bar_chart("c004", "C-trace (s0819_eval0multi0_004): answers by cut",
                   "plot_cuts_c004.png")
    plot_bar_chart("e036", "E-trace (s0819_eval0multi0_036): answers by cut",
                   "plot_cuts_e036.png")

    pie_df = (dist[dist["trace_arm"] == "shared"]
              .groupby("letters")["count"].sum())
    pie_order = [c for c in CATEGORY_ORDER if c in pie_df.index]
    pie_order += [c for c in pie_df.index if c not in pie_order]
    pie_df = pie_df.reindex(pie_order)
    total = pie_df.sum()
    labels = [f"{k}  {v}/{total} ({v/total*100:.0f}%)" for k, v in pie_df.items()]
    fig, ax = plt.subplots(figsize=(5.2, 5.2))
    ax.pie(pie_df, labels=labels, startangle=180, counterclock=False, labeldistance=0.75,
           colors=[CATEGORY_COLOR.get(k, DEFAULT_COLOR) for k in pie_df.index],
           wedgeprops=dict(edgecolor="white", linewidth=1))
    ax.set_title("cut-0 (no prefix): baseline answer distribution, n = 25")
    plt.tight_layout()
    if SAVE_PLOTS:
        plt.savefig("plot_cut0_pie.png", dpi=200)
    if SHOW_PLOTS:
        plt.show()
    plt.close()