"""
This file tests all classes and methods needed
for FSAP using fmp_api.py and sec_api.py based on AAPL.
"""
from stock_agent.services.fmp_api import FMP
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
aaple_calculus = Calculus(aaple_revenue)
aaple_revenue_gr = aaple_calculus.get_growth_rate("revenue")
print(aaple_revenue_gr)

# 3 CAGR over complete time period
aaple_cagr = aaple_calculus.get_CAGR("revenue")
print(aaple_cagr)

# 4 CAGR prediction for + 5 years plus year + 6 with long term growth rate
aaple_cagr_pred = aaple_calculus.get_CAGR_prediction_plus_one("revenue", aaple_cagr.iloc[0, 1])
print(aaple_cagr_pred)

# ---------------------------
# Extracting costs and Quota
# ---------------------------
aaple_costs = aapl_income_statement[["date",
                                    "revenue",
                                    "costOfRevenue",
                                    "sellingGeneralAndAdministrativeExpenses",
                                    "operatingExpenses",
                                    "depreciationAndAmortization"]]
print(aaple_costs)
# Example: operatingExpenses Quota
aaple_calculus_1 = Calculus(aaple_costs)
aaple_calculus_1.get_cost_quota(["costOfRevenue",
                                 "sellingGeneralAndAdministrativeExpenses",
                                 "operatingExpenses",
                                 "depreciationAndAmortization"])

# ----------------------
# LLM Calls
# ----------------------
bot = LLMCall("claude-haiku-4-5-20251001")
bot_answer = bot.llm_call(["I am Valentin"], SYSTEM_PROMPT, "Wie gehts?")
# Final answer
bot_answer[1].text