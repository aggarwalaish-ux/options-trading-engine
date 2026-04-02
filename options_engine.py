import numpy as np

class OptionsStrategyEngine:

    def generate_signal(self, df, agent, calls, puts, ticker):
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
