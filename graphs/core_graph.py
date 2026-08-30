"""
This is the core-graph which orchestrates the complete process. It defines when to call which sub-graph. It's a pure consumer of other sub-graphs.
"""

# ---------------------------
# Imports
# ---------------------------
import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd
from langgraph.graph import END, StateGraph

# The project root is the "codes" folder, the parent of the "graphs" folder.
# Adding it makes the sibling packages importable no matter where Python is started.
sys.path.append(str(Path(__file__).resolve().parent.parent))

from pydantic_models.pydantic_models import CoreGraphStateSchema, empty_frame
from services.fmp_api import FMP
from services.sec_api import SEC, SECError

# ---------------------------
# Mapping constants
# ---------------------------
# Every SEC parameter with its XBRL tag and the unit that tag is reported in.
# Ratios use the unit "pure", all money amounts use "USD".
SEC_TAGS: dict[str, tuple[str, str]] = {
    "deferred_income_taxes_current": ("DeferredTaxAssetsNetCurrent", "USD"),
    "equity_and_cost_investments": ("EquityMethodInvestments", "USD"),
    "property_plant_and_equipment_at_cost": ("PropertyPlantAndEquipmentGross", "USD"),
    "accumulated_depreciation": (
        "AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment", "USD"),
    "deferred_income_taxes_noncurrent": ("DeferredIncomeTaxAssetsNet", "USD"),
    "current_maturities_of_long_term_debt": ("LongTermDebtCurrent", "USD"),
    "deferred_tax_liabilities_current": ("DeferredTaxLiabilitiesCurrent", "USD"),
    "income_from_equity_investees": ("IncomeLossFromEquityMethodInvestments", "USD"),
    "income_from_equity_affiliates_net_of_dividends": (
        "IncomeLossFromEquityMethodInvestmentsNetOfDividends", "USD"),
    "change_in_income_taxes_payable": ("IncreaseDecreaseInAccruedIncomeTaxesPayable", "USD"),
    "change_in_deferred_revenues": ("IncreaseDecreaseInDeferredRevenue", "USD"),
    "proceeds_from_sales_of_property_plant_and_equipment": (
        "ProceedsFromSaleOfPropertyPlantAndEquipment", "USD"),
    "proceeds_from_stock_option_exercises": ("ProceedsFromStockOptionsExercised", "USD"),
    "other_comprehensive_income_items": ("OtherComprehensiveIncomeLossNetOfTax", "USD"),
    "comprehensive_income": ("ComprehensiveIncomeNetOfTax", "USD"),
    "statutory_tax_rate": (
        "EffectiveIncomeTaxRateReconciliationAtFederalStatutoryIncomeTaxRate", "pure"),
}

# FSAP writes these line items in angle brackets, which means it expects them as negative
# numbers. FMP is inconsistent here, so these values are always stored as -abs(value).
NEGATIVE_KEYS: set[str] = {
    "cost_of_sales_and_occupancy_expense",
    "depreciation_and_amortization_income_statement",
    "general_and_administrative_expenses",
    "interest_expense",
    "income_tax_expense",
    "treasury_stock",
    "property_plant_and_equipment_acquired",
    "investments_acquired",
    "share_repurchases",
    "dividend_payments",
    "store_operating_expenses",
    "other_operating_expenses",
    "accumulated_depreciation",
    "income_from_equity_affiliates_net_of_dividends",
    "effective_tax_rate_valuation",
}

# FSAP keeps these rows for manual entries or for company-specific items that are already
# part of another line. They carry no data point and are therefore always zero.
ZERO_KEYS: set[str] = {
    "other_operating_expenses_1",
    "other_operating_expenses_2",
    "income_loss_from_equity_affiliates_income_statement",
    "extraordinary_gains_losses",
    "changes_in_accounting_principles",
    "insurance_reserves",
    "stored_value_card_liability",
    "accrued_litigation_charge",
    "other_current_assets_1",
    "other_current_assets_2",
    "other_noncurrent_liabilities_1",
    "other_noncurrent_liabilities_2",
    "change_in_prepaid_expenses",
    "change_in_other_current_assets",
    "change_in_other_noncurrent_assets",
    "change_in_other_current_liabilities",
}

# These parameters only exist in the narrative part of the 10-K, so no API delivers them.
# They stay empty until the LLM service described in STATUS_QUO.md is built.
LLM_KEYS: set[str] = {
    "non_recurring_operating_gains_losses",
    "number_of_stores_per_segment",
    "revenue_per_store_per_segment",
    "new_stores_per_segment",
}


# ---------------------------
# Helpers
# ---------------------------
def _to_date(text: str) -> date:
    """Turns an API date string like '2024-09-29' into a real date object."""

    return datetime.strptime(text[:10], "%Y-%m-%d").date()


def _apply_sign(value: float | None, key: str) -> float | None:
    """Forces the FSAP sign: keys FSAP writes in angle brackets are always negative."""

    if value is None:
        return None
    return -abs(value) if key in NEGATIVE_KEYS else value


def _frame(dates: list[date], values: list[float | None]) -> pd.DataFrame:
    """Builds the two-column table of one FSAP parameter, oldest year first."""

    frame = pd.DataFrame({"date": dates, "value": values})
    return frame.sort_values("date", ignore_index=True)


def _fmp_series(records: list[dict], field: str, key: str) -> pd.DataFrame:
    """Reads one field out of an FMP response and returns it as a dated table."""

    # A field the response does not contain becomes None instead of raising an error.
    dates = [_to_date(record["date"]) for record in records]
    values = [_apply_sign(record.get(field), key) for record in records]
    return _frame(dates, values)


def _sec_series(sec: SEC, tag: str, unit: str, key: str) -> pd.DataFrame | None:
    """Reads one XBRL tag from the SEC and returns it as a dated table, or None if it fails."""

    try:
        facts = sec.get_concept(tag, unit=unit)
    except SECError:
        # Not every company reports every tag, so a missing tag is a normal case here.
        return None
    dates = [_to_date(fact["end"]) for fact in facts]
    values = [_apply_sign(fact["value"], key) for fact in facts]
    return _frame(dates, values)


def _point_value(value: float | None, end_date: date, key: str) -> pd.DataFrame:
    """Wraps a single current value, such as today's share price, into a one-row table."""

    return _frame([end_date], [_apply_sign(value, key)])


def _computed_series(records: list[dict], fields: list[str], key: str) -> pd.DataFrame:
    """Adds several fields of one FMP response per year, for values FMP reports split up."""

    dates = [_to_date(record["date"]) for record in records]
    values = []
    for record in records:
        parts = [record.get(field) for field in fields]
        known = [part for part in parts if part is not None]
        # A year in which every field is missing stays None instead of becoming a wrong zero.
        values.append(_apply_sign(sum(known), key) if known else None)
    return _frame(dates, values)


def _first_value(records: list[dict], field: str) -> float | None:
    """Returns one field of the newest entry of an FMP response."""

    return records[0].get(field) if records else None


# ---------------------------
# The node
# ---------------------------
def initialize_core_state(state: CoreGraphStateSchema) -> None:
    """Fills every FSAP parameter of the core-graph state with data from FMP and the SEC."""

    config = state.import_config
    fsap = state.fsap_data
    years = fsap.n_years_history
    end_date = config.end_date

    fmp = FMP(config.ticker_symbol)
    sec = SEC(config.ticker_symbol, config.user_agent_mail)

    # Each statement is fetched once and then read many times, which keeps the API calls low.
    balance = fmp.get_balance_sheet(limit=years)
    income = fmp.get_income_statement(limit=years)
    cash_flow = fmp.get_cash_flow(limit=years)
    ratios = fmp.get_financial_ratios(limit=years)
    enterprise = fmp.get_enterprise_values(limit=years)

    # ---------------------------
    # Table 1: values FMP delivers directly
    # ---------------------------
    # One entry means: FSAP key -> (FMP response, field name in that response).
    fmp_fields: dict[str, tuple[list[dict], str]] = {
        "cash_and_cash_equivalents": (balance, "cashAndCashEquivalents"),
        "short_term_investments": (balance, "shortTermInvestments"),
        "accounts_and_notes_receivable_net": (balance, "netReceivables"),
        "inventories": (balance, "inventory"),
        "current_assets_total": (balance, "totalCurrentAssets"),
        "long_term_investments": (balance, "longTermInvestments"),
        "other_assets": (balance, "otherNonCurrentAssets"),
        "other_intangible_assets": (balance, "intangibleAssets"),
        "goodwill": (balance, "goodwill"),
        "total_assets": (balance, "totalAssets"),
        "accounts_payable": (balance, "accountPayables"),
        "accrued_liabilities": (balance, "accruedExpenses"),
        "notes_payable_and_short_term_debt": (balance, "shortTermDebt"),
        "current_liabilities_total": (balance, "totalCurrentLiabilities"),
        "long_term_debt": (balance, "longTermDebt"),
        "long_term_accrued_liabilities": (balance, "otherNonCurrentLiabilities"),
        "deferred_tax_liabilities_noncurrent": (balance, "deferredTaxLiabilitiesNonCurrent"),
        "total_liabilities": (balance, "totalLiabilities"),
        "preferred_stock": (balance, "preferredStock"),
        "retained_earnings": (balance, "retainedEarnings"),
        "accum_other_comprehensive_income": (balance, "accumulatedOtherComprehensiveIncomeLoss"),
        "treasury_stock": (balance, "treasuryStock"),
        "total_common_shareholders_equity": (balance, "totalStockholdersEquity"),
        "noncontrolling_interests": (balance, "minorityInterest"),
        "total_equity": (balance, "totalEquity"),
        "revenues": (income, "revenue"),
        "cost_of_sales_and_occupancy_expense": (income, "costOfRevenue"),
        "gross_profit": (income, "grossProfit"),
        "depreciation_and_amortization_income_statement": (income, "depreciationAndAmortization"),
        "general_and_administrative_expenses": (income, "generalAndAdministrativeExpenses"),
        "operating_profit": (income, "operatingIncome"),
        "interest_income": (income, "interestIncome"),
        "interest_expense": (income, "interestExpense"),
        "other_income_or_gains_expenses_or_losses": (income, "nonOperatingIncomeExcludingInterest"),
        "income_before_tax": (income, "incomeBeforeTax"),
        "income_tax_expense": (income, "incomeTaxExpense"),
        "income_from_discontinued_operations": (income, "netIncomeFromDiscontinuedOperations"),
        "net_income": (income, "netIncome"),
        "net_income_attributable_to_noncontrolling_interests": (income, "netIncomeDeductions"),
        "net_income_attributable_to_common_shareholders": (income, "bottomLineNetIncome"),
        "net_income_check": (income, "netIncome"),
        "net_income_cash_flow": (cash_flow, "netIncome"),
        "add_back_depreciation_and_amortization": (cash_flow, "depreciationAndAmortization"),
        "add_back_stock_based_compensation": (cash_flow, "stockBasedCompensation"),
        "deferred_income_taxes": (cash_flow, "deferredIncomeTax"),
        "change_in_accounts_receivable": (cash_flow, "accountsReceivables"),
        "change_in_inventories": (cash_flow, "inventory"),
        "change_in_accounts_payable": (cash_flow, "accountsPayables"),
        "other_addbacks_to_net_income": (cash_flow, "otherNonCashItems"),
        "other_operating_cash_flows": (cash_flow, "otherWorkingCapital"),
        "net_cf_from_operating_activities": (cash_flow, "netCashProvidedByOperatingActivities"),
        "property_plant_and_equipment_acquired": (
            cash_flow, "investmentsInPropertyPlantAndEquipment"),
        "investments_sold": (cash_flow, "salesMaturitiesOfInvestments"),
        "investments_acquired": (cash_flow, "purchasesOfInvestments"),
        "payments_for_acquisitions_of_intangible_assets": (cash_flow, "acquisitionsNet"),
        "other_investment_transactions": (cash_flow, "otherInvestingActivities"),
        "net_cf_from_investing_activities": (cash_flow, "netCashProvidedByInvestingActivities"),
        "change_in_short_term_borrowing": (cash_flow, "shortTermNetDebtIssuance"),
        "change_in_long_term_borrowing": (cash_flow, "longTermNetDebtIssuance"),
        "issue_of_capital_stock": (cash_flow, "commonStockIssuance"),
        "share_repurchases": (cash_flow, "commonStockRepurchased"),
        "dividend_payments": (cash_flow, "commonDividendsPaid"),
        "other_financing_transactions": (cash_flow, "otherFinancingActivities"),
        "net_cf_from_financing_activities": (cash_flow, "netCashProvidedByFinancingActivities"),
        "effects_of_exchange_rate_changes_on_cash": (cash_flow, "effectOfForexChangesOnCash"),
        "net_change_in_cash": (cash_flow, "netChangeInCash"),
        "cash_and_cash_equivalents_beginning_of_year": (cash_flow, "cashAtBeginningOfPeriod"),
        "cash_and_cash_equivalents_end_of_year": (cash_flow, "cashAtEndOfPeriod"),
        "average_tax_rate": (ratios, "effectiveTaxRate"),
        "preferred_stock_dividends": (cash_flow, "preferredDividendsPaid"),
        "common_shares_outstanding": (income, "weightedAverageShsOut"),
        "earnings_per_share_basic": (income, "eps"),
        "common_dividends_per_share": (ratios, "dividendPerShare"),
        "share_price_at_fiscal_year_end": (enterprise, "stockPrice"),
        "debt_capital": (enterprise, "addTotalDebt"),
    }
    for key, (records, field) in fmp_fields.items():
        fsap.fmp_data[key] = _fmp_series(records, field, key)

    # Values that describe today instead of a fiscal year, so each is a single row.
    treasury = fmp.get_treasury_rates(str(config.start_date), str(end_date))
    current_values: dict[str, float | None] = {
        "current_share_price": _first_value(fmp.get_quote(), "price"),
        "number_of_shares_outstanding_current": _first_value(
            fmp.get_shares_float(), "outstandingShares"),
        "current_market_value": _first_value(fmp.get_market_cap(), "marketCap"),
        "equity_risk_factor_market_beta": _first_value(fmp.get_profile(), "beta"),
        # The treasury rates come day by day and oldest first, so the last one is current.
        "risk_free_rate": treasury[-1].get("year10") if treasury else None,
        # FSAP uses the tax rate of the newest year here and expects it as a negative number.
        "effective_tax_rate_valuation": _first_value(ratios, "effectiveTaxRate"),
    }
    for key, value in current_values.items():
        fsap.fmp_data[key] = _point_value(value, end_date, key)

    # ---------------------------
    # Table 2: values only the SEC delivers
    # ---------------------------
    for key, (tag, unit) in SEC_TAGS.items():
        series = _sec_series(sec, tag, unit, key)
        fsap.sec_data[key] = series if series is not None else empty_frame()

    # ---------------------------
    # Table 3: values that must be calculated or assumed
    # ---------------------------
    # FMP splits these items over two fields, so FSAP's single line is their sum.
    fsap.other_data["prepaid_expenses_and_other_current_assets"] = _computed_series(
        balance, ["prepaids", "otherCurrentAssets"], "prepaid_expenses_and_other_current_assets")
    fsap.other_data["common_stock_plus_additional_paid_in_capital"] = _computed_series(
        balance, ["commonStock", "additionalPaidInCapital"],
        "common_stock_plus_additional_paid_in_capital")
    fsap.other_data["change_in_marketable_securities"] = _computed_series(
        cash_flow, ["salesMaturitiesOfInvestments", "purchasesOfInvestments"],
        "change_in_marketable_securities")

    # FMP reports only the total of all operating expenses, so the store expenses are the
    # rest after removing the two parts FSAP lists separately.
    store_dates, store_values = [], []
    for record in income:
        store_dates.append(_to_date(record["date"]))
        total = record.get("operatingExpenses")
        if total is None:
            store_values.append(None)
            continue
        known_parts = ((record.get("depreciationAndAmortization") or 0)
                       + (record.get("generalAndAdministrativeExpenses") or 0))
        store_values.append(_apply_sign(total - known_parts, "store_operating_expenses"))
    fsap.other_data["store_operating_expenses"] = _frame(store_dates, store_values)
    # The split between store and other operating expenses is not reported anywhere, so the
    # whole rest stays in the line above and this one is zero.
    fsap.other_data["other_operating_expenses"] = _frame(store_dates, [0.0] * len(store_dates))

    # The cost of debt is the interest paid divided by the debt it was paid on.
    debt_dates, debt_values = [], []
    for income_record, balance_record in zip(income, balance):
        debt_dates.append(_to_date(income_record["date"]))
        interest = income_record.get("interestExpense")
        debt = balance_record.get("totalDebt")
        debt_values.append(interest / debt if interest and debt else None)
    fsap.other_data["cost_of_debt_capital_before_tax"] = _frame(debt_dates, debt_values)

    # A one-off item is taxed at the statutory rate, so only the part after tax hits net income.
    # The one-off amounts come from the LLM service that is still missing, so this stays empty.
    fsap.other_data["after_tax_effects_of_nonrecurring_and_unusual_items"] = empty_frame()

    # FSAP needs the depreciation without the amortization. Not every company reports it
    # separately, so the combined figure is the fallback.
    depreciation = _sec_series(sec, "Depreciation", "USD", "depreciation_expense")
    if depreciation is None:
        depreciation = _sec_series(
            sec, "DepreciationDepletionAndAmortization", "USD", "depreciation_expense")
    fsap.other_data["depreciation_expense"] = (
        depreciation if depreciation is not None else empty_frame())

    # Both assumptions are set by the user in the import configuration.
    fsap.other_data["market_risk_premium"] = _point_value(
        config.market_risk_premium, end_date, "market_risk_premium")
    fsap.other_data["long_run_growth_assumption"] = _point_value(
        config.long_run_growth_assumption, end_date, "long_run_growth_assumption")

    # The valuation needs the newest figure of these balance sheet and income lines.
    preferred_capital = _first_value(balance, "preferredStock") or 0.0
    preferred_dividends = _first_value(cash_flow, "preferredDividendsPaid") or 0.0
    minority_capital = _first_value(balance, "minorityInterest") or 0.0
    minority_earnings = _first_value(income, "netIncomeDeductions") or 0.0
    valuation_values: dict[str, float] = {
        "preferred_stock_capital": preferred_capital,
        "preferred_dividends": preferred_dividends,
        # A yield needs capital to divide by, so without preferred stock it is zero.
        "preferred_implied_yield": (
            preferred_dividends / preferred_capital if preferred_capital else 0.0),
        "noncontrolling_interests_capital": minority_capital,
        "noncontrolling_interests_earnings": minority_earnings,
        "noncontrolling_interests_implied_yield": (
            minority_earnings / minority_capital if minority_capital else 0.0),
    }
    for key, value in valuation_values.items():
        fsap.other_data[key] = _point_value(value, end_date, key)

    # Some fiscal years have 53 instead of 52 weeks, which lifts the revenue of that year.
    # More than 364 days between two year ends shows such a year.
    fiscal_dates = sorted(_to_date(record["date"]) for record in income)
    week_values = [1.0]  # The oldest year has no earlier year to compare it with.
    for earlier, later in zip(fiscal_dates, fiscal_dates[1:]):
        week_values.append(53 / 52 if (later - earlier).days > 364 else 1.0)
    fsap.other_data["fifty_third_week_in_fiscal_year"] = _frame(fiscal_dates, week_values)

    # FSAP keeps these rows only so a user can fill them by hand; they hold no data.
    for key in ZERO_KEYS:
        fsap.other_data[key] = _frame(fiscal_dates, [0.0] * len(fiscal_dates))

    # These wait for the LLM service described in STATUS_QUO.md.
    for key in LLM_KEYS:
        fsap.other_data[key] = empty_frame()


# ---------------------------
# The graph
# ---------------------------
graph = StateGraph(CoreGraphStateSchema)
graph.add_node("initialize_core_state", initialize_core_state)
graph.set_entry_point("initialize_core_state")
graph.add_edge("initialize_core_state", END)
core_graph = graph.compile()
