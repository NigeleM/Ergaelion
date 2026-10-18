"""Cooperation rates from the Dal Bó and Fréchette (2011) data, as shipped in the stratEst R package.

Run after exporting data.DF2011 to CSV (see the note at the end of docs/research/README.md):
    python3 docs/research/dalbo2011_rates.py dalbo2011.csv
The 'input' column is the previous round's profile: the first letter is your action, the second the partner's.
"""
import sys
import pandas as pd

df = pd.read_csv(sys.argv[1])
df["choice"] = df["choice"].astype(str)
df["other.choice"] = df["other.choice"].astype(str)
df["input"] = df["input"].astype(str)

first = df[df.period == 1]
print("First period, you cooperate, by treatment:")
print(first.groupby("treatment", observed=True)["choice"].apply(lambda s: round((s == "c").mean(), 3)).to_string())
print(f"Pooled first-period cooperation (n={len(first)}): {(first['other.choice'] == 'c').mean():.3f}")

later = df[df.period >= 2]
print("Partner cooperates this period, by previous round and your current choice:")
for (inp, mine), group in later.groupby(["input", "choice"], observed=True):
    print(f"  previous {inp}, you now {mine}: {(group['other.choice'] == 'c').mean():.2f} (n={len(group)})")
