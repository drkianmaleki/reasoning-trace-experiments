"""
analysis_base.py — independent re-derivation of the 08/19 sweep numbers (A1).

The sweep is four experiments in one file: each record's "condition" labels its
2x2 cell (eval sentence on/off x multi/single select). Registered quantities are
per cell; the pooled table is kept as a secondary view.

Conventions:
- "C-involving" uses CONTAINMENT: any letters tuple containing "C" counts,
  so ("C","E") counts. This is the convention the registered numbers
  (C-involving 25/194; eval effect 12/48 -> 5/50) were defined with.
  Exact-match C is also reported as a stricter secondary count.
- E-only = letters == ("E",) exactly.
- Unparsed (letters == ()) kept in denominators, reported as counts.

Outputs (repo root):
  baseline_summary        — pooled letters distribution over all 194 records
  baseline_cells_summary  — per-cell counts + derived registered quantities
  plot_baseline_cells.png — four pies, one per 2x2 cell (if SAVE_PLOTS)
"""
import pandas as pd
import matplotlib.pyplot as plt

TARGET_KEYS = ["condition", "letters", "sample"]
PRINT_Q = True
SHOW_PLOTS = False      # interactive windows
SAVE_PLOTS = True       # write PNG next to the summaries

def printer(*item):
    if PRINT_Q:
        print(*item)

df_raw = pd.read_json("runs/sweep_items_batball_2026-08-19_1623_rescored.jsonl", lines=True)
df = df_raw[df_raw.columns.intersection(TARGET_KEYS)].copy()
df["letters"] = df["letters"].apply(tuple)

# ---------------- sanity: cell sizes ----------------
print("*" * 50)
sizes = df.groupby("condition").size()
print(sizes.to_string())
expected = {"eval0_multi0": 44, "eval0_multi1": 50,
            "eval1_multi0": 50, "eval1_multi1": 50}
ok = all(sizes.get(k, 0) == v for k, v in expected.items()) and len(df) == 194
print(f"Sanity check: {'pass' if ok else 'NOT pass'} "
      f"(total {len(df)}; eval0_multi0 short by 6 lost samples, by design of the record)")
print("*" * 50)

# ---------------- per-cell distributions (the registered view) ----------------
df_cells = (df.groupby("condition")["letters"]
              .value_counts().reset_index(name="count"))
printer(df_cells.to_string())

# derived registered quantities
rows = []
for cond, g in df.groupby("condition"):
    n = len(g)
    c_inv = g["letters"].apply(lambda t: "C" in t).sum()      # containment
    c_exact = (g["letters"] == ("C",)).sum()
    e_only = (g["letters"] == ("E",)).sum()
    unparsed = (g["letters"] == ()).sum()
    rows.append([cond, n, int(e_only), int(c_inv), int(c_exact), int(unparsed),
                 float(e_only / n), float(c_inv / n)])
cells = pd.DataFrame(rows, columns=["condition", "n", "E_only", "C_involving",
                                    "C_exact", "unparsed", "P_E_only", "P_C_involving"])
print(cells.to_string(index=False))
cells.to_csv("baseline_cells_summary", index=False)

total_c_involving = int(df["letters"].apply(lambda t: "C" in t).sum())
print(f"C-involving total: {total_c_involving}/194")
m0 = df[df["condition"] == "eval0_multi1"]
m1 = df[df["condition"] == "eval1_multi1"]
print("eval effect (multi cells, C-involving over parsed):",
      f"{int(m0['letters'].apply(lambda t: 'C' in t).sum())}/"
      f"{int((m0['letters'] != ()).sum())} (eval off)  vs  "
      f"{int(m1['letters'].apply(lambda t: 'C' in t).sum())}/"
      f"{int((m1['letters'] != ()).sum())} (eval on)")

# ---------------- pooled view (secondary) ----------------
df_counts = df["letters"].value_counts()
printer(df_counts.to_string())
baseline_summary = pd.DataFrame(
    [[f"P{val}", float(count / len(df))] for val, count in df_counts.items()],
    columns=["letters", "probability"])
print(baseline_summary.to_csv(index=False))
baseline_summary.to_csv("baseline_summary", index=False)

# ---------------- per-cell pie charts (2x2, the elicitation picture) ----------------
# Same category order/colors as analysis_cuts.py so all figures read alike.
CATEGORY_ORDER = ["C", "A,C", "C,E", "E", "D,E", "B", "A", "F", "None"]
CATEGORY_COLOR = {"C": "#c0392b", "A,C": "#e74c3c", "C,E": "#e67e22", "E": "#2980b9",
                  "D,E": "#8e44ad", "B": "#f1c40f", "A": "#27ae60", "F": "#16a085",
                  "None": "#95a5a6"}
DEFAULT_COLOR = "#34495e"

def format_letters(x):
    return "None" if len(x) == 0 else ",".join(x)

if SHOW_PLOTS or SAVE_PLOTS:
    CELL_POS = {"eval0_multi0": (0, 0), "eval0_multi1": (0, 1),
                "eval1_multi0": (1, 0), "eval1_multi1": (1, 1)}
    CELL_TITLE = {"eval0_multi0": "no eval sentence, single-select",
                  "eval0_multi1": "no eval sentence, multi-select",
                  "eval1_multi0": "eval sentence, single-select",
                  "eval1_multi1": "eval sentence, multi-select"}
    fig, axes = plt.subplots(2, 2, figsize=(9.2, 9.2))
    for cond, g in df.groupby("condition"):
        counts = g["letters"].apply(format_letters).value_counts()
        order = [c for c in CATEGORY_ORDER if c in counts.index]
        order += [c for c in counts.index if c not in order]   # never drop a category
        counts = counts.reindex(order)
        n = int(counts.sum())
        ax = axes[CELL_POS[cond]]
        labels = [f"{k}  {v}/{n} ({v/n*100:.0f}%)" for k, v in counts.items()]
        ax.pie(counts, labels=labels, startangle=180, counterclock=False,
               labeldistance=0.72, textprops={"fontsize": 8.5},
               colors=[CATEGORY_COLOR.get(k, DEFAULT_COLOR) for k in counts.index],
               wedgeprops=dict(edgecolor="white", linewidth=1))
        ax.set_title(f"{CELL_TITLE[cond]}  (n = {n})", fontsize=10)
    fig.suptitle("Sweep 2x2: answer distribution per prompt variant (rescored letters)\n"
                 "Same underlying question, four elicitation formats", fontsize=11.5)
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    if SAVE_PLOTS:
        plt.savefig("plot_baseline_cells.png", dpi=200)
    if SHOW_PLOTS:
        plt.show()
    plt.close()