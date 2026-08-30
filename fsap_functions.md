# FSAP-Parameter und ihre Datenquellen

Grundlage ist das Blatt `Data` der Datei `FSAP - Starbucks.xlsx` (Zeilen 16-150), das
einzige Eingabeblatt von FSAP, plus die Bewertungsannahmen aus dem Blatt `Valuation`
(F24-F52). Alle uebrigen Blaetter (`Analysis`, `Forecasts`, `Forecast Development`)
werden daraus berechnet und brauchen keine eigenen Importe.

Jeder Parameter kommt in genau einer der drei Tabellen vor. Die Spalte `Key` nennt den
Dictionary-Schluessel im Modell `FSAPSchema` in `pydantic_models/pydantic_models.py`.

Zuordnung der Tabellen zu den Feldern von `FSAPSchema`:
- Tabelle 1 entspricht dem Feld `fmp_data`
- Tabelle 2 entspricht dem Feld `sec_data`
- Tabelle 3 entspricht dem Feld `other_data`

Abkuerzungen der Quellen:
- `FMP.<methode>` = Methode der Klasse `FMP` in `services/fmp_api.py`
- `SEC.<methode>` = Methode der Klasse `SEC` in `services/sec_api.py`

---

## 1. Parameter, die wir direkt mit FMP abrufen koennen

Hier steht nur, was ein einzelnes Feld einer FMP-Antwort direkt liefert. Parameter, die
erst aus mehreren Feldern berechnet werden muessen, stehen in Tabelle 3.

| # | Parameter | Key | FSAP-Zeile | FMP-Funktion | Feld |
|---|---|---|---|---|---|
| 1 | Cash and cash equivalents | `cash_and_cash_equivalents` | Data!16 | `FMP.get_balance_sheet` | `cashAndCashEquivalents` |
| 2 | Short-term investments | `short_term_investments` | Data!17 | `FMP.get_balance_sheet` | `shortTermInvestments` |
| 3 | Accounts and notes receivable - net | `accounts_and_notes_receivable_net` | Data!18 | `FMP.get_balance_sheet` | `netReceivables` |
| 4 | Inventories | `inventories` | Data!19 | `FMP.get_balance_sheet` | `inventory` |
| 5 | Current Assets (Summe) | `current_assets_total` | Data!24 | `FMP.get_balance_sheet` | `totalCurrentAssets` |
| 6 | Long-term investments | `long_term_investments` | Data!25 | `FMP.get_balance_sheet` | `longTermInvestments` |
| 7 | Other assets | `other_assets` | Data!30 | `FMP.get_balance_sheet` | `otherNonCurrentAssets` |
| 8 | Other intangible assets | `other_intangible_assets` | Data!31 | `FMP.get_balance_sheet` | `intangibleAssets` |
| 9 | Goodwill | `goodwill` | Data!32 | `FMP.get_balance_sheet` | `goodwill` |
| 10 | Total Assets | `total_assets` | Data!33 | `FMP.get_balance_sheet` | `totalAssets` |
| 11 | Accounts payable | `accounts_payable` | Data!36 | `FMP.get_balance_sheet` | `accountPayables` |
| 12 | Accrued liabilities | `accrued_liabilities` | Data!37 | `FMP.get_balance_sheet` | `accruedExpenses` |
| 13 | Notes payable and short-term debt | `notes_payable_and_short_term_debt` | Data!38 | `FMP.get_balance_sheet` | `shortTermDebt` |
| 14 | Current Liabilities (Summe) | `current_liabilities_total` | Data!44 | `FMP.get_balance_sheet` | `totalCurrentLiabilities` |
| 15 | Long-term debt | `long_term_debt` | Data!45 | `FMP.get_balance_sheet` | `longTermDebt` |
| 16 | Long-term accrued liabilities | `long_term_accrued_liabilities` | Data!46 | `FMP.get_balance_sheet` | `otherNonCurrentLiabilities` |
| 17 | Deferred tax liabilities - noncurrent | `deferred_tax_liabilities_noncurrent` | Data!47 | `FMP.get_balance_sheet` | `deferredTaxLiabilitiesNonCurrent` |
| 18 | Total Liabilities | `total_liabilities` | Data!50 | `FMP.get_balance_sheet` | `totalLiabilities` |
| 19 | Preferred stock | `preferred_stock` | Data!52 | `FMP.get_balance_sheet` | `preferredStock` |
| 20 | Retained earnings | `retained_earnings` | Data!54 | `FMP.get_balance_sheet` | `retainedEarnings` |
| 21 | Accum. other comprehensive income | `accum_other_comprehensive_income` | Data!55 | `FMP.get_balance_sheet` | `accumulatedOtherComprehensiveIncomeLoss` |
| 22 | Treasury stock | `treasury_stock` | Data!56 | `FMP.get_balance_sheet` | `treasuryStock` |
| 23 | Total Common Shareholders Equity | `total_common_shareholders_equity` | Data!57 | `FMP.get_balance_sheet` | `totalStockholdersEquity` |
| 24 | Noncontrolling interests | `noncontrolling_interests` | Data!58 | `FMP.get_balance_sheet` | `minorityInterest` |
| 25 | Total Equity | `total_equity` | Data!59 | `FMP.get_balance_sheet` | `totalEquity` |
| 26 | Revenues | `revenues` | Data!65 | `FMP.get_income_statement` | `revenue` |
| 27 | Cost of sales and occupancy expense | `cost_of_sales_and_occupancy_expense` | Data!66 | `FMP.get_income_statement` | `costOfRevenue` |
| 28 | Gross Profit | `gross_profit` | Data!67 | `FMP.get_income_statement` | `grossProfit` |
| 29 | Depreciation and Amortization (GuV) | `depreciation_and_amortization_income_statement` | Data!70 | `FMP.get_income_statement` | `depreciationAndAmortization` |
| 30 | General and Administrative Expenses | `general_and_administrative_expenses` | Data!71 | `FMP.get_income_statement` | `generalAndAdministrativeExpenses` |
| 31 | Operating Profit | `operating_profit` | Data!76 | `FMP.get_income_statement` | `operatingIncome` |
| 32 | Interest income | `interest_income` | Data!77 | `FMP.get_income_statement` | `interestIncome` |
| 33 | Interest expense | `interest_expense` | Data!78 | `FMP.get_income_statement` | `interestExpense` |
| 34 | Other income or gains / expenses or losses | `other_income_or_gains_expenses_or_losses` | Data!80 | `FMP.get_income_statement` | `nonOperatingIncomeExcludingInterest` |
| 35 | Income before Tax | `income_before_tax` | Data!81 | `FMP.get_income_statement` | `incomeBeforeTax` |
| 36 | Income tax expense | `income_tax_expense` | Data!82 | `FMP.get_income_statement` | `incomeTaxExpense` |
| 37 | Income from discontinued operations | `income_from_discontinued_operations` | Data!83 | `FMP.get_income_statement` | `netIncomeFromDiscontinuedOperations` |
| 38 | Net Income | `net_income` | Data!86 | `FMP.get_income_statement` | `netIncome` |
| 39 | Net income attributable to noncontrolling interests | `net_income_attributable_to_noncontrolling_interests` | Data!87 | `FMP.get_income_statement` | `netIncomeDeductions` |
| 40 | Net Income attributable to common shareholders | `net_income_attributable_to_common_shareholders` | Data!88 | `FMP.get_income_statement` | `bottomLineNetIncome` |
| 41 | Net Income (Kontrollwert) | `net_income_check` | Data!89 | `FMP.get_income_statement` | `netIncome` |
| 42 | Net Income (Kapitalflussrechnung) | `net_income_cash_flow` | Data!97 | `FMP.get_cash_flow` | `netIncome` |
| 43 | Add back depreciation and amortization | `add_back_depreciation_and_amortization` | Data!98 | `FMP.get_cash_flow` | `depreciationAndAmortization` |
| 44 | Add back stock-based compensation | `add_back_stock_based_compensation` | Data!99 | `FMP.get_cash_flow` | `stockBasedCompensation` |
| 45 | Deferred income taxes | `deferred_income_taxes` | Data!100 | `FMP.get_cash_flow` | `deferredIncomeTax` |
| 46 | Veraenderung accounts receivable | `change_in_accounts_receivable` | Data!102 | `FMP.get_cash_flow` | `accountsReceivables` |
| 47 | Veraenderung inventories | `change_in_inventories` | Data!103 | `FMP.get_cash_flow` | `inventory` |
| 48 | Veraenderung accounts payable | `change_in_accounts_payable` | Data!107 | `FMP.get_cash_flow` | `accountsPayables` |
| 49 | Other addbacks to net income | `other_addbacks_to_net_income` | Data!111 | `FMP.get_cash_flow` | `otherNonCashItems` |
| 50 | Other operating cash flows | `other_operating_cash_flows` | Data!112 | `FMP.get_cash_flow` | `otherWorkingCapital` |
| 51 | Net CF from Operating Activities | `net_cf_from_operating_activities` | Data!113 | `FMP.get_cash_flow` | `netCashProvidedByOperatingActivities` |
| 52 | Property, plant, and equipment acquired | `property_plant_and_equipment_acquired` | Data!115 | `FMP.get_cash_flow` | `investmentsInPropertyPlantAndEquipment` |
| 53 | Investments sold | `investments_sold` | Data!117 | `FMP.get_cash_flow` | `salesMaturitiesOfInvestments` |
| 54 | Investments acquired | `investments_acquired` | Data!118 | `FMP.get_cash_flow` | `purchasesOfInvestments` |
| 55 | Payments for acquisitions of intangible assets | `payments_for_acquisitions_of_intangible_assets` | Data!119 | `FMP.get_cash_flow` | `acquisitionsNet` |
| 56 | Other investment transactions | `other_investment_transactions` | Data!120 | `FMP.get_cash_flow` | `otherInvestingActivities` |
| 57 | Net CF from Investing Activities | `net_cf_from_investing_activities` | Data!121 | `FMP.get_cash_flow` | `netCashProvidedByInvestingActivities` |
| 58 | Veraenderung short-term borrowing | `change_in_short_term_borrowing` | Data!122-123 | `FMP.get_cash_flow` | `shortTermNetDebtIssuance` |
| 59 | Veraenderung long-term borrowing | `change_in_long_term_borrowing` | Data!124-125 | `FMP.get_cash_flow` | `longTermNetDebtIssuance` |
| 60 | Issue of capital stock | `issue_of_capital_stock` | Data!126 | `FMP.get_cash_flow` | `commonStockIssuance` |
| 61 | Share repurchases | `share_repurchases` | Data!128 | `FMP.get_cash_flow` | `commonStockRepurchased` |
| 62 | Dividend payments | `dividend_payments` | Data!129 | `FMP.get_cash_flow` | `commonDividendsPaid` |
| 63 | Other financing transactions | `other_financing_transactions` | Data!130-131 | `FMP.get_cash_flow` | `otherFinancingActivities` |
| 64 | Net CF from Financing Activities | `net_cf_from_financing_activities` | Data!132 | `FMP.get_cash_flow` | `netCashProvidedByFinancingActivities` |
| 65 | Effects of exchange rate changes on cash | `effects_of_exchange_rate_changes_on_cash` | Data!133 | `FMP.get_cash_flow` | `effectOfForexChangesOnCash` |
| 66 | Net Change in Cash | `net_change_in_cash` | Data!134 | `FMP.get_cash_flow` | `netChangeInCash` |
| 67 | Cash and cash equivalents, beginning of year | `cash_and_cash_equivalents_beginning_of_year` | Data!135 | `FMP.get_cash_flow` | `cashAtBeginningOfPeriod` |
| 68 | Cash and cash equivalents, end of year | `cash_and_cash_equivalents_end_of_year` | Data!136 | `FMP.get_cash_flow` | `cashAtEndOfPeriod` |
| 69 | Average tax rate (effektiver Steuersatz) | `average_tax_rate` | Data!143 | `FMP.get_financial_ratios` | `effectiveTaxRate` |
| 70 | Preferred stock dividends | `preferred_stock_dividends` | Data!146 | `FMP.get_cash_flow` | `preferredDividendsPaid` |
| 71 | Common shares outstanding | `common_shares_outstanding` | Data!147 | `FMP.get_income_statement` | `weightedAverageShsOut` |
| 72 | Earnings per share (basic) | `earnings_per_share_basic` | Data!148 | `FMP.get_income_statement` | `eps` |
| 73 | Common dividends per share | `common_dividends_per_share` | Data!149 | `FMP.get_financial_ratios` | `dividendPerShare` |
| 74 | Share price at fiscal year end | `share_price_at_fiscal_year_end` | Data!150 | `FMP.get_enterprise_values` | `stockPrice` |
| 75 | Current share price | `current_share_price` | Valuation!F24 | `FMP.get_quote` | `price` |
| 76 | Number of shares outstanding (aktuell) | `number_of_shares_outstanding_current` | Valuation!F25 | `FMP.get_shares_float` | `outstandingShares` |
| 77 | Current market value | `current_market_value` | Valuation!F26 | `FMP.get_market_cap` | `marketCap` |
| 78 | Equity risk factor (market beta) | `equity_risk_factor_market_beta` | Valuation!F33 | `FMP.get_profile` | `beta` |
| 79 | Risk free rate | `risk_free_rate` | Valuation!F34 | `FMP.get_treasury_rates` | `year10` |
| 80 | Debt capital | `debt_capital` | Valuation!F39 | `FMP.get_enterprise_values` | `addTotalDebt` |
| 81 | Effective tax rate (Bewertung) | `effective_tax_rate_valuation` | Valuation!F41 | `FMP.get_financial_ratios` | `effectiveTaxRate` |

---

## 2. Parameter, die FMP nicht liefert, SEC aber schon

Die Eintraege 3, 4, 14, 15 und 16 wurden mit echten API-Aufrufen gegen `SEC.get_concept`
geprueft und funktionieren. Die uebrigen Tags sind die US-GAAP-Standardtags fuer den
jeweiligen Posten und muessen beim Import noch einzeln bestaetigt werden.

Wichtig: `unit` muss passend gesetzt werden, der Standardwert `"USD"` funktioniert
nicht fuer Quoten und Betraege je Aktie.

| # | Parameter | Key | FSAP-Zeile | SEC-Funktion | XBRL-Tag / unit |
|---|---|---|---|---|---|
| 1 | Deferred income taxes - current | `deferred_income_taxes_current` | Data!21 | `SEC.get_concept` | `DeferredTaxAssetsNetCurrent`, unit `USD` |
| 2 | Equity and cost investments | `equity_and_cost_investments` | Data!26 | `SEC.get_concept` | `EquityMethodInvestments`, unit `USD` |
| 3 | Property, plant, and equipment - at cost | `property_plant_and_equipment_at_cost` | Data!27 | `SEC.get_concept` | `PropertyPlantAndEquipmentGross`, unit `USD` |
| 4 | Accumulated depreciation | `accumulated_depreciation` | Data!28 | `SEC.get_concept` | `AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment`, unit `USD` |
| 5 | Deferred income taxes - noncurrent | `deferred_income_taxes_noncurrent` | Data!29 | `SEC.get_concept` | `DeferredIncomeTaxAssetsNet`, unit `USD` |
| 6 | Current maturities of long-term debt | `current_maturities_of_long_term_debt` | Data!39 | `SEC.get_concept` | `LongTermDebtCurrent`, unit `USD` |
| 7 | Deferred tax liabilities - current | `deferred_tax_liabilities_current` | Data!40 | `SEC.get_concept` | `DeferredTaxLiabilitiesCurrent`, unit `USD` |
| 8 | Income from Equity Investees | `income_from_equity_investees` | Data!74 | `SEC.get_concept` | `IncomeLossFromEquityMethodInvestments`, unit `USD` |
| 9 | Income from equity affiliates, net of dividends | `income_from_equity_affiliates_net_of_dividends` | Data!101 | `SEC.get_concept` | `IncomeLossFromEquityMethodInvestmentsNetOfDividends`, unit `USD` |
| 10 | Veraenderung income taxes payable | `change_in_income_taxes_payable` | Data!108 | `SEC.get_concept` | `IncreaseDecreaseInAccruedIncomeTaxesPayable`, unit `USD` |
| 11 | Veraenderung deferred revenues | `change_in_deferred_revenues` | Data!110 | `SEC.get_concept` | `IncreaseDecreaseInDeferredRevenue`, unit `USD` |
| 12 | Proceeds from sales of property, plant, and equipment | `proceeds_from_sales_of_property_plant_and_equipment` | Data!114 | `SEC.get_concept` | `ProceedsFromSaleOfPropertyPlantAndEquipment`, unit `USD` |
| 13 | Proceeds from stock option exercises | `proceeds_from_stock_option_exercises` | Data!127 | `SEC.get_concept` | `ProceedsFromStockOptionsExercised`, unit `USD` |
| 14 | Other comprehensive income items | `other_comprehensive_income_items` | Data!91 | `SEC.get_concept` | `OtherComprehensiveIncomeLossNetOfTax`, unit `USD` |
| 15 | Comprehensive Income | `comprehensive_income` | Data!92 | `SEC.get_concept` | `ComprehensiveIncomeNetOfTax`, unit `USD` |
| 16 | Statutory tax rate | `statutory_tax_rate` | Data!142 | `SEC.get_concept` | `EffectiveIncomeTaxRateReconciliationAtFederalStatutoryIncomeTaxRate`, unit `pure` |

---

## 3. Parameter, die keine der beiden APIs direkt liefert

Hier stehen zwei Gruppen: Werte, die aus mehreren API-Feldern berechnet werden muessen
(Nr. 1 bis 4), und Werte, die in keiner der beiden APIs vorkommen (ab Nr. 5).

| # | Parameter | Key | FSAP-Zeile | Warum nicht direkt abrufbar | Vorschlag |
|---|---|---|---|---|---|
| 1 | Prepaid expenses and other current assets | `prepaid_expenses_and_other_current_assets` | Data!20 | Muss berechnet werden, FMP fuehrt zwei getrennte Felder. | Aus `FMP.get_balance_sheet` die Felder `prepaids` und `otherCurrentAssets` addieren. |
| 2 | Common stock + Additional paid in capital | `common_stock_plus_additional_paid_in_capital` | Data!53 | Muss berechnet werden, FMP fuehrt zwei getrennte Felder. | Aus `FMP.get_balance_sheet` die Felder `commonStock` und `additionalPaidInCapital` addieren. |
| 3 | Veraenderung marketable securities | `change_in_marketable_securities` | Data!116 | Muss berechnet werden, FMP fuehrt Kaeufe und Verkaeufe getrennt. | Aus `FMP.get_cash_flow` die Felder `salesMaturitiesOfInvestments` und `purchasesOfInvestments` addieren. |
| 4 | Cost of debt capital, before tax | `cost_of_debt_capital_before_tax` | Valuation!F40 | Muss berechnet werden, ist kein eigenes API-Feld. | `interestExpense` aus `FMP.get_income_statement` geteilt durch den durchschnittlichen `totalDebt` aus `FMP.get_balance_sheet`. |
| 5 | Store Operating Expenses | `store_operating_expenses` | Data!68 | Unternehmensspezifische GuV-Zeile ohne einheitliches XBRL-Tag. FMP fasst sie in `operatingExpenses` zusammen. | Als Restgroesse rechnen: `operatingExpenses` minus die bekannten Posten (D&A, G&A). Alternative: ein LLM-Sub-Graph liest den Posten aus der 10-K-GuV, deren URL `SEC.get_filings` bereits liefert. Empfehlung: Restgroesse, weil kein zusaetzlicher LLM-Aufruf noetig ist und FSAP nur die Summe der Betriebskosten braucht. |
| 6 | Other Operating Expenses | `other_operating_expenses` | Data!69 | Gleiche Ursache wie Nr. 5; `otherExpenses` bei FMP ist eine unscharfe Sammelposition. | Zusammen mit Nr. 5 als eine Restgroesse behandeln und FSAP-Zeile 69 mit 0 belegen. So bleibt die Summe der Betriebsaufwendungen korrekt, ohne eine Aufteilung zu erfinden. |
| 7 | Other operating expenses (1) | `other_operating_expenses_1` | Data!72 | Leere Reservezeile in FSAP, kein Datenpunkt. | Fest auf 0 setzen. Existiert nur, damit Nutzer manuell weitere Zeilen ergaenzen koennen. |
| 8 | Other operating expenses (2) | `other_operating_expenses_2` | Data!73 | Leere Reservezeile in FSAP, kein Datenpunkt. | Fest auf 0 setzen. Existiert nur, damit Nutzer manuell weitere Zeilen ergaenzen koennen. |
| 9 | Non-recurring operating gains/losses | `non_recurring_operating_gains_losses` | Data!75 | Einmalige Posten werden nicht einheitlich getaggt und stehen meist nur im Fliesstext des 10-K. | LLM-Sub-Graph, der den 10-K-Text (URL aus `SEC.get_filings`) nach einmaligen Posten durchsucht und einen Betrag je Jahr zurueckgibt. Fallback bei Unsicherheit: 0. |
| 10 | Income/Loss from equity affiliates (GuV) | `income_loss_from_equity_affiliates_income_statement` | Data!79 | Bei den meisten Firmen leer, da der Betrag bereits in Zeile 74 steht. | Fest auf 0 setzen, um Doppelzaehlung mit Tabelle 2 Nr. 8 zu vermeiden. |
| 11 | Extraordinary gains/losses | `extraordinary_gains_losses` | Data!84 | Nach ASU 2015-01 in US-GAAP abgeschafft, wird nicht mehr berichtet. | Fest auf 0 setzen. |
| 12 | Changes in accounting principles | `changes_in_accounting_principles` | Data!85 | Wird nur im Anhang beschrieben, nicht als Zahl getaggt. | Fest auf 0 setzen; bei Bedarf spaeter durch den LLM-Sub-Graph aus Nr. 9 mitabdecken. |
| 13 | Insurance Reserves | `insurance_reserves` | Data!41 | Unternehmensspezifische Bilanzzeile (Starbucks), kein allgemeines Tag. | Nicht separat abbilden. Der Betrag steckt bereits in `otherCurrentLiabilities` und damit in `totalCurrentLiabilities`. Auf 0 setzen. |
| 14 | Stored value card liability | `stored_value_card_liability` | Data!42 | Ebenfalls Starbucks-spezifisch (Guthabenkarten). | Wie Nr. 13 behandeln: in `otherCurrentLiabilities` belassen, auf 0 setzen. |
| 15 | Accrued litigation charge | `accrued_litigation_charge` | Data!43 | Einmaliger Rechtsstreit-Posten, nur bei Starbucks 2013 vorhanden. | Fest auf 0 setzen. |
| 16 | Other current assets (1) | `other_current_assets_1` | Data!22 | Leere Reservezeile. | Fest auf 0 setzen. |
| 17 | Other current assets (2) | `other_current_assets_2` | Data!23 | Leere Reservezeile. | Fest auf 0 setzen. |
| 18 | Other noncurrent liabilities (1) | `other_noncurrent_liabilities_1` | Data!48 | Leere Reservezeile. | Fest auf 0 setzen. |
| 19 | Other noncurrent liabilities (2) | `other_noncurrent_liabilities_2` | Data!49 | Leere Reservezeile. | Fest auf 0 setzen. |
| 20 | Veraenderung prepaid expenses | `change_in_prepaid_expenses` | Data!104 | FMP buendelt diesen Posten in `otherWorkingCapital`, eine Aufteilung ist nicht verfuegbar. | Nicht aufteilen. Der Sammelbetrag steht bereits in Tabelle 1 Nr. 50; hier 0 setzen, damit der Cash-Flow-Check aufgeht. |
| 21 | Veraenderung other current assets | `change_in_other_current_assets` | Data!105 | Gleiche Ursache wie Nr. 20. | Wie Nr. 20: auf 0 setzen, Betrag verbleibt in `otherWorkingCapital`. |
| 22 | Veraenderung other noncurrent assets | `change_in_other_noncurrent_assets` | Data!106 | Gleiche Ursache wie Nr. 20. | Wie Nr. 20: auf 0 setzen, Betrag verbleibt in `otherWorkingCapital`. |
| 23 | Veraenderung other current liabilities | `change_in_other_current_liabilities` | Data!109 | Gleiche Ursache wie Nr. 20. | Wie Nr. 20: auf 0 setzen, Betrag verbleibt in `otherWorkingCapital`. |
| 24 | After-tax effects of nonrecurring and unusual items | `after_tax_effects_of_nonrecurring_and_unusual_items` | Data!144 | Ergibt sich aus Nr. 9 und einer Steuerannahme, ist nirgends berichtet. | Aus Nr. 9 berechnen: einmaliger Posten mal (1 minus Statutory tax rate aus Tabelle 2 Nr. 16). Wenn Nr. 9 gleich 0 ist, ebenfalls 0. |
| 25 | Depreciation expense | `depreciation_expense` | Data!145 | Das Tag `Depreciation` wurde getestet und wird von Starbucks nicht berichtet; FMP kennt nur die Summe aus Abschreibung und Amortisation. | Zuerst `SEC.get_concept("Depreciation")` versuchen, bei Fehler auf `DepreciationDepletionAndAmortization` zurueckfallen. Die Naeherung ist unkritisch, da FSAP diesen Wert nur fuer Nebenkennzahlen nutzt. |
| 26 | Market risk premium | `market_risk_premium` | Valuation!F35 | Reine Analystenannahme, kein Marktdatum. | Standardwert 0.06 verwenden, wie im FSAP-Beispiel. Vom Nutzer ueberschreibbar. |
| 27 | Long-run growth assumption | `long_run_growth_assumption` | Valuation!F28-F29 | Reine Analystenannahme. | Standardwert 0.03 verwenden (Vorgabe aus dem FSAP-Beispiel). Vom Nutzer ueberschreibbar. |
| 28 | Preferred stock capital | `preferred_stock_capital` | Valuation!F45 | Nur relevant, wenn Vorzugsaktien existieren; bei den meisten Firmen 0. | Aus Tabelle 1 Nr. 19 ableiten; sonst 0 setzen. |
| 29 | Preferred dividends | `preferred_dividends` | Valuation!F46 | Nur relevant, wenn Vorzugsaktien existieren. | Aus Tabelle 1 Nr. 70 ableiten; sonst 0 setzen. |
| 30 | Preferred implied yield | `preferred_implied_yield` | Valuation!F47 | Ergibt sich erst aus Nr. 28 und Nr. 29. | Nr. 29 geteilt durch Nr. 28; sind beide 0, ebenfalls 0 setzen. |
| 31 | Noncontrolling interests capital | `noncontrolling_interests_capital` | Valuation!F50 | FSAP setzt diesen Wert im Starbucks-Beispiel selbst auf 0. | Aus Tabelle 1 Nr. 24 ableiten; sonst 0 setzen. |
| 32 | Noncontrolling interests earnings | `noncontrolling_interests_earnings` | Valuation!F51 | FSAP setzt diesen Wert im Starbucks-Beispiel selbst auf 0. | Aus Tabelle 1 Nr. 39 ableiten; sonst 0 setzen. |
| 33 | Noncontrolling interests implied yield | `noncontrolling_interests_implied_yield` | Valuation!F52 | Ergibt sich erst aus Nr. 31 und Nr. 32. | Nr. 32 geteilt durch Nr. 31; sind beide 0, ebenfalls 0 setzen. |
| 34 | Anzahl Stores je Segment | `number_of_stores_per_segment` | PDF Exhibit 10.2 | Segment- und Filialzahlen stehen nur im MD&A-Teil des Geschaeftsberichts, keine API liefert sie. | Fuer das Blatt `Data` nicht noetig, nur fuer das feinere Blatt `Forecast Development`. Vorschlag: aus dem Umfang herausnehmen und Umsatz stattdessen ueber Wachstumsraten der Gesamtumsaetze prognostizieren. Wenn die Segmentlogik gewuenscht ist, braucht es einen eigenen LLM-Sub-Graph auf dem 10-K-Text. |
| 35 | Umsatz je Store je Segment | `revenue_per_store_per_segment` | PDF Exhibit 10.2 | Gleiche Ursache wie Nr. 34. | Wie Nr. 34 behandeln. |
| 36 | Neue Stores je Segment | `new_stores_per_segment` | PDF Exhibit 10.2 | Gleiche Ursache wie Nr. 34. | Wie Nr. 34 behandeln. |
| 37 | 53. Woche im Geschaeftsjahr (Faktor 53/52) | `fifty_third_week_in_fiscal_year` | PDF Step 1 | Kalendarische Besonderheit einzelner Firmen, nicht als Datenpunkt abrufbar. | Aus den Geschaeftsjahresenddaten selbst berechnen: liegen zwischen zwei Abschlussstichtagen mehr als 364 Tage, den Faktor 53/52 anwenden. Die Stichtage liefert `FMP.get_income_statement` im Feld `date`. |

---

## Offene Punkte fuer die Umsetzung

1. **Anzahl der Jahre.** Das Blatt `Data` nutzt sechs Geschaeftsjahre, `n_years_history`
   in `FSAPSchema` steht auf 5. Damit hat die Analyse eine Spalte weniger als die Vorlage.
2. **Unit-Argument bei `SEC.get_concept`.** Der Standardwert `"USD"` scheitert bei
   Quoten (`pure`) und Betraegen je Aktie (`USD/shares`). Beim Import muss die Einheit
   je Tag mitgegeben werden.
3. **Vorzeichen.** FSAP erwartet Aufwendungen und Abschreibungen als negative Werte
   (erkennbar an den spitzen Klammern in den Zeilenbeschriftungen), FMP liefert sie
   ueberwiegend positiv. Die Vorzeichenlogik muss beim Mapping festgelegt werden.
