"""
Service to import filings and XBRL data of one company from the SEC API.
This is the fallback source for data the FMP API does not provide, such as depreciation
reported separately from amortization or the statutory tax rate.
"""

# ---------------------------
# Imports
# ---------------------------
import re
import warnings
from typing import Literal

import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

# Modern filings are XHTML, which makes the HTML parser warn on every single call.
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

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
        """Store the symbol, the request headers and the endpoints, and look up the CIK."""

        self.symbol = str(symbol).upper()
        self._headers = {"User-Agent": user_agent_mail}
        self._tickers_url = "https://www.sec.gov/files/company_tickers.json"
        self._endpoints = [
            "https://data.sec.gov/submissions",
            "https://data.sec.gov/api/xbrl/companyfacts",
            "https://data.sec.gov/api/xbrl/companyconcept",
            "https://www.sec.gov/Archives/edgar/data",
        ]
        # Every endpoint below needs the CIK, so it is fetched once and reused.
        self.cik = self.get_cik()

    # ---------------------------
    # Internal request helper
    # ---------------------------
    def _get(self, url: str, html: bool = False) -> dict | str:
        """Send one GET request to the SEC and return the parsed JSON,
        or the plain text of the page when html is True."""

        response = requests.get(url, headers=self._headers)
        if response.status_code != 200:
            raise SECError(f"'{url}' failed with HTTP {response.status_code}: {response.text[:200]}")
        if not html:
            return response.json()
        # get_text() drops every tag, the regex collapses the leftover whitespace into
        # single blanks, so the result is one readable block of text.
        text = BeautifulSoup(response.text, "html.parser").get_text(" ")
        return re.sub(r"\s+", " ", text).strip()

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
    # Endpoints
    # ---------------------------
    def get_submissions(self) -> dict:
        """Return the company profile and the metadata of all its recent filings."""

        return self._get(f"{self._endpoints[0]}/CIK{self.cik}.json")

    def get_companyfacts(self) -> dict:
        """Return all XBRL facts the company has ever reported, grouped by taxonomy and tag."""

        return self._get(f"{self._endpoints[1]}/CIK{self.cik}.json")

    def get_companyconcept(self, tag: str, taxonomy: str = "us-gaap") -> dict:
        """Return one reported line item over time, for example the tag
        'DepreciationDepletionAndAmortization', with all its units and periods."""

        return self._get(f"{self._endpoints[2]}/CIK{self.cik}/{taxonomy}/{tag}.json")

    def get_archives(self, form: FilingForm = "10-K", index: int = 0) -> dict:
        """Return the text of one filing, split into its items, for example 'item_1a'.
        index 0 is the most recent filing of that form type."""

        recent = self.get_submissions()["filings"]["recent"]
        # The SEC returns parallel lists, so one position describes one filing across all lists.
        positions = [n for n, filed in enumerate(recent["form"]) if filed == form]
        if index >= len(positions):
            raise SECError(
                f"'{self.symbol}' has only {len(positions)} recent filings of the form "
                f"'{form}', so index {index} does not exist."
            )
        position = positions[index]
        # The URL holds the accession number without its dashes and the CIK without zeros.
        accession = recent["accessionNumber"][position].replace("-", "")
        url = (f"{self._endpoints[3]}/{int(self.cik)}/{accession}/"
               f"{recent['primaryDocument'][position]}")
        return self._split_items(self._get(url, html=True))

    # ---------------------------
    # Internal text helper
    # ---------------------------
    @staticmethod
    def _split_items(text: str) -> dict:
        """Split the text of a filing into its items and return them keyed by 'item_<number>'."""

        # Matches headings like 'Item 1.', 'ITEM 1A:' or 'Item 7 -' and keeps the number.
        headings = [(found.group(1).upper(), found.start())
                    for found in re.finditer(r"Item\s+(\d{1,2}[A-C]?)\s*[\.\:\-]", text, re.I)]

        # Every item number appears twice: once in the table of contents and once as the real
        # heading. Keeping the longest section per number picks the real one.
        sections = {}
        for number, (item, start) in enumerate(headings):
            end = headings[number + 1][1] if number + 1 < len(headings) else len(text)
            if item not in sections or (end - start) > (sections[item][1] - sections[item][0]):
                sections[item] = (start, end)
        return {f"item_{item.lower()}": text[start:end]
                for item, (start, end) in sections.items()}


if __name__ == "__main__":
    starbucks = SEC("SBUX")
    print("CIK:", starbucks.cik)
    print("Industry:", starbucks.get_submissions()["sicDescription"])
    print("Gross PP&E:", starbucks.get_companyconcept("PropertyPlantAndEquipmentGross")["units"]["USD"][0])
    print("Items:", list(starbucks.get_archives("10-K").keys()))
