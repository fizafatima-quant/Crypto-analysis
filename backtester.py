import ccxt
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

class CryptoBacktester:
    def __init__(self, data: pd.DataFrame, initial_balance: float = 100, 
                 fee: float = 0.001, stop_loss_pct: float = 0.02):
        """
        Enhanced backtester with stop-loss functionality
        
        Parameters:
        - data: OHLCV DataFrame
        - initial_balance: Starting capital in quote currency (default $100)
        - fee: Exchange fee percentage (default 0.1%)
        - stop_loss_pct: Stop-loss percentage (default 2%)
        """
        self.data = data
        self.initial_balance = initial_balance
        self.fee = fee
        self.stop_loss_pct = stop_loss_pct
        self.trades = []
        self.active_position = None  # Tracks {entry_price, entry_time}
        self.final_balance = initial_balance

    def calculate_indicators(self):
        """Calculate technical indicators"""
        self.data['SMA_50'] = self.data['close'].rolling(50).mean()
        self.data['SMA_200'] = self.data['close'].rolling(200).mean()

    def generate_signals(self):
        """Generate trading signals"""
        self.data['signal'] = 0
        self.data.loc[self.data['SMA_50'] > self.data['SMA_200'], 'signal'] = 1

    def run_backtest(self):
        """Execute backtest with stop-loss logic"""
        self.calculate_indicators()
        self.generate_signals()
        
        position_size = 0
        balance = self.initial_balance
        
        for idx, row in self.data.iterrows():
            # 1. Check stop-loss trigger first
            if self.active_position:
                stop_loss_price = self.active_position['entry_price'] * (1 - self.stop_loss_pct)
                
                if row['low'] <= stop_loss_price:
                    # Execute at worst possible price
                    execute_price = min(stop_loss_price, row['open'])
                    balance = position_size * execute_price * (1 - self.fee)
                    
                    self.trades.append({
                        'time': idx,
                        'action': 'SELL',
                        'price': execute_price,
                        'type': 'stop-loss',
                        'pnl': (execute_price - self.active_position['entry_price'])/self.active_position['entry_price']
                    })
                    
                    position_size = 0
                    self.active_position = None
                    continue
            
            # 2. Original signal logic
            if row['signal'] == 1 and not self.active_position:
                position_size = balance / row['close'] * (1 - self.fee)
                balance = 0
                self.active_position = {
                    'entry_price': row['close'],
                    'entry_time': idx
                }
                
                self.trades.append({
                    'time': idx,
                    'action': 'BUY',
                    'price': row['close'],
                    'type': 'entry'
                })
                
            elif row['signal'] == 0 and self.active_position:
                balance = position_size * row['close'] * (1 - self.fee)
                
                self.trades.append({
                    'time': idx,
                    'action': 'SELL',
                    'price': row['close'],
                    'type': 'signal-exit',
                    'pnl': (row['close'] - self.active_position['entry_price'])/self.active_position['entry_price']
                })
                
                position_size = 0
                self.active_position = None
        
        # Final account value
        self.final_balance = balance + (position_size * self.data['close'].iloc[-1] * (1 - self.fee))

    def evaluate_performance(self):
        """Calculate performance metrics"""
        exits = [t for t in self.trades if t['action'] == 'SELL']
        
        results = {
            'final_balance': self.final_balance,
            'return_pct': (self.final_balance - self.initial_balance)/self.initial_balance * 100,
            'total_trades': len(exits),
            'stop_loss_hits': len([t for t in exits if t['type'] == 'stop-loss']),
            'win_rate': None,
            'avg_profit': None
        }
        
        if exits:
            results['win_rate'] = len([t for t in exits if t['pnl'] > 0])/len(exits) * 100
            results['avg_profit'] = np.mean([t['pnl'] for t in exits]) * 100
            
        return results

    def plot_results(self):
        """Visualize trades with stop-loss markers"""
        plt.figure(figsize=(12,6))
        plt.plot(self.data.index, self.data['close'], label='Price', alpha=0.5)
        
        # Plot trades
        buys = [t for t in self.trades if t['action'] == 'BUY']
        sells = [t for t in self.trades if t['action'] == 'SELL']
        
        if buys:
            plt.scatter(
                [t['time'] for t in buys],
                [t['price'] for t in buys],
                color='green', label='Buy', marker='^', s=100
            )
        
        if sells:
            for t in sells:
                color = 'red' if t['type'] == 'stop-loss' else 'orange'
                plt.scatter(
                    [t['time']],
                    [t['price']],
                    color=color, label=f'Sell ({t["type"]})', marker='v', s=100
                )
        
        plt.title(f'Backtest Results (Stop-Loss: {self.stop_loss_pct*100}%)')
        plt.legend()
        plt.grid()
        plt.show()

def fetch_live_data(symbol='BTC/USDT', timeframe='1h', limit=500):
    """Fetch OHLCV data from exchange"""
    exchange = ccxt.binance({'enableRateLimit': True})
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df.set_index('timestamp')

if __name__ == "__main__":
    # Load data
    try:
        data = fetch_live_data(timeframe='1h', limit=1000)
        print(f"Loaded data until {data.index[-1]}")
    except Exception as e:
        print(f"Error fetching data: {e}. Using sample data.")
        data = pd.DataFrame({
            'close': np.random.normal(50000, 1000, 200).cumsum(),
            'open': np.random.normal(50000, 1000, 200).cumsum(),
            'high': np.random.normal(50000, 1000, 200).cumsum() + 200,
            'low': np.random.normal(50000, 1000, 200).cumsum() - 200,
            'volume': np.random.randint(1000, 5000, 200)
        }, index=pd.date_range(end=datetime.now(), periods=200))
    
    # Run backtest
    bt = CryptoBacktester(data, stop_loss_pct=0.02)  # 2% stop-loss
    bt.run_backtest()
    
    # Show results
    results = bt.evaluate_performance()
    print("\n=== Backtest Results ===")
    print(f"Initial Balance: ${bt.initial_balance:.2f}")
    print(f"Final Balance: ${results['final_balance']:.2f}")
    print(f"Return: {results['return_pct']:.2f}%")
    print(f"Total Trades: {results['total_trades']}")
    print(f"Stop-Loss Triggers: {results['stop_loss_hits']}")
    print(f"Win Rate: {results['win_rate']:.1f}%")
    print(f"Avg Profit per Trade: {results['avg_profit']:.2f}%")
    
    # Save and plot
    bt.data.to_csv('backtest_results.csv', index=True)
    bt.plot_results()