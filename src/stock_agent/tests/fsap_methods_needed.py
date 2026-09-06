"""
This file tests all classes and methods needed
for FSAP using fmp_api.py and sec_api.py based on AAPL.
"""
from stock_agent.services.fmp_api import FMP
from stock_agent.services.sec_api import SEC
from stock_agent.services.calculus import Calculus
from stock_agent.services.llm_call import LLMCall

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
# LLM Calls
# ----------------------
bot = LLMCall("claude-haiku-4-5-20251001")
bot_answer = bot.llm_call(["I am Valentin"], SYSTEM_PROMPT, "Wie gehts?")
# Final answer
bot_answer[1].text

