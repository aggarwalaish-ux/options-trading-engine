import pandas as pd
from config import NIFTY_50
from data_fetcher import fetch_ohlcv, fetch_option_chain
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
        df = fetch_ohlcv(ticker)
        df = compute_features(df)

        for i in range(len(df) - 5):
            state = agent.get_state(df.iloc[i])
            action = agent.choose_action(state)

            reward = (df['Close'].iloc[i+5] - df['Close'].iloc[i]) / df['Close'].iloc[i]
            agent.update(state, action, reward)

        calls, puts, expiries = fetch_option_chain(ticker)

        result = engine.generate_signal(df, agent, calls, puts, ticker)

        results.append(result)
        simulator.log_trade(result)

    return pd.DataFrame(results), simulator.get_results()
