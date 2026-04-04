import pandas as pd
from nse_fetcher import fetch_nifty_option_chain

calls, puts, expiries = fetch_nifty_option_chain()

if calls is not None:
    calls.to_csv("nifty_calls.csv", index=False)
    puts.to_csv("nifty_puts.csv", index=False)

    print("✅ Data saved locally")
else:
    print("❌ Failed to fetch NSE data")
