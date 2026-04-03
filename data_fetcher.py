import yfinance as yf
import pandas as pd
import requests
from config import DATA_PERIOD, DATA_INTERVAL

def fetch_ohlcv(ticker):
    """Fetch OHLCV data for a given ticker from Yahoo Finance"""
    df = yf.download(ticker, period=DATA_PERIOD, interval=DATA_INTERVAL)

    # 🔴 IMPORTANT FIX: Handle multi-level columns
    if isinstance(df.columns, type(df.columns)):
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    df.dropna(inplace=True)
    return df

def fetch_option_chain(ticker):
    """Fetch option chain data from NSE India API"""
    try:
        # Convert ticker format from .NS to NSE symbol
        symbol = ticker.replace(".NS", "")
        
        # NSE API endpoint
        url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        calls = {}
        puts = {}
        expiries = []
        
        if 'records' in data and 'data' in data['records']:
            for option in data['records']['data']:
                expiry = option.get('expiryDate', '')
                strike = option.get('strikePrice', 0)
                
                if expiry not in expiries:
                    expiries.append(expiry)
                
                # Process call options
                if 'CE' in option and option['CE']:
                    ce_data = option['CE']
                    calls[str(strike)] = {
                        'bid': ce_data.get('bidprice', 0),
                        'ask': ce_data.get('askPrice', 0),
                        'oi': ce_data.get('openInterest', 0),
                        'volume': ce_data.get('totalTradedVolume', 0),
                        'iv': ce_data.get('impliedVolatility', 0)
                    }
                
                # Process put options
                if 'PE' in option and option['PE']:
                    pe_data = option['PE']
                    puts[str(strike)] = {
                        'bid': pe_data.get('bidprice', 0),
                        'ask': pe_data.get('askPrice', 0),
                        'oi': pe_data.get('openInterest', 0),
                        'volume': pe_data.get('totalTradedVolume', 0),
                        'iv': pe_data.get('impliedVolatility', 0)
                    }
        
        return calls, puts, expiries
    
    except Exception as e:
        print(f"Error fetching option chain for {ticker}: {e}")
        return {}, {}, []
