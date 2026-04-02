import pandas as pd

class TradeSimulator:

    def __init__(self):
        self.trades = []

    def log_trade(self, result):
        if result["Signal"] != "NO TRADE":
            self.trades.append(result)

    def get_results(self):
        return pd.DataFrame(self.trades)
