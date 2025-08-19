from dex_backtester import LiquidityPool, DexBacktester
from config import RISK_PARAMS, SLIPPAGE_TOLERANCE, GAS_LIMIT

def test_large_trades():
    pool = LiquidityPool({"ETH": 1000, "USDC": 200000})
    backtester = DexBacktester(pool, test_mode=True)

    # --- Normal trade (should pass) ---
    amt_out, price = backtester.execute_swap("ETH", 1)
    assert amt_out > 0, "❌ Normal trade failed when it should succeed"
    print(f"✅ Normal trade succeeded: {amt_out:.2f} USDC, price after {price:.4f}")

    # --- MEV / risky trade (should be blocked) ---
    risky_trade_size = 200  # ~20% of pool
    amt_out, price = backtester.execute_swap("ETH", risky_trade_size)
    assert amt_out == 0.0, "❌ MEV/risky trade was not blocked"
    print(f"✅ Risky trade of {risky_trade_size} ETH correctly blocked")

    # --- Print config values for visibility ---
    print("\n📊 Config in effect:")
    print(f"   Slippage tolerance: {SLIPPAGE_TOLERANCE:.2%}")
    print(f"   Max position size: {RISK_PARAMS['max_position_size']:.2%} of pool")
    print(f"   Max daily loss: {RISK_PARAMS['max_daily_loss']:.2%}")
    print(f"   Gas limit per swap: {GAS_LIMIT}")

    print("\n🎉 All tests passed")

if __name__ == "__main__":
    test_large_trades()
