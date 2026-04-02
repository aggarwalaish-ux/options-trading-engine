import yfinance as yf
import pandas as pd

def fetch_ohlcv(ticker):
    df = yf.download(ticker, period="2y", interval="1d")

    # 🔴 IMPORTANT FIX
    if isinstance(df.columns, type(df.columns)):
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    df.dropna(inplace=True)
    return df

def fetch_option_chain(ticker):
    """Fetch option chain data for the given ticker"""
    # Placeholder implementation - returns empty tuples
    # In production, integrate with NSE API or other data source
    calls = {}
    puts = {}
    expiries = []
    return calls, puts, expiries
