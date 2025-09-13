# scripts/backtest.py
import pandas as pd
import numpy as np
from src.data_fetcher import DataFetcher

def run_simple_backtest(df, signal_col='signal', initial_cash=1000):
    cash = initial_cash
    position = 0.0
    equity = []
    for _, row in df.iterrows():
        price = row['Close']
        if row.get(signal_col) == 1 and position == 0:
            # Buy
            position = cash / price
            cash = 0
        elif row.get(signal_col) == -1 and position > 0:
            # Sell
            cash = position * price
            position = 0
        equity.append(cash + position * price)
    return pd.Series(equity)

if __name__ == "__main__":
    # Fetch historical data for AAPL
    fetcher = DataFetcher("AAPL")
    df = fetcher.get_historical_prices(period="3mo")

    # Generate a simple test signal
    df['signal'] = 0
    df.loc[10, 'signal'] = 1   # Buy at index 10
    df.loc[50, 'signal'] = -1  # Sell at index 50

    equity = run_simple_backtest(df)
    print("Final equity:", equity.iloc[-1])
