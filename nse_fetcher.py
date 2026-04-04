import requests
import pandas as pd
import time

BASE_URL = "https://www.nseindia.com"
API_URL = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json",
}

session = requests.Session()


def get_nse_data():
    for attempt in range(3):
        try:
            # Step 1: Get cookies
            session.get(BASE_URL, headers=HEADERS, timeout=5)

            # Step 2: Fetch data
            response = session.get(API_URL, headers=HEADERS, timeout=10)

            if response.status_code == 200:
                return response.json()

            time.sleep(1)

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            time.sleep(1)

    return None


def fetch_nifty_option_chain():
    data = get_nse_data()

    if data is None:
        return None, None, None

    records = data.get("records", {})
    expiry_dates = records.get("expiryDates", [])
    rows = records.get("data", [])

    calls, puts = [], []

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

    return pd.DataFrame(calls), pd.DataFrame(puts), expiry_dates
