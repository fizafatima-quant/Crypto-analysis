import pandas as pd
from backtester import DEXBacktester  # Use your existing backtester

class HistoricalBacktester:
    def __init__(self, historical_data_path: str):
        self.data = pd.read_csv(historical_data_path)
        self.backtester = DEXBacktester()
        
        # Setup an initial pool
        self.backtester.user_balances["historical_user"] = {"ETH": 10000, "USDC": 2000000}
        self.backtester.provide_liquidity("historical_user", "ETH", "USDC", 10000, 2000000)
    
    def run_backtest(self, strategy):
        """Run a trading strategy on historical data"""
        results = []
        for index, row in self.data.iterrows():
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
