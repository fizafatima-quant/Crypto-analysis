import backtrader as bt
import pandas as pd
from datetime import datetime

class FinalStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('rsi_high', 70),
        ('rsi_low', 30),
    )

    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)

    def next(self):
        if not self.position:
            if self.rsi < self.p.rsi_low:
                self.buy(size=self.broker.getcash() / self.data.close[0] * 0.95)
        else:
            if self.rsi > self.p.rsi_high:
                self.sell(size=self.position.size)

def run_backtest(data_path):
    try:
        # 1. Load and convert data
        df = pd.read_csv(data_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])  # Convert to datetime
        
        # 2. Create Data Feed with proper datetime handling
        data = bt.feeds.PandasData(
            dataname=df,
            datetime=0,  # Use already converted datetime
            open=1,
            high=2,
            low=3,
            close=4,
            volume=5,
            openinterest=-1
        )
        
        # 3. Run backtest
        cerebro = bt.Cerebro()
        cerebro.adddata(data)
        cerebro.addstrategy(FinalStrategy)
        cerebro.broker.setcash(10000.0)
        
        print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
        cerebro.run()
        print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
        
        # Optional plotting
        cerebro.plot(style='candlestick')
        
    except Exception as e:
        print(f"\n❌ Critical Error: {str(e)}")
        print("\nDebug Info:")
        print(f"First timestamp type: {type(df.iloc[0,0])}")
        print(f"First 5 timestamps: {df['timestamp'].head().tolist()}")

if __name__ == "__main__":
    print("\n🚀 Running Final Backtest...")
    run_backtest("data/BTC-USDT_1d.csv")