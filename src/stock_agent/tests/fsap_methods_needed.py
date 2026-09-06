"""
This file tests all classes and methods needed
for FSAP using fmp_api.py and sec_api.py based on AAPL.
"""
from stock_agent.services.fmp_api import FMP
from stock_agent.services.sec_api import SEC
from stock_agent.services.calculus import Calculus
from stock_agent.services.llm_call import LLMCall
import pandas as pd

SAMPLE_STOCK = "AAPL"
SYSTEM_PROMPT = "You are a professional stock analyst, searching for profitable investment possibilities."

# ----------------------
# Revenue last 5 years
# ----------------------
# 1 Revenue Time Series from raw data
aapl_income_statement = FMP(SAMPLE_STOCK).get_income_statement("FY", 6)
aaple_revenue = aapl_income_statement[["date", "revenue"]]
print(aaple_revenue)

# 2 Revenue Growth Rate
aaple_calculus = Calculus(aapl_income_statement)
aaple_calculus.get_growth_rate("revenue")
aaple_calculus.data_calculated

# 3 CAGR over complete time period
aaple_calculus.get_CAGR("revenue")
aaple_calculus.cagr

# 4 CAGR prediction for + 5 years plus year + 6 with long term growth rate
aaple_calculus.get_CAGR_prediction_plus_one("revenue")
aaple_calculus.data_predictions

# ------------------------------
# Extracting expenses and Quota
# ------------------------------
aaple_calculus.get_expenses_quota(["costOfRevenue",
                                   "operatingExpenses"])
aaple_calculus.data_calculated

# ----------------------------------
# Extracting SEC data for LLM-quota
# ----------------------------------
aapl_sec = SEC(SAMPLE_STOCK)
aapl_sec.cik
aapl_industry = aapl_sec.get_submissions()["sicDescription"] # returns the branche of the company
aapl_items = aapl_sec.get_archives("10-K")
aapl_items.keys()

# ----------------------
# LLM sets the quotas
# ----------------------
aaple_calculus.get_llm_quota([f"Industry: {aapl_industry}",
                              "Management Discussion and Analysis: " + aapl_items["item_7"],
                              f"Revenue CAGR: {aaple_calculus.cagr["revenue_CAGR"]}"])
# The six LLM predicted quotas per cost column
aaple_calculus.data_predictions
# Reasoning and confidence per cost column
aaple_calculus.llm_quota_response.quotas["operatingExpenses_quota"].reasoning
aaple_calculus.llm_quota_response.quotas["operatingExpenses_quota"].confidence

# ----------------------
# Expenses Prediction
# ----------------------
aaple_calculus.get_expenses_prediction()
aaple_calculus.data_predictions

# -------------------------------------
# Expenses Prediction vs. Reality Test
# -------------------------------------
# 1 Long history from FY2010 to FY2025 in one call
aapl_history = FMP(SAMPLE_STOCK).get_income_statement("FY", 16)

# 2 Split: the training years end in 2018, the six following years are the reality check.
aapl_training = aapl_history[aapl_history["date"].dt.year <= 2018].reset_index(drop=True)
aapl_reality = aapl_history[
    (aapl_history["date"].dt.year >= 2019) & (aapl_history["date"].dt.year <= 2024)
].reset_index(drop=True)

# 3 The same pipeline as above, but only on the training years
aaple_calculus_test = Calculus(aapl_training)
aaple_calculus_test.get_growth_rate("revenue")
aaple_calculus_test.get_CAGR("revenue")
aaple_calculus_test.get_CAGR_prediction_plus_one("revenue")
aaple_calculus_test.get_expenses_quota(["costOfRevenue",
                                        "operatingExpenses"])
aaple_calculus_test.llm_quota_response.quotas["operatingExpenses_quota"].reasoning

# 4 The newest 10-K available in 2018, so the LLM knows nothing about the years it predicts.
aapl_items_2018 = aapl_sec.get_archives("10-K", 7)
aaple_calculus_test.get_llm_quota([f"Industry: {aapl_industry}",
                                   "Management Discussion and Analysis: " + aapl_items_2018["item_7"],
                                   f"Revenue CAGR: {aaple_calculus_test.cagr["revenue_CAGR"]}"])
aaple_calculus_test.get_expenses_prediction()

# 5 Prediction against reality, with the relative deviation per year and column.
# .values drops the pandas index of both sides, so the rows are matched by their order.
comparison = pd.DataFrame({"date": aaple_calculus_test.data_predictions["date"]})
for column in ["costOfRevenue", "operatingExpenses"]:
    prediction = aaple_calculus_test.data_predictions[column + "_prediction"].values
    real = aapl_reality[column].values
    comparison[column + "_prediction"] = prediction
    comparison[column + "_real"] = real
    comparison[column + "_deviation"] = abs((prediction - real) / real)
print(comparison)
