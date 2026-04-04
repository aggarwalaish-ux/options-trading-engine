import pandas as pd
import logging
from config import NIFTY_50
from data_fetcher import fetch_ohlcv, fetch_option_chain
from nse_fetcher import fetch_nifty_option_chain
calls, puts, expiries = fetch_nifty_option_chain()
from nse_fetcher import fetch_option_chain_nse
from features import compute_features
from rl_agent import TradingAgent
from options_engine import OptionsStrategyEngine
from simulator import TradeSimulator

def run_pipeline():
    agent = TradingAgent()
    engine = OptionsStrategyEngine()
    simulator = TradeSimulator()

    results = []

    for ticker in NIFTY_50:
        try:
            df = fetch_ohlcv(ticker)
            
            # ✅ FIX: Check if data is available
            if df is None or len(df) < 30:
                logging.warning(f"Insufficient data for {ticker}, skipping...")
                continue
            
            df = compute_features(df)
            
            # ✅ FIX: Check if DataFrame is empty after feature computation
            if df.empty or len(df) == 0:
                logging.warning(f"No valid features for {ticker} after processing, skipping...")
                continue
            
            # RL Training loop
            for i in range(max(0, len(df) - 5)):
                try:
                    state = agent.get_state(df.iloc[i])
                    action = agent.choose_action(state)
                    
                    if i + 5 < len(df):
                        reward = (df['Close'].iloc[i+5] - df['Close'].iloc[i]) / df['Close'].iloc[i]
                        agent.update(state, action, reward)
                except Exception as e:
                    logging.warning(f"Error in training loop for {ticker}: {e}")
                    continue
            
            # Fetch options and generate signal
            symbol = ticker.replace(".NS", "")
            calls, puts, expiries = fetch_nifty_option_chain()
            
            # ✅ FIX: Safe signal generation with error handling
            result = engine.generate_signal(df, agent, calls, puts, ticker)
            
            results.append(result)
            simulator.log_trade(result)
            
        except Exception as e:
            logging.error(f"Error processing {ticker}: {e}")
            continue

    # ✅ FIX: Handle case where no results are available
    if not results:
        results = [{
            "Ticker": "N/A",
            "Signal": "NO DATA",
            "Confidence": 0.0,
            "Spot": 0.0
        }]
    
    return pd.DataFrame(results), simulator.get_results()
