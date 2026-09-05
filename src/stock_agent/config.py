import os
from pathlib import Path
from dotenv import load_dotenv

# Loading .env file
ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

# Reading relevant keys
FMP_API_KEY = os.environ["FMP_API_KEY"]