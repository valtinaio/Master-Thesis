"""
This file tests all classes and methods needed
for FSAP using fmp_api.py and sec_api.py based on AAPL.
"""
from stock_agent.services.fmp_api import FMP
from stock_agent.services.calculus import Calculus

SAMPLE_STOCK = "AAPL"

# ----------------------
# Revenue last 5 years
# ----------------------
# 1 Revenue Time Series from raw data
aapl_income_statement = FMP(SAMPLE_STOCK)
aaple_revenue = aapl_income_statement.get_income_statement("FY", 5)[["date", "revenue"]]
print(aaple_revenue)

# 2 Revenue Growth Rate
aaple_calculus = Calculus(aaple_revenue)
aaple_revenue_gr = aaple_calculus.get_growth_rate("revenue")
print(aaple_revenue_gr)

# 3 CAGR over complete time period
aaple_cagr = aaple_calculus.get_CAGR("revenue")
print(aaple_cagr)
