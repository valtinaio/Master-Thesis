"""
Service to import filings and XBRL data of one company from the SEC API.
This is the fallback source for data the FMP API does not provide, such as depreciation
reported separately from amortization or the statutory tax rate.
"""

# ---------------------------
# Imports
# ---------------------------
from typing import Literal

import requests

# The SEC requires every request to identify the caller by mail address.
DEFAULT_USER_AGENT = "valti.luther@gmail.com"

# The type aliases make the allowed argument values visible in every method signature.
FilingForm = Literal["10-K", "10-Q", "8-K", "4", "DEF 14A", "20-F"]
FactPeriod = Literal["annual", "quarterly", "all"]


class SECError(Exception):
    """Raised when an SEC request fails, naming the URL and the reason."""


class SEC:
    """Imports filings and XBRL facts of one symbol from the SEC; every method fetches on demand."""

    def __init__(self, symbol: str, user_agent_mail: str = DEFAULT_USER_AGENT):
        """Store the symbol and the request headers without performing any request."""

        self.symbol = str(symbol).upper()
        self._headers = {"User-Agent": user_agent_mail}
        self._tickers_url = "https://www.sec.gov/files/company_tickers.json"

    # ---------------------------
    # Internal request helper
    # ---------------------------
    def _get(self, url: str) -> dict:
        """Send one GET request to the SEC and return the parsed JSON."""

        response = requests.get(url, headers=self._headers)
        if response.status_code != 200:
            raise SECError(f"'{url}' failed with HTTP {response.status_code}: {response.text[:200]}")
        return response.json()

    # ---------------------------
    # Company identification
    # ---------------------------
    def get_cik(self) -> str:
        """Return the ten-digit Central Index Key (CIK) that the SEC uses to identify the company."""

        companies = self._get(self._tickers_url)
        for entry in companies.values():
            if entry["ticker"] == self.symbol:
                # The SEC expects the CIK padded with leading zeros to ten digits.
                return str(entry["cik_str"]).zfill(10)
        raise SECError(f"The symbol '{self.symbol}' was not found in the SEC ticker list.")

    # ---------------------------
    # Filings
    # ---------------------------
    def get_filings(self, form: FilingForm = "10-K", limit: int = 5) -> list[dict]:
        """Return the most recent filings of one form type, including the document URL of each."""

        cik = self.get_cik()
        submissions = self._get(f"https://data.sec.gov/submissions/CIK{cik}.json")
        recent = submissions["filings"]["recent"]

        filings = []
        # The SEC returns parallel lists, so one index describes one filing across all lists.
        for index, filing_form in enumerate(recent["form"]):
            if filing_form != form:
                continue
            accession = recent["accessionNumber"][index].replace("-", "")
            document = recent["primaryDocument"][index]
            filings.append({
                "form": filing_form,
                "filing_date": recent["filingDate"][index],
                "report_date": recent["reportDate"][index],
                "accession_number": recent["accessionNumber"][index],
                "document_url": (f"https://www.sec.gov/Archives/edgar/data/"
                                 f"{int(cik)}/{accession}/{document}"),
            })
            if len(filings) == limit:
                break
        return filings

    # ---------------------------
    # XBRL data
    # ---------------------------
    def get_company_facts(self) -> dict:
        """Return all XBRL facts the company has ever reported, grouped by taxonomy and tag."""

        cik = self.get_cik()
        return self._get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")

    def get_concept(self,
                    tag: str,
                    unit: str = "USD",
                    period: FactPeriod = "annual",
                    taxonomy: str = "us-gaap") -> list[dict]:
        """Return one reported line item over time, for example the tag 'DepreciationDepletionAndAmortization'."""

        cik = self.get_cik()
        concept = self._get(f"https://data.sec.gov/api/xbrl/companyconcept/"
                            f"CIK{cik}/{taxonomy}/{tag}.json")
        if unit not in concept["units"]:
            raise SECError(f"The tag '{tag}' is not reported in the unit '{unit}'.")

        # The form tells the period length: 10-K reports a year, 10-Q reports a quarter.
        wanted_forms = {"annual": ["10-K"], "quarterly": ["10-Q"]}.get(period)

        # One period appears in several filings, because every report repeats the previous
        # periods as comparatives. Keyed by period, the last entry wins and that is the
        # most recently filed value, which also reflects any later restatement.
        facts = {}
        for fact in concept["units"][unit]:
            if wanted_forms is not None and fact["form"] not in wanted_forms:
                continue
            facts[(fact.get("start"), fact["end"])] = {
                "start": fact.get("start"),
                "end": fact["end"],
                "value": fact["val"],
                "fiscal_year": fact["fy"],
                "fiscal_period": fact["fp"],
                "form": fact["form"],
            }
        # Sorted by end date, so the oldest period comes first and the newest last.
        return sorted(facts.values(), key=lambda fact: fact["end"])


if __name__ == "__main__":
    starbucks = SEC("SBUX")
    print("CIK:", starbucks.get_cik())
    print("Filings:", starbucks.get_filings("10-K", limit=2))
    print("Depreciation:", starbucks.get_concept("DepreciationDepletionAndAmortization")[:2])
