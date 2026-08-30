from datetime import date, timedelta

from pydantic import BaseModel, EmailStr, Field, field_validator


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

    @field_validator("ticker_symbol")   # Through this decorator the classmethod down below gets used when ticker_symbol gets set
    @classmethod
    def uppercase_ticker_symbol(cls, value: str) -> str:
        """Normalizes the ticker symbol to uppercase."""
        return value.upper()


class FSAPSchema(BaseModel):
    """Holds every parameter an FSAP analysis needs, grouped by its data source."""

    # Each key maps to one FSAP line item; the list holds one value per fiscal year.
    # The keys mirror the tables in "fsap_functions.md": what FMP delivers directly,
    # what only the SEC delivers, and what has to be calculated or assumed.
    fmp_data: dict[str, list[float]] = Field(
        default_factory=lambda: {
            "cash_and_cash_equivalents": [],
            "short_term_investments": [],
            "accounts_and_notes_receivable_net": [],
            "inventories": [],
            "current_assets_total": [],
            "long_term_investments": [],
            "other_assets": [],
            "other_intangible_assets": [],
            "goodwill": [],
            "total_assets": [],
            "accounts_payable": [],
            "accrued_liabilities": [],
            "notes_payable_and_short_term_debt": [],
            "current_liabilities_total": [],
            "long_term_debt": [],
            "long_term_accrued_liabilities": [],
            "deferred_tax_liabilities_noncurrent": [],
            "total_liabilities": [],
            "preferred_stock": [],
            "retained_earnings": [],
            "accum_other_comprehensive_income": [],
            "treasury_stock": [],
            "total_common_shareholders_equity": [],
            "noncontrolling_interests": [],
            "total_equity": [],
            "revenues": [],
            "cost_of_sales_and_occupancy_expense": [],
            "gross_profit": [],
            "depreciation_and_amortization_income_statement": [],
            "general_and_administrative_expenses": [],
            "operating_profit": [],
            "interest_income": [],
            "interest_expense": [],
            "other_income_or_gains_expenses_or_losses": [],
            "income_before_tax": [],
            "income_tax_expense": [],
            "income_from_discontinued_operations": [],
            "net_income": [],
            "net_income_attributable_to_noncontrolling_interests": [],
            "net_income_attributable_to_common_shareholders": [],
            "net_income_check": [],
            "net_income_cash_flow": [],
            "add_back_depreciation_and_amortization": [],
            "add_back_stock_based_compensation": [],
            "deferred_income_taxes": [],
            "change_in_accounts_receivable": [],
            "change_in_inventories": [],
            "change_in_accounts_payable": [],
            "other_addbacks_to_net_income": [],
            "other_operating_cash_flows": [],
            "net_cf_from_operating_activities": [],
            "property_plant_and_equipment_acquired": [],
            "investments_sold": [],
            "investments_acquired": [],
            "payments_for_acquisitions_of_intangible_assets": [],
            "other_investment_transactions": [],
            "net_cf_from_investing_activities": [],
            "change_in_short_term_borrowing": [],
            "change_in_long_term_borrowing": [],
            "issue_of_capital_stock": [],
            "share_repurchases": [],
            "dividend_payments": [],
            "other_financing_transactions": [],
            "net_cf_from_financing_activities": [],
            "effects_of_exchange_rate_changes_on_cash": [],
            "net_change_in_cash": [],
            "cash_and_cash_equivalents_beginning_of_year": [],
            "cash_and_cash_equivalents_end_of_year": [],
            "average_tax_rate": [],
            "preferred_stock_dividends": [],
            "common_shares_outstanding": [],
            "earnings_per_share_basic": [],
            "common_dividends_per_share": [],
            "share_price_at_fiscal_year_end": [],
            "current_share_price": [],
            "number_of_shares_outstanding_current": [],
            "current_market_value": [],
            "equity_risk_factor_market_beta": [],
            "risk_free_rate": [],
            "debt_capital": [],
            "effective_tax_rate_valuation": [],
        }
    )
    sec_data: dict[str, list[float]] = Field(
        default_factory=lambda: {
            "deferred_income_taxes_current": [],
            "equity_and_cost_investments": [],
            "property_plant_and_equipment_at_cost": [],
            "accumulated_depreciation": [],
            "deferred_income_taxes_noncurrent": [],
            "current_maturities_of_long_term_debt": [],
            "deferred_tax_liabilities_current": [],
            "income_from_equity_investees": [],
            "income_from_equity_affiliates_net_of_dividends": [],
            "change_in_income_taxes_payable": [],
            "change_in_deferred_revenues": [],
            "proceeds_from_sales_of_property_plant_and_equipment": [],
            "proceeds_from_stock_option_exercises": [],
            "other_comprehensive_income_items": [],
            "comprehensive_income": [],
            "statutory_tax_rate": [],
        }
    )
    other_data: dict[str, list[float]] = Field(
        default_factory=lambda: {
            "prepaid_expenses_and_other_current_assets": [],
            "common_stock_plus_additional_paid_in_capital": [],
            "change_in_marketable_securities": [],
            "cost_of_debt_capital_before_tax": [],
            "store_operating_expenses": [],
            "other_operating_expenses": [],
            "other_operating_expenses_1": [],
            "other_operating_expenses_2": [],
            "non_recurring_operating_gains_losses": [],
            "income_loss_from_equity_affiliates_income_statement": [],
            "extraordinary_gains_losses": [],
            "changes_in_accounting_principles": [],
            "insurance_reserves": [],
            "stored_value_card_liability": [],
            "accrued_litigation_charge": [],
            "other_current_assets_1": [],
            "other_current_assets_2": [],
            "other_noncurrent_liabilities_1": [],
            "other_noncurrent_liabilities_2": [],
            "change_in_prepaid_expenses": [],
            "change_in_other_current_assets": [],
            "change_in_other_noncurrent_assets": [],
            "change_in_other_current_liabilities": [],
            "after_tax_effects_of_nonrecurring_and_unusual_items": [],
            "depreciation_expense": [],
            "market_risk_premium": [],
            "long_run_growth_assumption": [],
            "preferred_stock_capital": [],
            "preferred_dividends": [],
            "preferred_implied_yield": [],
            "noncontrolling_interests_capital": [],
            "noncontrolling_interests_earnings": [],
            "noncontrolling_interests_implied_yield": [],
            "number_of_stores_per_segment": [],
            "revenue_per_store_per_segment": [],
            "new_stores_per_segment": [],
            "fifty_third_week_in_fiscal_year": [],
        }
    )
    # frozen keeps the number of history years fixed once the model is created.
    n_years_history: int = Field(default=5, frozen=True)
