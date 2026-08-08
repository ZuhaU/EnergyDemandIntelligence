import os
from pathlib import Path
from dotenv import load_dotenv
from azure.storage.filedatalake import DataLakeServiceClient

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT")
ACCOUNT_KEY = os.getenv("AZURE_STORAGE_KEY")

FILE_SYSTEM = "1gold"

LOCAL_FILE = "Data/Gold/electricity_source_gold.csv"
TARGET_FILE = "electricity_source_gold.csv"

service_client = DataLakeServiceClient(
    account_url=f"https://{ACCOUNT_NAME}.dfs.core.windows.net",
    credential=ACCOUNT_KEY
)

filesystem_client = service_client.get_file_system_client(FILE_SYSTEM)
file_client = filesystem_client.get_file_client(TARGET_FILE)

with open(LOCAL_FILE, "rb") as file:
    file_client.upload_data(file, overwrite=True)

print("✅ Source Gold dataset uploaded successfully to Azure!")