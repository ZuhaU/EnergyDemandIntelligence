import logging
import subprocess
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PYTHON = sys.executable

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "pipeline.log"


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


def run_step(name, script):
    logger.info(f"STARTED: {name}")

    print("\n" + "=" * 60)
    print(f"RUNNING: {name}")
    print("=" * 60)

    result = subprocess.run(
        [PYTHON, str(PROJECT_ROOT / script)],
        cwd=PROJECT_ROOT
    )

    if result.returncode != 0:
        logger.error(f"FAILED: {name}")
        print(f"\nFAILED: {name}")
        sys.exit(result.returncode)

    logger.info(f"COMPLETED: {name}")
    print(f"\nCOMPLETED: {name}")


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

    df = pd.read_csv(silver_path)

    original_rows = len(df)

    df = df[df["generation_gwh"] >= 0].copy()

    removed_rows = original_rows - len(df)

    df.to_csv(clean_path, index=False)

    logger.info(
        f"DATA CLEANING | Original rows: {original_rows} | "
        f"Clean rows: {len(df)} | Removed: {removed_rows}"
    )

    print(
        f"\nCleaning complete."
        f"\nOriginal rows: {original_rows}"
        f"\nClean rows: {len(df)}"
        f"\nRemoved rows: {removed_rows}"
    )


def main():

    logger.info("========== PIPELINE STARTED ==========")

    try:

        run_step(
            "Transform Raw → Silver",
            "src/transformation/transform_electricity.py"
        )

        run_step(
            "Validate Silver Data",
            "src/validation/validate_data.py"
        )

        clean_silver_data()

        run_step(
            "Create Monthly Gold",
            "src/transformation/create_gold.py"
        )

        run_step(
            "Create Source Gold",
            "src/transformation/create_source_gold.py"
        )
        run_step(
            "Generate Energy Forecast",
            "src/forecasting/forecast.py"
    )

        logger.info("========== PIPELINE COMPLETED SUCCESSFULLY ==========")

        print("\n" + "=" * 60)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as e:

        logger.exception(f"PIPELINE FAILED: {e}")
        raise


if __name__ == "__main__":
    main()