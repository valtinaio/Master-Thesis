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
        """Store the symbol and the API key without performing any request."""

        self.symbol = str(symbol).upper()
        self._api_key = os.getenv("FMP_API_KEY")
        self._base_url = "https://financialmodelingprep.com/stable/"

    # ---------------------------
    # Internal request helper
    # ---------------------------
    def _get(self, endpoint: str, **params) -> list | dict:
        """Send one GET request to an FMP endpoint and return the parsed JSON."""

        # Every FMP call needs the API key; most also need the symbol.
        params["apikey"] = self._api_key
        params.setdefault("symbol", self.symbol) # adds the symbol key with value self.symbol if symbol as an argument is missing.
        # Arguments left as None are optional ones the caller did not set.
        params = {key: value for key, value in params.items() if value is not None}

        response = requests.get(self._base_url + endpoint, params=params)
        if response.status_code != 200:
            raise FMPError(f"'{endpoint}' failed with HTTP {response.status_code}: {response.text[:200]}")

        data = response.json()
        # FMP reports problems as a JSON object with an error key instead of an HTTP error.
        if isinstance(data, dict) and ("Error Message" in data or "error" in data):
            raise FMPError(f"'{endpoint}' returned an error: {data}")
        return data

    # ---------------------------
    # Financial statements
    # ---------------------------
    def get_income_statement(self, period: Period = "FY", limit: int = DEFAULT_LIMIT) -> list[dict]:
        """Return the income statements, one dictionary per reporting period."""

        return self._get("income-statement", period=period, limit=limit)

    def get_balance_sheet(self, period: Period = "FY", limit: int = DEFAULT_LIMIT) -> list[dict]:
        """Return the balance sheet statements, one dictionary per reporting period."""

        return self._get("balance-sheet-statement", period=period, limit=limit)

    def get_cash_flow(self, period: Period = "FY", limit: int = DEFAULT_LIMIT) -> list[dict]:
        """Return the cash flow statements, one dictionary per reporting period."""

        return self._get("cash-flow-statement", period=period, limit=limit)

    # ---------------------------
    # Fundamentals derived from the statements
    # ---------------------------
    def get_key_metrics(self, period: Period = "FY", limit: int = DEFAULT_LIMIT) -> list[dict]:
        """Return key metrics per period, such as per-share and return figures."""

        return self._get("key-metrics", period=period, limit=limit)

    def get_financial_ratios(self, period: Period = "FY", limit: int = DEFAULT_LIMIT) -> list[dict]:
        """Return the financial ratios per period, such as margins and turnover ratios."""

        return self._get("ratios", period=period, limit=limit)

    def get_enterprise_values(self, period: Period = "FY", limit: int = DEFAULT_LIMIT) -> list[dict]:
        """Return the enterprise value per period, including market capitalization and debt."""

        return self._get("enterprise-values", period=period, limit=limit)

    # ---------------------------
    # Company and market data
    # ---------------------------
    def get_profile(self) -> list[dict]:
        """Return the company profile, including sector, industry, beta and description."""

        return self._get("profile")

    def get_quote(self) -> list[dict]:
        """Return the current quote, including the latest share price."""

        return self._get("quote")

    def get_market_cap(self) -> list[dict]:
        """Return the current market capitalization."""

        return self._get("market-capitalization")

    def get_shares_float(self) -> list[dict]:
        """Return the free float and the number of outstanding shares."""

        return self._get("shares-float")

    def get_peers(self) -> list[dict]:
        """Return comparable companies of the same industry."""

        return self._get("stock-peers")

    # ---------------------------
    # Price data
    # ---------------------------
    def get_price_history(self,
                          from_date: str,
                          to_date: str,
                          adjusted: bool = True) -> list[dict]:
        """Return the end-of-day prices between two dates, each formatted as 'YYYY-MM-DD'.
        The adjusted series uses the keys 'adjOpen' to 'adjClose', the unadjusted one 'open' to 'close'."""

        # The dividend-adjusted series is the correct basis for return calculations.
        endpoint = "historical-price-eod/dividend-adjusted" if adjusted else "historical-price-eod/full"
        return self._get(endpoint, **{"from": from_date, "to": to_date})

    def get_dividends(self, limit: int = DEFAULT_LIMIT) -> list[dict]:
        """Return the dividend history of the symbol."""

        return self._get("dividends", limit=limit)

    def get_splits(self, limit: int = DEFAULT_LIMIT) -> list[dict]:
        """Return the share split history of the symbol."""

        return self._get("splits", limit=limit)

    # ---------------------------
    # Analyst and macroeconomic data
    # ---------------------------
    def get_analyst_estimates(self,
                              period: Literal["annual", "quarter"] = "annual",
                              limit: int = DEFAULT_LIMIT) -> list[dict]:
        """Return the analyst estimates for revenue, earnings and EPS."""

        return self._get("analyst-estimates", period=period, limit=limit)

    def get_price_targets(self) -> list[dict]:
        """Return the summarized analyst price targets of the symbol."""

        return self._get("price-target-summary")

    def get_earnings_surprises(self, limit: int = DEFAULT_LIMIT) -> list[dict]:
        """Return the reported earnings against the estimated earnings per period."""

        return self._get("earnings", limit=limit)

    def get_analyst_grades(self) -> list[dict]:
        """Return the buy, hold and sell ratings that analysts assigned to the symbol."""

        return self._get("grades")

    def get_news(self, limit: int = DEFAULT_LIMIT) -> list[dict]:
        """Return the latest news articles about the symbol, newest first."""

        # This endpoint expects the parameter "symbols", so the default "symbol" is
        # switched off to keep it out of the request.
        return self._get("news/stock", symbol=None, symbols=self.symbol, limit=limit)

    def get_treasury_rates(self, from_date: str, to_date: str) -> list[dict]:
        """Return the US treasury rates between two dates, each formatted as 'YYYY-MM-DD'."""

        # Treasury rates are macroeconomic data and therefore not bound to a symbol.
        return self._get("treasury-rates", symbol=None, **{"from": from_date, "to": to_date})


if __name__ == "__main__":
    starbucks = FMP("SBUX")
    print("Fiscal years:", [entry["date"] for entry in starbucks.get_income_statement()])
    print("Beta:", starbucks.get_profile()[0]["beta"])
    print("Shares outstanding:", starbucks.get_shares_float()[0]["outstandingShares"])
    print("Price on 2024-01-02:", starbucks.get_price_history("2024-01-01", "2024-01-10")[-1])
    latest_article = starbucks.get_news(limit=1)[0]
    print("News:", latest_article["publishedDate"], "|", latest_article["title"])
