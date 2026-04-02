import numpy as np

ACTIONS = ["BUY CALL", "BUY PUT", "NO TRADE"]

class TradingAgent:
    def __init__(self):
        self.q_table = {}

    def get_state(self, row):
        return (
            int(row['rsi'] // 10),
            int(row['macd'] > row['macd_signal']),
            round(row['volatility'], 3)
        )

    def choose_action(self, state):
        if state not in self.q_table:
            self.q_table[state] = np.zeros(3)
        return np.argmax(self.q_table[state])

    def update(self, state, action, reward):
        self.q_table[state][action] += 0.1 * (
            reward - self.q_table[state][action]
        )
