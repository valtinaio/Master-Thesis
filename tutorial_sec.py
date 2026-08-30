# --- SEC Overview ---
# SEC stands for Securities and Exchange Commission and is the
# place where companies listed in a US stock exchange must send
# their financial statements - called "Filings". These 
# filings are public and available through an API. An API
# is simply a "connector" between a Server and any client 
# (myself / my computer). With requests I can do requests to
# a that server. The server is identified through an endpoint
# defined through an URL.

# CIK
# CIK stands for "Central Index Key". Every company listed in 
# SEC has its own CIK. The CIK is needed for any request to 
# the SEC server. Example:

# Libraries
import pandas as pd
import requests

# Create Request Headers
headers = {"User-Agent": "valti.luther@gmail.com"}

# Request: Apple's CIK is 0000320193
cik = "0000320193"
url = f"https://data.sec.gov/submissions/CIK{cik}.json"

response = requests.get(url, headers=headers)
print(response.status_code) # should be 200
data = response.json()
data["accessionNumber"]

# The different keys of data describes all the information
# one can get from a SEC request.
print(data.keys())

# Some specific keys:
print(data["name"])             # Returns the name of the company
print(data["sic"])              # Returns the branche-ID the company is part of
print(data["sicDescription"])   # Returns the name of the branche

# --- The fillings ---
print(data["filings"])          # Are a dictionary themselves
filings = data["filings"]["recent"]

# The structure of filings
# Every company has its own row in each dictionary key =>
filings["form"][0] # and
filings["filingDate"][0]    # belong to the same company because
                            # they are in the same row [0].

# We can transform each of those rows to one dataframe for a
# better readability:
df = pd.DataFrame({
    "form": filings["form"],       # type of statement
    "date": filings["filingDate"], # date of creation
    "accessionNumber": filings["accessionNumber"] # unique ID
})

print(df.head(10))

# --- The "form" ---
# There are different statement types, the most important ones are:
# - 10-K = Yearly, detailed 
# - 10-Q = Quarterly, less detailed
# - 8-K  = Not planned, released only if important things happen "E.g. change of CEO"
# - 4    = Insider (e.g. CEO) has bought or sold stocks.

# --- The accessionNumber ---
# Is a unique ID identifing every filing. Needed to open later
# specific documents. The first part (only) of the accessionNumber is the
# CIK. But accessionNumber != CIK.

# --- Filtering for a certain filing form - e.g. yearly financial statements ---
df_10k = df[df["form"] == "10-K"]

# --- Identifying the CIK for a certain company ---
# SEC provides a mapping file which maps each ticker symobol (e.g. TSLA) to
# a CIK. By using that file one can automatically map the symbol to the 
# corresponding CIK. That file can be found within the following URL:
tickers_url = "https://www.sec.gov/files/company_tickers.json"

# We can request this URL with a request again:
response = requests.get(tickers_url, headers=headers)
companies = response.json()
print(companies["0"])
# Every company has exactly one dictionary, and they are numbered
# consecutively. That number though has no deeper meaning. To find the 
# Every company has three keys:
# 1) cik_str: The CIK number without the leading 0s.
# 2) ticker: The ticker symbol
# 3) title: Offical name of the company
# We can use the following function to find the full(!) CIK of a certain 
# ticker symbol:
def get_cik(ticker):
    for entry in companies.values():
        if entry["ticker"] == ticker.upper():
            return str(entry["cik_str"]).zfill(10)  # fill 0s until 10 numbers are reached in sum
    return None

# IMPORTANT: With get_cik we only get the CIK, but not the actual data
# of that company were looking for. Therefor we follow the same procedure
# as for AAPL before. We create another function, where we apply get_cik:
def get_cik_data(ticker_symbol: str, headers: dict):
    cik = get_cik(ticker_symbol)
    url = url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = requests.get(url, headers=headers)
    data = response.json()
    return data

tesla = get_cik_data("TSLA", headers)
tesla.keys()
tesla["filings"]

# --- Opening a concrete filing document ---
# First we transform the recent filings into a more readable pd.dataframe
# where we now include also the key "primaryDocument" which is the actual
# document we want to read:
filings = tesla["filings"]["recent"]

df = pd.DataFrame({
    "form": filings["form"],
    "date": filings["filingDate"],
    "accessionNumber": filings["accessionNumber"],
    "primaryDocument": filings["primaryDocument"]
})

df_10k = df[df["form"] == "10-K"]
print(df_10k)
# The SEC data is sorted descending by date => First row is always the 
# most recent document:
newest_10k = df_10k.iloc[0]
print(newest_10k)

# Based on the information we get from newest_10k we can now built the
# actual url address to get to the actual document:
accession = newest_10k["accessionNumber"].replace("-", "")
doc = newest_10k["primaryDocument"]
cik_tesla = get_cik("TSLA")

filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik_tesla)}/{accession}/{doc}"
print(filing_url)
# This url inserted inside a browser delivers the original document.

# --- Finding specific data with SEC: XBRL ---
# While one financial data statement of a certain company contains many
# information, it is not handy as a data source to find specific information
# (even they are theoretically included) - such as the revenue for example.
# Therefor SEC provides specific XBRL data.

# For these kind of requests, we need again a specific URL:
cik_tesla = get_cik("TSLA")

concept_url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik_tesla}/us-gaap/Revenues.json"
response = requests.get(concept_url, headers=headers)
revenue_data = response.json()
# This URL contains three different important parts:
# - companyconcept: Defines that we want a specific variable
# - us-gaap: Defines the ruling-framework used to report that variable. Standard = us-gaap
# - Revenues: The concrete variable requested - here equal to revenue.

# Witin the key-combination ["units"]["USD"] one can find the concrete
# values of the variable:
values = revenue_data["units"]["USD"]
revenue_df = pd.DataFrame(values)
print(revenue_df[["end", "val", "form", "fp"]].tail(10))
# fp = Fiscal Period and FY = Fiscal Year => Revenue from that complete year
# IMPORTANT: There are different tag-names for the same variables. For example
# while Tesla uses the tag "Revenue" for the variable Revenue, Apple uses
# the tag name "RevenueFromContractWithCustomerExcludingAssessedTax".

# The tag-names used by any company can be seen under the "companyfacts":
facts_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_tesla}.json"
response = requests.get(facts_url, headers=headers)
facts = response.json()

all_tags = list(facts["facts"]["us-gaap"].keys())
print(len(all_tags))       # How many tags where used in total?
print(all_tags[:20])       # Show the first 20

# In practice one can "search" for a certain variable via the following strategy:
profit_tags = [tag for tag in all_tags if "Income" in tag]
print(profit_tags)

# --- Combining everything into one function ---
def get_variable(ticker_symbol: str, tag: str, headers: dict):
    cik = get_cik(ticker_symbol)
    url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/{tag}.json"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - Tag '{tag}' eventually doesn't exist for {ticker_symbol}")
        return None

    data = response.json()
    df = pd.DataFrame(data["units"]["USD"])
    return df[["end", "val", "form", "fp"]]

apple_df = get_variable("AAPL",
                        "RevenueFromContractWithCustomerExcludingAssessedTax",
                        headers)

apple_df.head()

# --- Requesting more than one company at once, respecting the MAX possible requests ---
import time

ticker_liste = ["AAPL", "TSLA", "MSFT"]

results = {}

for ticker in ticker_liste:
    print(f"Getting data of {ticker}...")
    df = get_variable(ticker, "NetIncomeLoss", headers)
    results[ticker] = df
    time.sleep(0.15)  # 0.15 seconds between requests => Staying under 10 requests / second

results["MSFT"]