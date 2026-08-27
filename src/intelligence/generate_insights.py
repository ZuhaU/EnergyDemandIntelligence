from pathlib import Path
import json
import subprocess

import pandas as pd
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GOLD_FILE = (
    PROJECT_ROOT
    / "Data"
    / "Gold"
    / "electricity_monthly_gold.csv"
)

FORECAST_FILE = (
    PROJECT_ROOT
    / "Data"
    / "Gold"
    / "forecast_evaluation.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "Data"
    / "Intelligence"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "insights.csv"
)

OLLAMA_MODEL = "phi3:mini"


# ============================================================
# LOAD DATA
# ============================================================

def load_gold_data():

    df = pd.read_csv(GOLD_FILE)

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values("date").reset_index(drop=True)

    return df


def load_forecast_data():

    if not FORECAST_FILE.exists():

        print("WARNING: Forecast file not found.")

        return pd.DataFrame()

    df = pd.read_csv(FORECAST_FILE)

    print(f"Forecast rows loaded: {len(df)}")

    return df


# ============================================================
# TREND INTELLIGENCE
# ============================================================

def detect_trends(df):

    insights = []

    if len(df) < 2:
        return insights

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    # --------------------------------------------------------
    # Total generation MoM
    # --------------------------------------------------------

    previous_total = previous["total_generation_gwh"]
    current_total = latest["total_generation_gwh"]

    if previous_total != 0:

        mom = (
            (current_total - previous_total)
            / previous_total
            * 100
        )

        if abs(mom) >= 3:

            direction = (
                "increased"
                if mom > 0
                else "decreased"
            )

            severity = (
                "Positive"
                if mom > 0
                else "Warning"
            )

            insights.append({
                "date": latest["date"],
                "type": "Trend",
                "category": "Total Generation",
                "severity": severity,
                "metric": "total_generation_gwh",
                "value": current_total,
                "change_pct": mom,
                "z_score": np.nan,
                "title": (
                    f"Total generation {direction}"
                ),
            })

    # --------------------------------------------------------
    # YoY growth
    # --------------------------------------------------------

    yoy = latest.get("yoy_growth_pct")

    if pd.notna(yoy):

        if abs(yoy) >= 5:

            direction = (
                "growth"
                if yoy > 0
                else "decline"
            )

            insights.append({
                "date": latest["date"],
                "type": "YoY",
                "category": "Total Generation",
                "severity": (
                    "Positive"
                    if yoy > 0
                    else "Warning"
                ),
                "metric": "yoy_growth_pct",
                "value": yoy,
                "change_pct": yoy,
                "z_score": np.nan,
                "title": (
                    f"Year-over-year {direction} detected"
                ),
            })

    # --------------------------------------------------------
    # Renewable share
    # --------------------------------------------------------

    current_share = latest[
        "renewable_share_pct"
    ]

    previous_share = previous[
        "renewable_share_pct"
    ]

    share_change = (
        current_share - previous_share
    )

    if abs(share_change) >= 2:

        direction = (
            "increased"
            if share_change > 0
            else "decreased"
        )

        insights.append({
            "date": latest["date"],
            "type": "Renewables",
            "category": "Renewable Share",
            "severity": (
                "Positive"
                if share_change > 0
                else "Warning"
            ),
            "metric": "renewable_share_pct",
            "value": current_share,
            "change_pct": share_change,
            "z_score": np.nan,
            "title": (
                f"Renewable share {direction}"
            ),
        })

    return insights


# ============================================================
# ANOMALY DETECTION
# ============================================================

def detect_anomalies(df):

    insights = []

    if len(df) < 13:
        return insights

    latest = df.iloc[-1]

    history = df.iloc[-13:-1]

    mean = history[
        "total_generation_gwh"
    ].mean()

    std = history[
        "total_generation_gwh"
    ].std()

    if std == 0 or pd.isna(std):
        return insights

    z_score = (
        latest["total_generation_gwh"] - mean
    ) / std

    if abs(z_score) >= 2:

        direction = (
            "above"
            if z_score > 0
            else "below"
        )

        insights.append({
            "date": latest["date"],
            "type": "Anomaly",
            "category": "Total Generation",
            "severity": "Warning",
            "metric": "total_generation_gwh",
            "value": latest["total_generation_gwh"],
            "change_pct": np.nan,
            "z_score": z_score,
            "title": (
                f"Generation unusually {direction} "
                "recent baseline"
            ),
        })

    return insights


# ============================================================
# HISTORICAL EXTREMES
# ============================================================

def detect_extremes(df):

    insights = []

    latest = df.iloc[-1]

    max_generation = df[
        "total_generation_gwh"
    ].max()

    min_generation = df[
        "total_generation_gwh"
    ].min()

    if latest["total_generation_gwh"] == max_generation:

        insights.append({
            "date": latest["date"],
            "type": "Milestone",
            "category": "Total Generation",
            "severity": "Positive",
            "metric": "total_generation_gwh",
            "value": latest["total_generation_gwh"],
            "change_pct": np.nan,
            "z_score": np.nan,
            "title": "Historical generation high",
        })

    if latest["total_generation_gwh"] == min_generation:

        insights.append({
            "date": latest["date"],
            "type": "Milestone",
            "category": "Total Generation",
            "severity": "Warning",
            "metric": "total_generation_gwh",
            "value": latest["total_generation_gwh"],
            "change_pct": np.nan,
            "z_score": np.nan,
            "title": "Historical generation low",
        })

    return insights


# ============================================================
# FORECAST INTELLIGENCE
# ============================================================

def analyze_forecast(forecast_df):

    insights = []

    if forecast_df.empty:
        return insights

    required = [
        "date",
        "actual_gwh",
        "predicted_gwh",
        "absolute_error_gwh",
    ]

    if not all(
        column in forecast_df.columns
        for column in required
    ):

        print(
            "Forecast evaluation file does not contain "
            "the expected columns."
        )

        return insights

    forecast_df["date"] = pd.to_datetime(
        forecast_df["date"],
        errors="coerce",
    )

    forecast_df["actual_gwh"] = pd.to_numeric(
        forecast_df["actual_gwh"],
        errors="coerce",
    )

    forecast_df["predicted_gwh"] = pd.to_numeric(
        forecast_df["predicted_gwh"],
        errors="coerce",
    )

    forecast_df["absolute_error_gwh"] = pd.to_numeric(
        forecast_df["absolute_error_gwh"],
        errors="coerce",
    )

    forecast_df = forecast_df.dropna(
        subset=[
            "date",
            "actual_gwh",
            "predicted_gwh",
            "absolute_error_gwh",
        ]
    )

    if forecast_df.empty:
        return insights

    forecast_df = forecast_df.sort_values(
        "date"
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # Latest forecast error
    # --------------------------------------------------------

    latest = forecast_df.iloc[-1]

    actual = latest["actual_gwh"]
    predicted = latest["predicted_gwh"]

    if actual != 0:

        error_pct = (
            (predicted - actual)
            / actual
            * 100
        )

        if abs(error_pct) >= 5:

            direction = (
                "overestimated"
                if error_pct > 0
                else "underestimated"
            )

            insights.append({
                "date": latest["date"],
                "type": "Forecast",
                "category": "Forecast Accuracy",
                "severity": "Warning",
                "metric": "predicted_gwh",
                "value": predicted,
                "change_pct": error_pct,
                "z_score": np.nan,
                "title": (
                    f"Forecast {direction} actual generation"
                ),
            })

    # --------------------------------------------------------
    # Overall forecast accuracy
    # --------------------------------------------------------

    mean_actual = forecast_df[
        "actual_gwh"
    ].mean()

    mean_error = forecast_df[
        "absolute_error_gwh"
    ].mean()

    if mean_actual != 0:

        mean_error_pct = (
            mean_error
            / mean_actual
            * 100
        )

        insights.append({
            "date": latest["date"],
            "type": "Forecast",
            "category": "Forecast Accuracy",
            "severity": (
                "Positive"
                if mean_error_pct < 10
                else "Warning"
            ),
            "metric": "mae_gwh",
            "value": mean_error,
            "change_pct": mean_error_pct,
            "z_score": np.nan,
            "title": (
                f"Forecast mean error is "
                f"{mean_error_pct:.1f}% of actual generation"
            ),
        })

    return insights


# ============================================================
# OLLAMA AI SUMMARY
# ============================================================

def generate_ai_explanation(insights):

    if not insights:
        return "No significant insights detected."

    facts = []

    for item in insights:

        facts.append({
            "type": item["type"],
            "category": item["category"],
            "severity": item["severity"],
            "title": item["title"],
            "value": (
                None
                if pd.isna(item["value"])
                else round(float(item["value"]), 2)
            ),
            "change_pct": (
                None
                if pd.isna(item["change_pct"])
                else round(float(item["change_pct"]), 2)
            ),
            "z_score": (
                None
                if pd.isna(item["z_score"])
                else round(float(item["z_score"]), 2)
            ),
        })

    prompt = f"""
You are an electricity analytics assistant.

Summarize ONLY the verified findings provided below.

STRICT RULES:
- Use ONLY the supplied findings.
- Do not invent facts.
- Do not invent statistics.
- Do not create dates or time periods.
- Do not add economic, seasonal, infrastructure, or policy claims
  unless they appear explicitly in the findings.
- Do not calculate new numbers.
- Preserve all supplied percentages exactly.
- Do not change 7.07% into another value.
- Distinguish forecast accuracy from future forecasts.
- Mention only the 2 or 3 most important findings.
- Write exactly 2 or 3 sentences.
- Use concise professional language.

VERIFIED FINDINGS:
{json.dumps(facts, indent=2)}

Write the executive summary now.
"""

    print()
    print("Running Ollama AI summarization...")

    try:

        result = subprocess.run(
            [
                "ollama",
                "run",
                OLLAMA_MODEL,
                prompt,
            ],
            capture_output=True,
            text=True,
            timeout=120,
            encoding="utf-8",
            errors="replace",
        )

        if result.returncode != 0:

            print("WARNING: Ollama failed.")

            if result.stderr:
                print(result.stderr)

            return "AI summary unavailable."

        output = result.stdout.strip()

        if not output:

            print(
                "WARNING: Ollama returned an empty response."
            )

            return "AI summary unavailable."

        # Remove ANSI terminal escape sequences
        import re

        output = re.sub(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])",
            "",
            output,
        )

        # Remove accidental terminal control characters
        output = "".join(
            char
            for char in output
            if char.isprintable()
            or char in "\n\r\t"
        )

        return output.strip()

    except FileNotFoundError:

        print(
            "WARNING: Ollama executable was not found."
        )

        print(
            "Make sure Ollama is installed and available "
            "in your PATH."
        )

        return "AI summary unavailable."

    except subprocess.TimeoutExpired:

        print(
            "WARNING: Ollama timed out."
        )

        return "AI summary unavailable."

    except Exception as exc:

        print(
            f"WARNING: Could not run Ollama: {exc}"
        )

        return "AI summary unavailable."


# ============================================================
# MAIN
# ============================================================

def generate_insights():

    print()
    print("=" * 60)
    print("ENERGY INTELLIGENCE ENGINE")
    print("=" * 60)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    df = load_gold_data()

    forecast_df = load_forecast_data()

    print(f"Gold rows: {len(df)}")

    # --------------------------------------------------------
    # Generate insights
    # --------------------------------------------------------

    insights = []

    insights.extend(
        detect_trends(df)
    )

    insights.extend(
        detect_anomalies(df)
    )

    insights.extend(
        detect_extremes(df)
    )

    insights.extend(
        analyze_forecast(forecast_df)
    )

    # --------------------------------------------------------
    # Output directory
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Create output
    # --------------------------------------------------------

    if insights:

        result = pd.DataFrame(
            insights
        )

        # ----------------------------------------------------
        # Generate one AI explanation
        # ----------------------------------------------------

        explanation = generate_ai_explanation(
            insights
        )

        result["ai_explanation"] = explanation

    else:

        result = pd.DataFrame(
            columns=[
                "date",
                "type",
                "category",
                "severity",
                "metric",
                "value",
                "change_pct",
                "z_score",
                "title",
                "ai_explanation",
            ]
        )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    result.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    # --------------------------------------------------------
    # Console output
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("INTELLIGENCE ANALYSIS COMPLETE")
    print("=" * 60)

    print(
        f"Insights generated: {len(result)}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    if not result.empty:

        print()

        print(
            result[
                [
                    "type",
                    "category",
                    "severity",
                    "title",
                ]
            ].to_string(
                index=False
            )
        )

        print()
        print("AI SUMMARY:")
        print(
            result[
                "ai_explanation"
            ].iloc[0]
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    generate_insights()