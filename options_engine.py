import numpy as np
import logging

class OptionsStrategyEngine:

    def generate_signal(self, df, agent, calls, puts, ticker):
        """Generate trading signal from the latest market data"""
        
        # ✅ FIX: Check if DataFrame has data
        if df is None or df.empty or len(df) == 0:
            return {
                "Ticker": ticker,
                "Signal": "NO DATA",
                "Confidence": 0.0,
                "Spot": 0.0
            }
        
        try:
            latest = df.iloc[-1]
            state = agent.get_state(latest)

            q = agent.q_table.get(state, np.zeros(3))
            probs = q / (np.sum(np.abs(q)) + 1e-6)

            spot = latest['Close']

            if probs[0] > 0.5:
                return {
                    "Ticker": ticker,
                    "Signal": "BUY CALL",
                    "Confidence": round(probs[0], 2),
                    "Spot": spot
                }

            elif probs[1] > 0.5:
                return {
                    "Ticker": ticker,
                    "Signal": "BUY PUT",
                    "Confidence": round(probs[1], 2),
                    "Spot": spot
                }

            return {
                "Ticker": ticker,
                "Signal": "NO TRADE",
                "Confidence": round(probs[2], 2),
                "Spot": spot
            }
        
        except Exception as e:
            logging.error(f"Error generating signal for {ticker}: {e}")
            return {
                "Ticker": ticker,
                "Signal": "ERROR",
                "Confidence": 0.0,
                "Spot": 0.0
            }
