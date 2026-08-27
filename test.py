import os
import requests
from dotenv import load_dotenv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("SBP_API_KEY")

if not API_KEY:
    raise RuntimeError("SBP_API_KEY was not found")
url = "https://easydata.sbp.org.pk/api/v1/series/TS_GP_RLS_ELECGEN_M.E_001000/data"

params = {
    "api_key": API_KEY,
    "start_date": "2012-07-01",
    "format": "json",
}

response = requests.get(url, params=params, timeout=60)

print("Status:", response.status_code)
print("Response:", response.text[:1000])