import pandas as pd

class OptionsEngine:
    def __init__(self, data):
        self.data = data

    def validate_dataframe(self):
        if not isinstance(self.data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame")
        if self.data.empty:
            raise ValueError("DataFrame is empty")

    def process_data(self):
        self.validate_dataframe()
        # Assuming processing involves Accessing the last row
        try:
            last_row = self.data.iloc[-1]
            # Process the last row
            return last_row
        except IndexError:
            raise IndexError("Attempted to access an empty DataFrame")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {e}")