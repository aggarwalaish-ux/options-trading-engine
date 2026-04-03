import yfinance as yf
import pandas as pd
import requests
import logging
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
    """Fetch option chain data from NSE India API with improved error handling"""
    try:
        # Convert ticker format from .NS to NSE symbol
        symbol = ticker.replace(".NS", "")
        
        # ✅ FIX: NSE API endpoint
        url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"
        
        # ✅ FIX: Enhanced headers for better API compatibility
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.nseindia.com/',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        # ✅ FIX: Create session for better connection handling
        session = requests.Session()
        
        # Initialize session with NSE website
        try:
            session.get('https://www.nseindia.com/', headers=headers, timeout=5)
        except:
            pass  # Continue even if initialization fails
        
        # Fetch options data
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        calls = {}
        puts = {}
        expiries = []
        
        # ✅ FIX: Improved JSON parsing with flexible field names
        if 'records' in data and 'data' in data['records']:
            for option in data['records']['data']:
                expiry = option.get('expiryDate', '')
                strike = option.get('strikePrice', 0)
                
                if expiry and expiry not in expiries:
                    expiries.append(expiry)
                
                # Process call options - try multiple field name variations
                if 'CE' in option and option['CE']:
                    ce_data = option['CE']
                    calls[str(strike)] = {
                        'bid': float(ce_data.get('bidprice') or ce_data.get('bid') or 0),
                        'ask': float(ce_data.get('askPrice') or ce_data.get('ask') or 0),
                        'oi': float(ce_data.get('openInterest') or ce_data.get('oi') or 0),
                        'volume': float(ce_data.get('totalTradedVolume') or ce_data.get('volume') or 0),
                        'iv': float(ce_data.get('impliedVolatility') or ce_data.get('iv') or 0)
                    }
                
                # Process put options - try multiple field name variations
                if 'PE' in option and option['PE']:
                    pe_data = option['PE']
                    puts[str(strike)] = {
                        'bid': float(pe_data.get('bidprice') or pe_data.get('bid') or 0),
                        'ask': float(pe_data.get('askPrice') or pe_data.get('ask') or 0),
                        'oi': float(pe_data.get('openInterest') or pe_data.get('oi') or 0),
                        'volume': float(pe_data.get('totalTradedVolume') or pe_data.get('volume') or 0),
                        'iv': float(pe_data.get('impliedVolatility') or pe_data.get('iv') or 0)
                    }
        
        if calls or puts:
            logging.info(f"✅ Successfully fetched options for {ticker}: {len(calls)} calls, {len(puts)} puts, {len(expiries)} expiries")
        else:
            logging.warning(f"⚠️ No options data returned for {ticker}")
        
        return calls, puts, expiries
    
    except requests.exceptions.ConnectionError as e:
        logging.error(f"🌐 Connection error for {ticker}: {e}")
        return {}, {}, []
    except requests.exceptions.Timeout as e:
        logging.error(f"⏱️ Timeout error for {ticker}: {e}")
        return {}, {}, []
    except requests.exceptions.HTTPError as e:
        logging.error(f"📡 HTTP error for {ticker}: {e}")
        return {}, {}, []
    except ValueError as e:
        logging.error(f"🔴 JSON decode error for {ticker}: {e}")
        return {}, {}, []
    except Exception as e:
        logging.error(f"❌ Unexpected error fetching option chain for {ticker}: {type(e).__name__}: {e}")
        return {}, {}, []
