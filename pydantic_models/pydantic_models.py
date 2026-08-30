from datetime import date, timedelta

import pandas as pd
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def empty_frame() -> pd.DataFrame:
    """Returns an empty table with the two columns every FSAP parameter uses."""
    return pd.DataFrame({"date": [], "value": []})


class DataImportSchema(BaseModel):
    """Input parameters for the data node in the core-graph."""

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
    # Both are analyst assumptions, not market data, so FSAP takes them as given values.
    market_risk_premium: float = 0.06
    long_run_growth_assumption: float = 0.03

    @field_validator("ticker_symbol")   # Through this decorator the classmethod down below gets used when ticker_symbol gets set
    @classmethod
    def uppercase_ticker_symbol(cls, value: str) -> str:
        """Normalizes the ticker symbol to uppercase."""
        return value.upper()


class FSAPSchema(BaseModel):
    """Holds every parameter an FSAP analysis needs, grouped by its data source."""

    # arbitrary_types_allowed is needed because pandas is not a type Pydantic knows.
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Each key maps to one FSAP line item; the table holds one row per fiscal year,
    # with the columns "date" (fiscal year end) and "value".
    # The keys mirror the tables in "fsap_functions.md": what FMP delivers directly,
    # what only the SEC delivers, and what has to be calculated or assumed.
    fmp_data: dict[str, pd.DataFrame] = Field(
        default_factory=lambda: {
            "cash_and_cash_equivalents": empty_frame(),
            "short_term_investments": empty_frame(),
            "accounts_and_notes_receivable_net": empty_frame(),
            "inventories": empty_frame(),
            "current_assets_total": empty_frame(),
            "long_term_investments": empty_frame(),
            "other_assets": empty_frame(),
            "other_intangible_assets": empty_frame(),
            "goodwill": empty_frame(),
            "total_assets": empty_frame(),
            "accounts_payable": empty_frame(),
            "accrued_liabilities": empty_frame(),
            "notes_payable_and_short_term_debt": empty_frame(),
            "current_liabilities_total": empty_frame(),
            "long_term_debt": empty_frame(),
            "long_term_accrued_liabilities": empty_frame(),
            "deferred_tax_liabilities_noncurrent": empty_frame(),
            "total_liabilities": empty_frame(),
            "preferred_stock": empty_frame(),
            "retained_earnings": empty_frame(),
            "accum_other_comprehensive_income": empty_frame(),
            "treasury_stock": empty_frame(),
            "total_common_shareholders_equity": empty_frame(),
            "noncontrolling_interests": empty_frame(),
            "total_equity": empty_frame(),
            "revenues": empty_frame(),
            "cost_of_sales_and_occupancy_expense": empty_frame(),
            "gross_profit": empty_frame(),
            "depreciation_and_amortization_income_statement": empty_frame(),
            "general_and_administrative_expenses": empty_frame(),
            "operating_profit": empty_frame(),
            "interest_income": empty_frame(),
            "interest_expense": empty_frame(),
            "other_income_or_gains_expenses_or_losses": empty_frame(),
            "income_before_tax": empty_frame(),
            "income_tax_expense": empty_frame(),
            "income_from_discontinued_operations": empty_frame(),
            "net_income": empty_frame(),
            "net_income_attributable_to_noncontrolling_interests": empty_frame(),
            "net_income_attributable_to_common_shareholders": empty_frame(),
            "net_income_check": empty_frame(),
            "net_income_cash_flow": empty_frame(),
            "add_back_depreciation_and_amortization": empty_frame(),
            "add_back_stock_based_compensation": empty_frame(),
            "deferred_income_taxes": empty_frame(),
            "change_in_accounts_receivable": empty_frame(),
            "change_in_inventories": empty_frame(),
            "change_in_accounts_payable": empty_frame(),
            "other_addbacks_to_net_income": empty_frame(),
            "other_operating_cash_flows": empty_frame(),
            "net_cf_from_operating_activities": empty_frame(),
            "property_plant_and_equipment_acquired": empty_frame(),
            "investments_sold": empty_frame(),
            "investments_acquired": empty_frame(),
            "payments_for_acquisitions_of_intangible_assets": empty_frame(),
            "other_investment_transactions": empty_frame(),
            "net_cf_from_investing_activities": empty_frame(),
            "change_in_short_term_borrowing": empty_frame(),
            "change_in_long_term_borrowing": empty_frame(),
            "issue_of_capital_stock": empty_frame(),
            "share_repurchases": empty_frame(),
            "dividend_payments": empty_frame(),
            "other_financing_transactions": empty_frame(),
            "net_cf_from_financing_activities": empty_frame(),
            "effects_of_exchange_rate_changes_on_cash": empty_frame(),
            "net_change_in_cash": empty_frame(),
            "cash_and_cash_equivalents_beginning_of_year": empty_frame(),
            "cash_and_cash_equivalents_end_of_year": empty_frame(),
            "average_tax_rate": empty_frame(),
            "preferred_stock_dividends": empty_frame(),
            "common_shares_outstanding": empty_frame(),
            "earnings_per_share_basic": empty_frame(),
            "common_dividends_per_share": empty_frame(),
            "share_price_at_fiscal_year_end": empty_frame(),
            "current_share_price": empty_frame(),
            "number_of_shares_outstanding_current": empty_frame(),
            "current_market_value": empty_frame(),
            "equity_risk_factor_market_beta": empty_frame(),
            "risk_free_rate": empty_frame(),
            "debt_capital": empty_frame(),
            "effective_tax_rate_valuation": empty_frame(),
        }
    )
    sec_data: dict[str, pd.DataFrame] = Field(
        default_factory=lambda: {
            "deferred_income_taxes_current": empty_frame(),
            "equity_and_cost_investments": empty_frame(),
            "property_plant_and_equipment_at_cost": empty_frame(),
            "accumulated_depreciation": empty_frame(),
            "deferred_income_taxes_noncurrent": empty_frame(),
            "current_maturities_of_long_term_debt": empty_frame(),
            "deferred_tax_liabilities_current": empty_frame(),
            "income_from_equity_investees": empty_frame(),
            "income_from_equity_affiliates_net_of_dividends": empty_frame(),
            "change_in_income_taxes_payable": empty_frame(),
            "change_in_deferred_revenues": empty_frame(),
            "proceeds_from_sales_of_property_plant_and_equipment": empty_frame(),
            "proceeds_from_stock_option_exercises": empty_frame(),
            "other_comprehensive_income_items": empty_frame(),
            "comprehensive_income": empty_frame(),
            "statutory_tax_rate": empty_frame(),
        }
    )
    other_data: dict[str, pd.DataFrame] = Field(
        default_factory=lambda: {
            "prepaid_expenses_and_other_current_assets": empty_frame(),
            "common_stock_plus_additional_paid_in_capital": empty_frame(),
            "change_in_marketable_securities": empty_frame(),
            "cost_of_debt_capital_before_tax": empty_frame(),
            "store_operating_expenses": empty_frame(),
            "other_operating_expenses": empty_frame(),
            "other_operating_expenses_1": empty_frame(),
            "other_operating_expenses_2": empty_frame(),
            "non_recurring_operating_gains_losses": empty_frame(),
            "income_loss_from_equity_affiliates_income_statement": empty_frame(),
            "extraordinary_gains_losses": empty_frame(),
            "changes_in_accounting_principles": empty_frame(),
            "insurance_reserves": empty_frame(),
            "stored_value_card_liability": empty_frame(),
            "accrued_litigation_charge": empty_frame(),
            "other_current_assets_1": empty_frame(),
            "other_current_assets_2": empty_frame(),
            "other_noncurrent_liabilities_1": empty_frame(),
            "other_noncurrent_liabilities_2": empty_frame(),
            "change_in_prepaid_expenses": empty_frame(),
            "change_in_other_current_assets": empty_frame(),
            "change_in_other_noncurrent_assets": empty_frame(),
            "change_in_other_current_liabilities": empty_frame(),
            "after_tax_effects_of_nonrecurring_and_unusual_items": empty_frame(),
            "depreciation_expense": empty_frame(),
            "market_risk_premium": empty_frame(),
            "long_run_growth_assumption": empty_frame(),
            "preferred_stock_capital": empty_frame(),
            "preferred_dividends": empty_frame(),
            "preferred_implied_yield": empty_frame(),
            "noncontrolling_interests_capital": empty_frame(),
            "noncontrolling_interests_earnings": empty_frame(),
            "noncontrolling_interests_implied_yield": empty_frame(),
            "number_of_stores_per_segment": empty_frame(),
            "revenue_per_store_per_segment": empty_frame(),
            "new_stores_per_segment": empty_frame(),
            "fifty_third_week_in_fiscal_year": empty_frame(),
        }
    )
    # frozen keeps the number of history years fixed once the model is created.
    n_years_history: int = Field(default=5, frozen=True)


class CoreGraphStateSchema(BaseModel):
    """Holds the complete state of the core-graph."""

    import_config: DataImportSchema
    fsap_data: FSAPSchema
