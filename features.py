import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD

def compute_features(df):

    # ✅ FORCE 1D SERIES (FIX)
    close = df['Close']
    if hasattr(close, "ndim") and close.ndim > 1:
        close = close.squeeze()

    # RSI
    df['rsi'] = RSIIndicator(close).rsi()

    # MACD
    macd = MACD(close)
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()

    # Returns + Volatility
    df['returns'] = close.pct_change()
    df['volatility'] = df['returns'].rolling(20).std()

    df.dropna(inplace=True)

    return df