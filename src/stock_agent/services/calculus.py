"""
Service to perform calculations on financial data provided as a pandas DataFrame.
"""

# ---------------------------
# Imports
# ---------------------------
import pandas as pd


class Calculus:
    """Performs calculations on one financial data set given as a DataFrame."""

    def __init__(self, data: pd.DataFrame):
        self.data = data

    def get_growth_rate(self):
        """Calculate the period-over-period growth rate of the single value column.
        Returns a copy of the DataFrame with the growth rate appended as a new column."""

        if "date" in self.data.columns and len(self.data.columns) == 2:
            df = self.data.copy()
            # The one column that is not "date" holds the values to compare.
            value_column = [column for column in df.columns if column != "date"][0]
            # shift(1) moves every value one row down, so each row can access its predecessor (t-1).
            previous = df[value_column].shift(1)
            df[value_column + "_growth_rate"] = (df[value_column] - previous) / previous
            return df
        else:
            raise ValueError(
                "The date-column is missing or you have more than two columns in your pd.DataFrame"
            )
