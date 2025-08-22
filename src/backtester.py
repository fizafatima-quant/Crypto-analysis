# backtester.py
from DEXBacktester import DEXBacktester

if __name__ == "__main__":
    dex = DEXBacktester()
    dex.user_balances["alice"] = {"ETH": 100, "USDC": 50000}

    print("===== DEX Backtester =====")

    print("\n[1] Creating ETH-USDC pool")
    dex.provide_liquidity("alice", "ETH", "USDC", 10, 20000)

    print("\n[2] Alice swaps ETH for USDC")
    try:
        dex.safe_swap("alice", "ETH", "USDC", 1)
    except ValueError as e:
        print(f"🚨 {e}")

    report = dex.monitor.get_report()
    print("\n[Performance Report]")
    for k, v in report.items():
        print(f"{k}: {v:.2f}")

    print("\n[Final State]")
    print("Alice balances:", dex.user_balances["alice"])
    print("Alice LP positions:", dex.user_lp_positions["alice"])
    print("ETH-USDC pool reserves:", dex.amm.pools["ETH-USDC"].reserves)
