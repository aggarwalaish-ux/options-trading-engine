import yfinance as yf
import pandas as pd
import logging
from config import DATA_PERIOD, DATA_INTERVAL

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fetch_ohlcv(ticker):
    """Fetch OHLCV data for a given ticker from Yahoo Finance"""
    try:
        logger.info(f"📥 Fetching OHLCV data for {ticker} (period={DATA_PERIOD})")
        df = yf.download(ticker, period=DATA_PERIOD, interval=DATA_INTERVAL, progress=False)

        # Handle multi-level columns
        if isinstance(df.columns, type(df.columns)):
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

        df.dropna(inplace=True)
        logger.info(f"✅ Successfully fetched {len(df)} rows for {ticker}")
        return df
    except Exception as e:
        logger.error(f"❌ Error fetching OHLCV for {ticker}: {e}")
        return pd.DataFrame()

def fetch_option_chain(ticker):
    """
    Fetch option chain data from NSE using NSEPython library
    This is the most reliable method for NSE data in 2025
    """
    try:
        # Convert ticker format from .NS to NSE symbol (remove .NS suffix)
        symbol = ticker.replace(".NS", "")
        logger.info(f"🔍 Fetching options for {ticker} (symbol: {symbol})")
        
        # Try using NSEPython
        try:
            from nsepython import nse_optionchain_scrapper
            logger.debug(f"📚 Using NSEPython library")
            
            logger.debug(f"⏳ Calling nse_optionchain_scrapper({symbol})...")
            data = nse_optionchain_scrapper(symbol)
            
            logger.debug(f"✅ NSEPython returned data type: {type(data)}")
            
            calls = {}
            puts = {}
            expiries = []
            
            # Parse NSEPython response
            if isinstance(data, dict):
                logger.debug(f"🔑 Top-level keys: {list(data.keys())}")
                
                # Get expiry dates
                if 'expiryDates' in data:
                    expiries = data['expiryDates']
                    logger.info(f"📅 Available expiry dates: {expiries}")
                
                # Parse records
                if 'records' in data and 'data' in data['records']:
                    records = data['records']['data']
                    logger.debug(f"📊 Total records: {len(records)}")
                    
                    for idx, record in enumerate(records):
                        strike = record.get('strikePrice', 0)
                        
                        # Parse Call data
                        if 'CE' in record and record['CE']:
                            ce = record['CE']
                            try:
                                calls[str(strike)] = {
                                    'bid': float(ce.get('bidprice', 0)),
                                    'ask': float(ce.get('askPrice', 0)),
                                    'oi': float(ce.get('openInterest', 0)),
                                    'volume': float(ce.get('totalTradedVolume', 0)),
                                    'iv': float(ce.get('impliedVolatility', 0)),
                                    'ltp': float(ce.get('lastPrice', 0))
                                }
                                if idx < 2:
                                    logger.debug(f"  ✅ CE Strike {strike}: {calls[str(strike)]}")
                            except Exception as e:
                                logger.warning(f"  ⚠️ Error parsing CE at strike {strike}: {e}")
                        
                        # Parse Put data
                        if 'PE' in record and record['PE']:
                            pe = record['PE']
                            try:
                                puts[str(strike)] = {
                                    'bid': float(pe.get('bidprice', 0)),
                                    'ask': float(pe.get('askPrice', 0)),
                                    'oi': float(pe.get('openInterest', 0)),
                                    'volume': float(pe.get('totalTradedVolume', 0)),
                                    'iv': float(pe.get('impliedVolatility', 0)),
                                    'ltp': float(pe.get('lastPrice', 0))
                                }
                                if idx < 2:
                                    logger.debug(f"  ✅ PE Strike {strike}: {puts[str(strike)]}")
                            except Exception as e:
                                logger.warning(f"  ⚠️ Error parsing PE at strike {strike}: {e}")
                
                logger.info(f"✅ Parsed {len(calls)} calls and {len(puts)} puts for {ticker}")
                return calls, puts, expiries
            
            else:
                logger.warning(f"⚠️ Unexpected data type from NSEPython: {type(data)}")
                return {}, {}, []
        
        except ImportError:
            logger.warning(f"⚠️ NSEPython not installed. Install with: pip install nsepython")
            logger.info(f"📝 Falling back to empty data...")
            return {}, {}, []
    
    except Exception as e:
        logger.error(f"❌ Error fetching option chain for {ticker}: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return {}, {}, []
