import pandas as pd
from pathlib import Path

# -----------------------------
# File paths
# -----------------------------

INPUT_FILE = "Data/Silver/electricity_generation_silver.csv"
OUTPUT_FILE = "Data/Gold/electricity_monthly_gold.csv"

# -----------------------------
# Load Silver data
# -----------------------------

df = pd.read_csv(INPUT_FILE)

df["date"] = pd.to_datetime(df["date"])
df["generation_gwh"] = pd.to_numeric(
    df["generation_gwh"],
    errors="coerce"
)

# -----------------------------
# Remove total from source rows
# -----------------------------

source_df = df[
    ~df["source"].str.contains(
        "Total Electricity Generation",
        case=False,
        na=False
    )
].copy()

# -----------------------------
# Monthly total generation
# -----------------------------

monthly_total = (
    source_df
    .groupby("date", as_index=False)["generation_gwh"]
    .sum()
    .rename(columns={
        "generation_gwh": "total_generation_gwh"
    })
)

# -----------------------------
# Renewable generation
# -----------------------------

renewable_sources = [
    "Electricity Generation by Hydel",
    "Electricity Generation by Wind",
    "Electricity Generation by Solar",
    "Electricity Generation by bagasse"
]

renewable = source_df[
    source_df["source"].isin(renewable_sources)
]

renewable_monthly = (
    renewable
    .groupby("date", as_index=False)["generation_gwh"]
    .sum()
    .rename(columns={
        "generation_gwh": "renewable_generation_gwh"
    })
)

# -----------------------------
# Combine metrics
# -----------------------------

gold = monthly_total.merge(
    renewable_monthly,
    on="date",
    how="left"
)

gold["renewable_generation_gwh"] = (
    gold["renewable_generation_gwh"].fillna(0)
)

gold["renewable_share_pct"] = (
    gold["renewable_generation_gwh"]
    / gold["total_generation_gwh"]
    * 100
)

# -----------------------------
# Year and month
# -----------------------------

gold["year"] = gold["date"].dt.year
gold["month"] = gold["date"].dt.month

# -----------------------------
# Year-over-year growth
# -----------------------------

gold = gold.sort_values("date")

gold["yoy_growth_pct"] = (
    gold["total_generation_gwh"]
    .pct_change(periods=12)
    * 100
)

# -----------------------------
# Save Gold dataset
# -----------------------------

Path("Data/Gold").mkdir(
    parents=True,
    exist_ok=True
)

gold.to_csv(
    OUTPUT_FILE,
    index=False
)

# -----------------------------
# Validation
# -----------------------------

print("\n--- GOLD DATASET ---")
print(gold.head(15))

print("\n--- SHAPE ---")
print(gold.shape)

print("\n--- DATE RANGE ---")
print(gold["date"].min())
print(gold["date"].max())

print(f"\nSaved to: {OUTPUT_FILE}")