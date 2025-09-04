import pandas as pd
from backtester import DEXBacktester

def main():
    # Load data
    try:
        data = pd.read_csv("data.csv")
        print(f"INFO: Data loaded successfully. Shape: {data.shape}")
    except FileNotFoundError:
        print("ERROR: data.csv not found in src/ folder.")
        return

    # Initialize backtester (no arguments needed)
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

if __name__ == "__main__":
    main()
