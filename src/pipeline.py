import logging
import subprocess
import sys
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PYTHON = sys.executable

# Temporary Docker testing switch.
# False = use existing Raw CSV
# True = run live SBP ingestion
USE_LIVE_INGESTION = False


# ============================================================
# LOGGING
# ============================================================

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "pipeline.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# RUN PIPELINE STEP
# ============================================================

def run_step(name, script):

    logger.info(f"STARTED: {name}")

    print("\n" + "=" * 60)
    print(f"RUNNING: {name}")
    print("=" * 60)

    result = subprocess.run(
        [PYTHON, str(PROJECT_ROOT / script)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )

    # Show the child script's output
    if result.stdout:
        print(result.stdout)

    # Show errors/warnings
    if result.stderr:
        print(result.stderr)

    # Stop pipeline if the step failed
    if result.returncode != 0:

        logger.error(f"FAILED: {name}")

        print(f"\nFAILED: {name}")

        sys.exit(result.returncode)

    logger.info(f"COMPLETED: {name}")

    print(f"\nCOMPLETED: {name}")


# ============================================================
# CLEAN SILVER DATA
# ============================================================

def clean_silver_data():

    silver_path = (
        PROJECT_ROOT
        / "Data"
        / "Silver"
        / "electricity_generation_silver.csv"
    )

    clean_path = (
        PROJECT_ROOT
        / "Data"
        / "Silver"
        / "electricity_generation_silver_clean.csv"
    )

    print("\n" + "=" * 60)
    print("CLEANING SILVER DATA")
    print("=" * 60)

    df = pd.read_csv(silver_path)

    original_rows = len(df)

    # Remove negative generation values
    df = df[
        df["generation_gwh"] >= 0
    ].copy()

    removed_rows = original_rows - len(df)

    df.to_csv(
        clean_path,
        index=False
    )

    logger.info(
        f"DATA CLEANING | "
        f"Original rows: {original_rows} | "
        f"Clean rows: {len(df)} | "
        f"Removed: {removed_rows}"
    )

    print(
        f"Original rows: {original_rows}"
    )

    print(
        f"Clean rows: {len(df)}"
    )

    print(
        f"Removed rows: {removed_rows}"
    )

    print(
        f"Clean dataset: {clean_path}"
    )


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    logger.info(
        "========== PIPELINE STARTED =========="
    )

    print("\n")
    print("=" * 60)
    print("ENERGY DEMAND INTELLIGENCE PIPELINE")
    print("=" * 60)

    try:

        # ====================================================
        # 1. INGESTION
        # ====================================================

        if USE_LIVE_INGESTION:

            run_step(
                "Download Latest SBP Electricity Data",
                "src/ingestion/download_data.py"
            )

        else:

            print("\n" + "=" * 60)
            print("SKIPPING LIVE SBP INGESTION")
            print("Using existing Raw dataset for pipeline test")
            print("=" * 60)

        # ====================================================
        # 2. TRANSFORMATION
        # ====================================================

        run_step(
            "Transform Raw → Silver",
            "src/transformation/transform_electricity.py"
        )

        # ====================================================
        # 3. VALIDATION
        # ====================================================

        run_step(
            "Validate Silver Data",
            "src/validation/validate_data.py"
        )

        # ====================================================
        # 4. CLEANING
        # ====================================================

        clean_silver_data()

        # ====================================================
        # 5. GOLD TABLES
        # ====================================================

        run_step(
            "Create Monthly Gold",
            "src/transformation/create_gold.py"
        )

        run_step(
            "Create Source Gold",
            "src/transformation/create_source_gold.py"
        )

        # ====================================================
        # 6. FORECASTING
        # ====================================================

        run_step(
            "Generate Energy Forecast",
            "src/forecasting/forecast.py"
        )

        # ====================================================
        # 7. INTELLIGENCE
        # ====================================================

        run_step(
            "Generate Intelligence Insights",
            "src/intelligence/generate_insights.py"
        )

        # ====================================================
        # 8. AZURE UPLOADS
        # ====================================================

        run_step(
            "Upload Raw Data to Azure Bronze",
            "src/azure/upload_to_bronze.py"
        )

        run_step(
            "Upload Silver Data to Azure",
            "src/azure/upload_silver.py"
        )

        run_step(
            "Upload Gold Data to Azure",
            "src/azure/upload_gold.py"
        )

        run_step(
            "Upload Source Gold Data to Azure",
            "src/azure/upload_source_gold.py"
        )

        # ====================================================
        # PIPELINE COMPLETE
        # ====================================================

        logger.info(
            "========== PIPELINE COMPLETED SUCCESSFULLY =========="
        )

        print("\n" + "=" * 60)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as e:

        logger.exception(
            f"PIPELINE FAILED: {e}"
        )

        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()