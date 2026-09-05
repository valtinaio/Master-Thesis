"""
Service to import any available stock data from the Financial Modeling Prep (FMP) API.
This is the primary data source; `sec_api.py` is only the fallback for data FMP does not provide.
"""

# ---------------------------
# Imports
# ---------------------------
import pandas as pd
import requests

from stock_agent.config import FMP_API_KEY

class FMP:
    """Imports stock data of one symbol from the FMP API; every method fetches on demand."""

    def __init__(self, symbol: str):
        """Store the symbol, the API key and the endpoint URLs without performing any request."""

        self.symbol = str(symbol).upper()
        self._api_key = FMP_API_KEY
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
