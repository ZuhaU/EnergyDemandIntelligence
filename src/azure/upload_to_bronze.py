import os
from dotenv import load_dotenv
from azure.storage.filedatalake import DataLakeServiceClient

# Load environment variables
load_dotenv()

print("Account:", os.getenv("AZURE_STORAGE_ACCOUNT"))
print("Key exists:", os.getenv("AZURE_STORAGE_KEY") is not None)

ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT")
ACCOUNT_KEY = os.getenv("AZURE_STORAGE_KEY")
FILE_SYSTEM = "1bronze"

LOCAL_FILE = "Data/Raw/Generation of Electricity by Sector.csv"
TARGET_FILE = "Generation of Electricity by Sector.csv"

# Connect to Azure
service_client = DataLakeServiceClient(
    account_url=f"https://{ACCOUNT_NAME}.dfs.core.windows.net",
    credential=ACCOUNT_KEY
)

filesystem_client = service_client.get_file_system_client(FILE_SYSTEM)

file_client = filesystem_client.get_file_client(TARGET_FILE)

with open(LOCAL_FILE, "rb") as file:
    file_client.upload_data(file, overwrite=True)

print("✅ Raw dataset uploaded successfully to Bronze!")