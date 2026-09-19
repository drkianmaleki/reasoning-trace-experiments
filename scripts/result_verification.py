import pandas as pd
import numpy as np
import re

df = pd.read_json("runs/experiments/resample_blocks_2026-09-17_1759/continuations.jsonl", lines=True)

print("Number of records:", len(df))
print("Unique IDs:", df["id"].nunique())
print(df.columns.tolist())

df.head()

print ("="*50)
print ("="*50)
print ("="*50)

def get_answer(letters):
    if len(letters) == 1:
        return letters[0]
    return "?"

df["answer_original"] = df["letters"].apply(get_answer)

group_cols = ["condition", "trace_arm", "block"]

counts = pd.crosstab(
    [
        df["condition"],
        df["trace_arm"],
        df["block"].fillna(-1)
    ],
    df["answer_original"]
)

counts = counts.reindex(
    columns=list("ABCDEF") + ["?"],
    fill_value=0
)

counts["n"] = counts.sum(axis=1)

print(counts.to_string())

print ("="*50)
print ("="*50)


def calculate_shifts(count_table):

    data = count_table.reset_index()
    baseline = data[data["condition"] == "cut0"].iloc[0]

    baseline_p = {
        "c004": baseline["C"] / baseline["n"],
        "e036": baseline["E"] / baseline["n"]
    }

    cuts = data[data["condition"] == "cut"].copy()
    cuts = cuts.sort_values(["trace_arm", "block"])

    cuts["k"] = np.where(
        cuts["trace_arm"] == "c004",
        cuts["C"],
        cuts["E"]
    )

    cuts["p"] = cuts["k"] / cuts["n"]


    cuts["p_prev"] = cuts.groupby("trace_arm")["p"].shift(1)

    cuts["p_prev"] = cuts["p_prev"].fillna(
        cuts["trace_arm"].map(baseline_p)
    )

    cuts["delta"] = cuts["p"] - cuts["p_prev"]

    return cuts


cuts_A = calculate_shifts(counts)

print(
    cuts_A[
        ["trace_arm", "block", "k", "n", "p", "delta"]
    ].to_string(index=False)
)

print ("="*50)
print ("="*50)

for arm in ["c004", "e036"]:

    x = cuts_A[cuts_A["trace_arm"] == arm]

    print("\nTrace:", arm)


    print(
        x.nlargest(3, "delta")[
            ["block", "p", "delta"]
        ].to_string(index=False)
    )


    stopping = x.loc[x["k"] == x["n"], "block"]

    print("First all-target cut:", stopping.min())

    # Gap between the two largest shifts
    top = x["delta"].nlargest(2).to_numpy()

    print("Top-two gap:", round(top[0] - top[1], 4))


def score_completed(row):

    # No completed reply
    if row["finish"] != "stop" or not row["think_closed"]:
        return "?"

    # Extract the reply after the thinking section
    reply = row["cont_text"].split("</think>", 1)[-1]

    # Last nonblank line
    final_line = reply.strip().splitlines()[-1]

    # Remove simple Markdown formatting
    final_line = re.sub(r"[*_`]", "", final_line).strip()

    # Accept Answer: C, Answer: (C), etc.
    match = re.search(
        r"\bAnswer:\s*\(?([A-F])\)?\s*[.!]?\s*$",
        final_line,
        flags=re.IGNORECASE
    )

    if match:
        return match.group(1).upper()

    return "?"


df["answer_checked"] = df.apply(score_completed, axis=1)

# Find disagreements
disagree = df[
    df["answer_original"] != df["answer_checked"]
]

print("Number of disagreements:", len(disagree))

print(
    disagree[
        ["id", "finish", "letters",
         "answer_original", "answer_checked"]
    ].to_string(index=False)
)



# Inspect one particular continuation
record = disagree.iloc[0]

print("ID:", record["id"])
print("Original:", record["answer_original"])
print("Checked:", record["answer_checked"])

# Last 500 characters of its continuation
print(record["cont_text"][-500:])

print ("="*50)
print ("="*50)

counts_B = pd.crosstab(
    [
        df["condition"],
        df["trace_arm"],
        df["block"].fillna(-1)
    ],
    df["answer_checked"]
)

counts_B = counts_B.reindex(
    columns=list("ABCDEF") + ["?"],
    fill_value=0
)

counts_B["n"] = counts_B.sum(axis=1)

cuts_B = calculate_shifts(counts_B)

# Compare the two analyses
comparison = cuts_A[
    ["trace_arm", "block", "p", "delta"]
].merge(
    cuts_B[["trace_arm", "block", "p", "delta"]],
    on=["trace_arm", "block"],
    suffixes=("_original", "_checked")
)

print(comparison.to_string(index=False))


print ("="*50)
print ("="*50)


def wilson(k, n):
    z = 1.959964
    p = k / n

    denominator = 1 + z**2 / n
    center = (p + z**2 / (2*n)) / denominator

    half = z * np.sqrt(
        p*(1-p)/n + z**2/(4*n**2)
    ) / denominator

    return center - half, center + half


def add_intervals(cuts, count_table):

    cuts = cuts.copy()

    # Wilson interval for each cut
    cuts["lo"], cuts["hi"] = wilson(
        cuts["k"], cuts["n"]
    )

    # Wilson intervals for cut-0 baseline
    baseline = count_table.reset_index()
    baseline = baseline[baseline["condition"] == "cut0"].iloc[0]

    base_lo = {}
    base_hi = {}

    for arm, letter in [("c004", "C"), ("e036", "E")]:
        base_lo[arm], base_hi[arm] = wilson(
            baseline[letter], baseline["n"]
        )

    # Previous cut's Wilson interval
    cuts["prev_lo"] = cuts.groupby("trace_arm")["lo"].shift(1)
    cuts["prev_hi"] = cuts.groupby("trace_arm")["hi"].shift(1)

    cuts["prev_lo"] = cuts["prev_lo"].fillna(
        cuts["trace_arm"].map(base_lo)
    )
    cuts["prev_hi"] = cuts["prev_hi"].fillna(
        cuts["trace_arm"].map(base_hi)
    )

    # Newcombe interval for the signed shift
    cuts["delta_lo"] = cuts["delta"] - np.sqrt(
        (cuts["p"] - cuts["lo"])**2
        + (cuts["prev_hi"] - cuts["p_prev"])**2
    )

    cuts["delta_hi"] = cuts["delta"] + np.sqrt(
        (cuts["hi"] - cuts["p"])**2
        + (cuts["p_prev"] - cuts["prev_lo"])**2
    )

    return cuts


cuts_A = add_intervals(cuts_A, counts)
cuts_B = add_intervals(cuts_B, counts_B)

print(
    cuts_A[
        ["trace_arm", "block", "p", "lo", "hi",
         "delta", "delta_lo", "delta_hi"]
    ].round(4).to_string(index=False)
)

print ("="*50)
print ("="*50)

def bootstrap_gap(cuts, count_table, arm, B=10000):

    rng = np.random.default_rng(0)

    letter = "C" if arm == "c004" else "E"

    # Original cut-0 baseline
    baseline = count_table.reset_index()
    baseline = baseline[baseline["condition"] == "cut0"].iloc[0]

    n0 = int(baseline["n"])
    p0 = baseline[letter] / n0

    # Bootstrap the baseline
    base_draw = rng.binomial(n0, p0, size=B) / n0

    # All cuts of this trace
    x = cuts[cuts["trace_arm"] == arm].sort_values("block")

    # Every experimental cut contains 25 records
    assert (x["n"] == 25).all()

    # Independent bootstrap samples for each cut
    samples = rng.binomial(
        25,
        x["p"].to_numpy(),
        size=(B, len(x))
    ) / 25

    # Previous probability in every bootstrap draw
    previous = np.column_stack([
        base_draw,
        samples[:, :-1]
    ])

    # Recalculate all shifts
    shifts = samples - previous

    # Rank shifts separately in every bootstrap draw
    ranked = np.sort(shifts, axis=1)

    gaps = ranked[:, -1] - ranked[:, -2]

    return np.quantile(gaps, [0.025, 0.975])


for name, cuts, table in [
    ("Original", cuts_A, counts),
    ("Checked", cuts_B, counts_B)
]:
    for arm in ["c004", "e036"]:

        ci = bootstrap_gap(cuts, table, arm)

        print(name, arm, np.round(ci, 4))


print ("="*50)
print ("="*50)