# src/main.py

import os
import pandas as pd
from backtester import DEXBacktester
from src.data_fetcher import DataFetcher
from src.executor import Executor
from dotenv import load_dotenv

# Load environment variables for paper trading
load_dotenv()
TRADE_MODE = os.getenv("TRADE_MODE", "paper")
executor = Executor(mode=TRADE_MODE)

# -------------------------------
# Paper trading functions
# -------------------------------
def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Example strategy:
    - Buy if price > 5-period MA
    - Sell if price < 5-period MA
    """
    df['MA5'] = df['Close'].rolling(5).mean()
    df['signal'] = 0
    df.loc[df['Close'] > df['MA5'], 'signal'] = 1   # Buy
    df.loc[df['Close'] < df['MA5'], 'signal'] = -1  # Sell
    return df

def run_paper_trading(ticker: str):
    fetcher = DataFetcher(ticker)
    df = fetcher.get_historical_prices(period="1mo")
    df = generate_signals(df)

    for idx, row in df.iterrows():
        if row['signal'] == 1:
            executor.place_order(ticker, "buy", amount=1, price=row['Close'])
        elif row['signal'] == -1:
            executor.place_order(ticker, "sell", amount=1, price=row['Close'])

    print(f"Paper trading for {ticker} completed.")

# -------------------------------
# DEX backtesting functions
# -------------------------------
def run_dex_backtest():
    # Load data from CSV
    try:
        data = pd.read_csv("data.csv")
        print(f"INFO: Data loaded successfully. Shape: {data.shape}")
    except FileNotFoundError:
        print("ERROR: data.csv not found in src/ folder.")
        return

    # Initialize backtester
    backtester = DEXBacktester()

    # Provide initial liquidity
    backtester.provide_liquidity("Alice", "BTC", "USDT", 1000, 30000)

    # Execute swaps from CSV
    for _, row in data.iterrows():
        amount_in = row["volume"]
        try:
            backtester.safe_swap("Alice", "BTC", "USDT", amount_in)
        except ValueError as e:
            print(f"Swap failed: {e}")

    # Print performance report
    report = backtester.monitor.get_report()
    print("Performance report:")
    print(f"Success rate: {report['success_rate']*100:.2f}%")
    print(f"MEV block rate: {report['mev_block_rate']*100:.2f}%")
    print(f"Slippage revert rate: {report['slippage_revert_rate']*100:.2f}%")

# -------------------------------
# Main entry
# -------------------------------
if __name__ == "__main__":
    # Run both systems independently
    run_paper_trading("AAPL")
    run_dex_backtest()
