import os
from pathlib import Path
from dotenv import load_dotenv
from azure.storage.filedatalake import DataLakeServiceClient

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT")
ACCOUNT_KEY = os.getenv("AZURE_STORAGE_KEY")

FILE_SYSTEM = "1gold"

service_client = DataLakeServiceClient(
    account_url=f"https://{ACCOUNT_NAME}.dfs.core.windows.net",
    credential=ACCOUNT_KEY
)

filesystem_client = service_client.get_file_system_client(FILE_SYSTEM)

# -------------------------
# Monthly Gold
# -------------------------

LOCAL_FILE = "Data/Gold/electricity_monthly_gold.csv"
TARGET_FILE = "electricity_monthly_gold.csv"

file_client = filesystem_client.get_file_client(TARGET_FILE)

with open(LOCAL_FILE, "rb") as file:
    file_client.upload_data(file, overwrite=True)

print("✅ Monthly Gold uploaded successfully!")


# -------------------------
# Forecast Gold
# -------------------------

FORECAST_LOCAL_FILE = "Data/Gold/electricity_generation_forecast.csv"
FORECAST_TARGET_FILE = "electricity_generation_forecast.csv"

forecast_client = filesystem_client.get_file_client(
    FORECAST_TARGET_FILE
)

with open(FORECAST_LOCAL_FILE, "rb") as file:
    forecast_client.upload_data(file, overwrite=True)

print("✅ Forecast Gold uploaded successfully!")