import pandas as pd

class TradingEngine:
    def __init__(self, data):
        self.data = data

    def validate_data(self):
        if not isinstance(self.data, pd.DataFrame):
            raise ValueError("Data is not a DataFrame")
        if self.data.empty:
            raise ValueError("DataFrame is empty")

    def generate_signal(self):
        if self.data is None or self.data.empty:
            return 'NO DATA'
        try:
            self.validate_data()
            signal = self.data.iloc[-1]['signal']  # Replace with your actual logic
            return signal
        except Exception as e:
            print(f'Error in generating signal: {e}')
            return 'ERROR'

# Example usage:
# data = pd.DataFrame(...)  # Your DataFrame initialization
# engine = TradingEngine(data)
# signal = engine.generate_signal()