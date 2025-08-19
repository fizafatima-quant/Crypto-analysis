from dex_backtester import LiquidityPool, DexBacktester

def test_large_trades():
    pool = LiquidityPool({"ETH": 1000, "USDC": 1000})
    backtester = DexBacktester(pool)
    
    # Normal trade
    amt_out, price = backtester.execute_swap("ETH", 1)
    assert amt_out > 0, "Normal trade failed"
    
    # Huge trade should trigger MEV detection or large slippage
    amt_out, price = backtester.execute_swap("ETH", 500)
    assert amt_out < 1000, "Mega trade should not exceed pool reserves"

if __name__ == "__main__":
    test_large_trades()
    print("✅ Large trade tests passed")
