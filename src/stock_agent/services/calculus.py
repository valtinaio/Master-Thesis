"""
Service to perform calculations on financial data provided as a pandas DataFrame.
"""

# ---------------------------
# Imports
# ---------------------------
import pandas as pd
from stock_agent.config import LONGTERM_GROWTH_RATE


class Calculus:
    """Performs calculations on one financial data set given as a DataFrame."""

    def __init__(self, data: pd.DataFrame):
        self.data = data

    def get_growth_rate(self, column: str):
        """Calculate the period-over-period growth rate of the given value column.
        Returns a DataFrame with the date, the value column and its growth rate."""

        if "date" in self.data.columns and column in self.data.columns:
            df = self.data[["date", column]].copy()
            # shift(1) moves every value one row down, so each row can access its predecessor (t-1).
            previous = df[column].shift(1)
            df[column + "_growth_rate"] = (df[column] - previous) / previous
            return df
        else:
            raise ValueError(
                f"The date-column or the column '{column}' is missing in your pd.DataFrame"
            )

    def get_CAGR(self, column: str):
        """Calculate the compound annual growth rate (CAGR) of the given value column.
        Returns a DataFrame with one row holding the date period and the CAGR."""

        if "date" in self.data.columns and column in self.data.columns:
            start_value = self.data[column].iloc[0]
            end_value = self.data[column].iloc[-1]
            start_date = self.data["date"].iloc[0]
            end_date = self.data["date"].iloc[-1]
            periods = len(self.data) - 1
            # The CAGR is the constant growth rate that turns the start value into the end value.
            cagr = (end_value / start_value) ** (1 / periods) - 1
            return pd.DataFrame(
                {
                    "period": [f"{start_date} - {end_date}"],
                    column + "_CAGR": [cagr],
                }
            )
        else:
            raise ValueError(
                f"The date-column or the column '{column}' is missing in your pd.DataFrame"
            )

    def get_CAGR_prediction_plus_one(self, column: str, CAGR: float):
        """Project the given value column five years ahead with a constant CAGR
        plus one further year grown with the long-run rate.
        Returns a DataFrame with the last observed year, five CAGR years and year +6."""

        if "date" in self.data.columns and column in self.data.columns:
            start_value = self.data[column].iloc[-1]
            start_date = self.data["date"].iloc[-1]
            dates = [start_date]
            values = [start_value]
            # Each forecast year grows the previous year by the CAGR, so the growth compounds.
            for year in range(1, 6):
                dates.append(start_date + pd.DateOffset(years=year))
                values.append(values[-1] * (1 + CAGR))
            # Year +6 is the long-run state and grows with the economy, not with the firm's own CAGR.
            dates.append(start_date + pd.DateOffset(years=6))
            values.append(values[-1] * (1 + LONGTERM_GROWTH_RATE))
            return pd.DataFrame(
                {
                    "date": dates,
                    column + "_CAGR_prediction": values,
                }
            )
        else:
            raise ValueError(
                f"The date-column or the column '{column}' is missing in your pd.DataFrame"
            )
