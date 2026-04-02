import yfinance as yf

def fetch_ohlcv(ticker):
    df = yf.download(ticker, period="2y", interval="1d")
    df.dropna(inplace=True)
    return df

def fetch_option_chain(ticker):
    try:
        stock = yf.Ticker(ticker)
        expiries = stock.options
        if not expiries:
            return None, None, None

        opt = stock.option_chain(expiries[0])
        return opt.calls, opt.puts, expiries
    except:
        return None, None, None
