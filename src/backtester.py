import ccxt
import pandas as pd
import matplotlib.pyplot as plt
import os

def fetch_live_data(symbol='BTC/USDT', timeframe='15m', limit=500):
    """Fetches live OHLCV data from Binance"""
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {
            'adjustForTimeDifference': True
        }
    })
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df.set_index('timestamp')

class CryptoBacktester:
    def __init__(self, data: pd.DataFrame, initial_balance: float = 10000, fee: float = 0.001):
        self.data = data
        self.initial_balance = initial_balance
        self.fee = fee
        self.balance = initial_balance
        self.position = 0
        self.trades = []
        
    def calculate_indicators(self):
        self.data['SMA_50'] = self.data['close'].rolling(50).mean()
        self.data['SMA_200'] = self.data['close'].rolling(200).mean()
        
    def generate_signals(self):
        self.data['signal'] = 0
        self.data.loc[self.data['SMA_50'] > self.data['SMA_200'], 'signal'] = 1
        self.data.loc[self.data['SMA_50'] <= self.data['SMA_200'], 'signal'] = 0
        
    def run_backtest(self):
        self.calculate_indicators()
        self.generate_signals()
        
        for i, row in self.data.iterrows():
            if row['signal'] == 1 and self.position <= 0:
                self.position = self.balance / row['close'] * (1 - self.fee)
                self.balance = 0
                self.trades.append({'time': i, 'action': 'BUY', 'price': row['close']})
            elif row['signal'] == 0 and self.position > 0:
                self.balance = self.position * row['close'] * (1 - self.fee)
                self.position = 0
                self.trades.append({'time': i, 'action': 'SELL', 'price': row['close']})
    
    def evaluate_performance(self):
        if self.position > 0:
            self.balance = self.position * self.data.iloc[-1]['close'] * (1 - self.fee)
        
        return {
            'return_pct': (self.balance - self.initial_balance) / self.initial_balance * 100,
            'num_trades': len(self.trades),
            'final_balance': self.balance
        }

def plot_results(backtester):
    plt.figure(figsize=(12, 6))
    plt.plot(backtester.data.index, backtester.data['close'], label='Price', alpha=0.5)
    
    if backtester.trades:
        buys = [t for t in backtester.trades if t['action'] == 'BUY']
        sells = [t for t in backtester.trades if t['action'] == 'SELL']
        
        if buys:
            plt.scatter(
                [t['time'] for t in buys],
                [t['price'] for t in buys],
                color='green', label='Buy', marker='^', s=100
            )
        if sells:
            plt.scatter(
                [t['time'] for t in sells],
                [t['price'] for t in sells],
                color='red', label='Sell', marker='v', s=100
            )
    
    plt.title('Backtest Results')
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
    print("===== STARTING BACKTEST =====")
    
    try:
        live_data = fetch_live_data()
        print(f"Fetched {len(live_data)} data points up to {live_data.index[-1]}")
    except Exception as e:
        print(f"Failed to fetch live data: {str(e)}")
        print("Using sample data instead...")
        live_data = pd.DataFrame({
            'close': [1000, 1010, 1020, 1030, 1040],
            'open': [990, 1005, 1015, 1025, 1035],
            'high': [1010, 1020, 1030, 1040, 1050],
            'low': [980, 995, 1005, 1015, 1025],
            'volume': [5000, 6000, 7000, 8000, 9000]
        }, index=pd.date_range(start='2023-01-01', periods=5))
    
    backtester = CryptoBacktester(live_data)
    backtester.run_backtest()
    
    results = backtester.evaluate_performance()
    print("\n===== RESULTS =====")
    print(f"Initial Balance: ${backtester.initial_balance:,.2f}")
    print(f"Final Balance: ${results['final_balance']:,.2f}")
    print(f"Return: {results['return_pct']:.2f}%")
    print(f"Trades Executed: {results['num_trades']}")
    
    # Save results AFTER creating backtester
    backtester.data.to_csv('backtest_results.csv', index=True)
    print(f"\nSaved results to: {os.path.abspath('backtest_results.csv')}")
    
    plot_results(backtester)
    input("Press Enter to exit...")