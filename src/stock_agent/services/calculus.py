"""
Service to perform calculations on financial data provided as a pandas DataFrame.
"""

# ---------------------------
# Imports
# ---------------------------
from pathlib import Path

import pandas as pd

from stock_agent.config import LONGTERM_GROWTH_RATE
from stock_agent.pydantic_models.pydantic_models import LLMQuota
from stock_agent.services.llm_call import LLMCall

# Expenses may miss this share of revenue before the column choice counts as wrong.
EXPENSES_TOLERANCE = 0.005

# The model gets the role here; the task itself is described in prompts/llm_quota.md.
SYSTEM_PROMPT_QUOTA = (
    "You are a professional stock analyst, searching for profitable investment possibilities."
)


class Calculus:
    """Performs calculations on one financial data set given as a DataFrame."""

    def __init__(self, data_raw: pd.DataFrame):
        self.data_raw = data_raw
        self.data_calculated = pd.DataFrame({"date": self.data_raw["date"]})
        # The forecast starts after the last observed year and covers the next six years.
        last_date = self.data_raw["date"].iloc[-1]
        self.data_predictions = pd.DataFrame(
            {"date": [last_date + pd.DateOffset(years=year) for year in range(1, 7)]}
        )
        self.cagr = None
        self.llm_quota_response = None

    def get_growth_rate(self, column: str):
        """Calculate the period-over-period growth rate of the given value column.
        Adds the growth rate as a new column to self.data_calculated."""

        if "date" in self.data_raw.columns and column in self.data_raw.columns:
            # shift(1) moves every value one row down, so each row can access its predecessor (t-1).
            previous = self.data_raw[column].shift(1)
            self.data_calculated[column + "_growth_rate"] = (
                self.data_raw[column] - previous
            ) / previous
        else:
            raise ValueError(
                f"The date-column or the column '{column}' is missing in your pd.DataFrame"
            )

    def get_CAGR(self, column: str):
        """Calculate the compound annual growth rate (CAGR) of the given value column.
        Adds the CAGR as a new column to self.cagr."""

        if "date" in self.data_raw.columns and column in self.data_raw.columns:
            start_value = self.data_raw[column].iloc[0]
            end_value = self.data_raw[column].iloc[-1]
            start_date = self.data_raw["date"].iloc[0]
            end_date = self.data_raw["date"].iloc[-1]
            periods = len(self.data_raw) - 1
            # The CAGR is the constant growth rate that turns the start value into the end value.
            cagr = (end_value / start_value) ** (1 / periods) - 1
            period = f"{start_date} - {end_date}"
            if self.cagr is None:
                self.cagr = pd.DataFrame({"period": [period]})
            # Every CAGR in self.cagr must cover the same period, otherwise they are not comparable.
            elif self.cagr["period"].iloc[0] != period:
                raise Exception(
                    "You calculated a CAGR with a period different to the existing CAGR"
                )
            self.cagr[column + "_CAGR"] = [cagr]
            return None
        else:
            raise ValueError(
                f"The date-column or the column '{column}' is missing in your pd.DataFrame"
            )

    def get_CAGR_prediction_plus_one(self, column: str):
        """Project the given value column five years ahead with the CAGR from self.cagr
        plus one further year grown with the long-run rate.
        Adds the six forecast values as a new column to self.data_predictions."""

        if self.cagr is None or column + "_CAGR" not in self.cagr.columns:
            raise ValueError(f"You must calculate the CAGR of {column} first")

        if "date" in self.data_raw.columns and column in self.data_raw.columns:
            cagr = self.cagr[column + "_CAGR"].iloc[0]
            # The last observed value is only the basis of the forecast and is not part of it.
            previous_value = self.data_raw[column].iloc[-1]
            values = []
            # Each forecast year grows the previous year by the CAGR, so the growth compounds.
            for _ in range(5):
                previous_value = previous_value * (1 + cagr)
                values.append(previous_value)
            # Year +6 is the long-run state and grows with the economy, not with the firm's own CAGR.
            values.append(previous_value * (1 + LONGTERM_GROWTH_RATE))
            self.data_predictions[column + "_CAGR_prediction"] = values
        else:
            raise ValueError(
                f"The date-column or the column '{column}' is missing in your pd.DataFrame"
            )

    def get_expenses_quota(self, columns_costs: list):
        """Calculate the common-size quota of several expense columns relative to revenue.
        Adds one quota column per expense column to self.data_calculated."""

        # Revenue minus all operating expenses must give the reported operating income.
        # A large leftover means an expense is counted twice or one is missing. Small
        # leftovers happen because FMP does not map every reported line into a column,
        # so the difference is measured relative to revenue and printed per year.
        check = (
            self.data_raw["revenue"]
            - self.data_raw[columns_costs].sum(axis=1)
            - self.data_raw["operatingIncome"]
        )
        deviation = (check / self.data_raw["revenue"]).abs()
        if (deviation > EXPENSES_TOLERANCE).any():
            raise Exception("Your choice of expenses are not correct - check them.")
        for date, share in zip(self.data_raw["date"], deviation):
            print(f"Expense check {date.year}: {share:.4%} of revenue unexplained")

        if (
            "date" in self.data_raw.columns
            and "revenue" in self.data_raw.columns
            # all() is True only if every cost column of the list exists in the data.
            and all(column in self.data_raw.columns for column in columns_costs)
        ):
            for column_cost in columns_costs:
                self.data_calculated[column_cost + "_quota"] = (
                    self.data_raw[column_cost] / self.data_raw["revenue"]
                )
        else:
            raise ValueError(
                f"The date-column, the revenue-column or the columns '{columns_costs}' are missing in your pd.DataFrame"
            )

    def get_llm_quota(self, context: list):
        """Let an LLM set the cost quotas of the next six years for every quota column.
        Adds one prediction column per quota column to self.data_predictions."""

        # Every column written by get_expenses_quota() ends with '_quota'.
        columns_quota = [
            column for column in self.data_calculated.columns if column.endswith("_quota")
        ]
        if not columns_quota:
            raise ValueError(
                "self.data_calculated holds no quota column. "
                "You must calculate the quotas with get_expenses_quota() first"
            )

        # The LLM reads plain text, so the quota table becomes a markdown table.
        table = self.data_calculated[["date"] + columns_quota].to_markdown(index=False)
        prompt_file = Path(__file__).resolve().parent.parent / "prompts" / "llm_quota.md"
        answer = LLMCall("claude-haiku-4-5-20251001").llm_call(
            [table] + context,
            SYSTEM_PROMPT_QUOTA,
            prompt_file.read_text(encoding="utf-8"),
            response_model=LLMQuota,
            tool_name="llm_quota",
        )

        # With a forced tool the answer holds a ToolUseBlock, whose .input is already a dict.
        blocks_tool = [block for block in answer if block.type == "tool_use"]
        if not blocks_tool:
            raise ValueError(
                f"The LLM answered without using the tool 'llm_quota', so it returned no "
                f"quotas. Blocks received: {[block.type for block in answer]}"
            )
        self.llm_quota_response = LLMQuota(**blocks_tool[0].input)

        for column in columns_quota:
            if column not in self.llm_quota_response.quotas:
                raise ValueError(f"The LLM returned no quotas for the column '{column}'")
            quotas = self.llm_quota_response.quotas[column].quotas
            # One quota per forecast year, otherwise the column does not fit the DataFrame.
            if len(quotas) != len(self.data_predictions):
                raise ValueError(
                    f"The LLM returned {len(quotas)} quotas for the column '{column}', "
                    f"but {len(self.data_predictions)} forecast years are needed"
                )
            self.data_predictions[column + "_llm"] = quotas
