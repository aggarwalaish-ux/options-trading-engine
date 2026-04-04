import requests
import pandas as pd

BASE_URL = "https://www.nseindia.com"
OPTION_CHAIN_API = "https://www.nseindia.com/api/option-chain-equities?symbol={}"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

session = requests.Session()


def get_cookies():
    """Initialize session to get NSE cookies"""
    session.get(BASE_URL, headers=HEADERS, timeout=5)


def fetch_option_chain_nse(symbol):
    try:
        get_cookies()

        url = OPTION_CHAIN_API.format(symbol)
        response = session.get(url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            print(f"Failed NSE fetch for {symbol}")
            return None, None, None

        data = response.json()

        records = data.get("records", {})
        expiry_dates = records.get("expiryDates", [])

        rows = records.get("data", [])

        calls = []
        puts = []

        for row in rows:
            strike = row.get("strikePrice")

            if "CE" in row:
                ce = row["CE"]
                calls.append({
                    "strike": strike,
                    "lastPrice": ce.get("lastPrice"),
                    "openInterest": ce.get("openInterest"),
                    "impliedVolatility": ce.get("impliedVolatility")
                })

            if "PE" in row:
                pe = row["PE"]
                puts.append({
                    "strike": strike,
                    "lastPrice": pe.get("lastPrice"),
                    "openInterest": pe.get("openInterest"),
                    "impliedVolatility": pe.get("impliedVolatility")
                })

        calls_df = pd.DataFrame(calls)
        puts_df = pd.DataFrame(puts)

        return calls_df, puts_df, expiry_dates

    except Exception as e:
        print(f"NSE fetch error for {symbol}: {e}")
        return None, None, None
