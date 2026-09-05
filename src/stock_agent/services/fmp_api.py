"""
Service to import any available stock data from the Financial Modeling Prep (FMP) API.
This is the primary data source; `sec_api.py` is only the fallback for data FMP does not provide.
"""

# ---------------------------
# Imports
# ---------------------------
import os
from pathlib import Path
from typing import Literal

import pandas as pd
import requests
from dotenv import load_dotenv

# The .env file lives in the "codes" folder, which is the parent of the "services" folder.
# Deriving the path from this file keeps the code working on Windows and macOS alike.
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

# The FMP Starter plan provides five years of history, so five is the default everywhere.
DEFAULT_LIMIT = 5

# The type alias makes the allowed argument values visible in every method signature.
Period = Literal["FY", "quarter"]


class FMPError(Exception):
    """Raised when an FMP request fails, naming the endpoint and the reason."""


class FMP:
    """Imports stock data of one symbol from the FMP API; every method fetches on demand."""

    def __init__(self, symbol: str):
        """Store the symbol, the API key and the endpoint URLs without performing any request."""

        self.symbol = str(symbol).upper()
        self._api_key = os.getenv("FMP_API_KEY")
        self._endpoints = [
            "https://financialmodelingprep.com/stable/income-statement",
            "https://financialmodelingprep.com/stable/balance-sheet-statement",
            "https://financialmodelingprep.com/stable/cash-flow-statement",
            "https://financialmodelingprep.com/stable/profile",
            "https://financialmodelingprep.com/stable/quote",
            "https://financialmodelingprep.com/stable/shares-float",
            "https://financialmodelingprep.com/stable/treasury-rates",
        ]

    def get_income_statement(self, period: str, limit: int):
        """Fetch the income statements of the symbol from FMP.
        Returns them as a DataFrame sorted by date in ascending order."""

        try:
            response = requests.get(
                self._endpoints[0],
                params={
                    "symbol": self.symbol,
                    "period": period,
                    "limit": limit,
                    "apikey": self._api_key,
                },
            )
            # Turns any HTTP error status (for example 401 or 404) into an exception.
            response.raise_for_status()
            data = response.json()
            # Every dict in the list becomes one row and every key becomes one column.
            df = pd.DataFrame(data)
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date", ascending=True).reset_index(drop=True)
            return df
        except Exception:
            raise


if __name__ == "__main__":
    fmp = FMP("AAPL")
    df = fmp.get_income_statement(period="FY", limit=5)
    print(df)
