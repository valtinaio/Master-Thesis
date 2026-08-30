from datetime import date, timedelta

from pydantic import BaseModel, EmailStr, Field, field_validator


class DataImportSchema(BaseModel):
    """Input parameters for the data import sub-graph."""

    ticker_symbol: str
    # default_factory runs at instance creation, so the dates are always relative to today.
    start_date: date = Field(
        default_factory=lambda: date.today() - timedelta(days=1) - timedelta(days=365 * 5)
    )
    end_date: date = Field(default_factory=lambda: date.today() - timedelta(days=1))
    stock_price_endpoint: str = (
        "https://financialmodelingprep.com/stable/historical-price-eod/dividend-adjusted"
    )
    user_agent_mail: EmailStr
    start_date_news: date = Field(
        default_factory=lambda: date.today() - timedelta(days=1) - timedelta(days=180)
    )

    @field_validator("ticker_symbol")   # Through this decorator the classmethod down below gets used when ticker_symbol gets set
    @classmethod
    def uppercase_ticker_symbol(cls, value: str) -> str:
        """Normalizes the ticker symbol to uppercase."""
        return value.upper()
