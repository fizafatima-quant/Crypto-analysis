# historical_backtester.py
import pandas as pd
from backtester import DEXBacktester  # Make sure this matches your class name

class HistoricalBacktester:
    def __init__(self, historical_data_path: str):
        self.data = pd.read_csv(historical_data_path)
        self.backtester = DEXBacktester()
    
    def run_backtest(self, strategy):
        results = []
        for _, row in self.data.iterrows():
            trade_decision = strategy(row['price'], row['volume'])
            if trade_decision:
                amount = trade_decision['amount']
                try:
                    result = self.backtester.safe_swap("historical_user", "ETH", "USDC", amount)
                except ValueError as e:
                    result = str(e)
                results.append({
                    'timestamp': row['timestamp'],
                    'amount': amount,
                    'result': result,
                    'price': row['price']
                })
        return results
