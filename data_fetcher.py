def fetch_ohlcv(ticker):
    df = yf.download(ticker, period="2y", interval="1d")

    # 🔴 IMPORTANT FIX
    if isinstance(df.columns, type(df.columns)):
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    df.dropna(inplace=True)
    return df
