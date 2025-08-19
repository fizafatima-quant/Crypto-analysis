from dex_backtester import LiquidityPool, DexBacktester

def test_large_trades():
    pool = LiquidityPool({"ETH": 1000, "USDC": 200000})
    backtester = DexBacktester(pool, test_mode=True)

    # Normal trade
    amt_out, _ = backtester.execute_swap("ETH", 1)
    assert amt_out > 0, "Normal trade failed"

    # MEV attack attempt
    amt_out, _ = backtester.execute_swap("ETH", 200)
    assert amt_out == 0.0, "MEV attack should be blocked"

    print("✅ Large trade tests passed")

if __name__ == "__main__":
    test_large_trades()
