"""
All Pydantic models used in the system.
"""

# ---------------------------
# Imports
# ---------------------------
from typing import Literal

from pydantic import BaseModel


class QuotaForecast(BaseModel):
    """Holds the forecast of one single cost quota over the next six years."""

    quotas: list[float]
    reasoning: str
    confidence: Literal["high", "medium", "low"]


class LLMQuota(BaseModel):
    """Holds one QuotaForecast per cost quota, keyed by the name of the quota column."""

    quotas: dict[str, QuotaForecast]
