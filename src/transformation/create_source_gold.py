import pandas as pd
from pathlib import Path

INPUT_FILE = "Data/Silver/electricity_generation_silver.csv"
OUTPUT_FILE = "Data/Gold/electricity_source_gold.csv"

# Load Silver
df = pd.read_csv(INPUT_FILE)

df["date"] = pd.to_datetime(df["date"])
df["generation_gwh"] = pd.to_numeric(
    df["generation_gwh"],
    errors="coerce"
)

# Remove the overall total and electricity imports.
df = df[
    ~df["source"].str.contains(
        "Total Electricity Generation|imported",
        case=False,
        na=False
    )
].copy()

# Classify energy sources
def classify_source(source):
    source_lower = source.lower()

    if any(x in source_lower for x in [
        "hydel",
        "wind",
        "solar",
        "bagasse"
    ]):
        return "Renewable"

    if "nuclear" in source_lower:
        return "Nuclear"

    if any(x in source_lower for x in [
        "coal",
        "gas",
        "diesel",
        "fuel oil",
        "rfo",
        "mixed"
    ]):
        return "Fossil / Other"

    return "Other"


df["category"] = df["source"].apply(classify_source)

# Add time dimensions
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["month_name"] = df["date"].dt.strftime("%b")

# Keep useful analytics columns
gold = df[
    [
        "date",
        "year",
        "month",
        "month_name",
        "source",
        "category",
        "generation_gwh",
        "unit"
    ]
].copy()

gold = gold.sort_values(
    ["date", "category", "source"]
).reset_index(drop=True)

# Save
Path("Data/Gold").mkdir(
    parents=True,
    exist_ok=True
)

gold.to_csv(
    OUTPUT_FILE,
    index=False
)

# Validation
print("\n--- SOURCE GOLD DATASET ---")
print(gold.head(20))

print("\n--- SHAPE ---")
print(gold.shape)

print("\n--- CATEGORIES ---")
print(gold["category"].value_counts())

print("\n--- SOURCES ---")
print(gold["source"].unique())

print(f"\nSaved to: {OUTPUT_FILE}")