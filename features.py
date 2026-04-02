from ta.momentum import RSIIndicator
from ta.trend import MACD

def compute_features(df):
    df['rsi'] = RSIIndicator(df['Close']).rsi()

    macd = MACD(df['Close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()

    df['returns'] = df['Close'].pct_change()
    df['volatility'] = df['returns'].rolling(20).std()

    df.dropna(inplace=True)
    return df
