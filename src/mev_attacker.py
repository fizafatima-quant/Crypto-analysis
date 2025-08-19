from dex_backtester import LiquidityPool, DexBacktester
from config import RISK_PARAMS, SLIPPAGE_TOLERANCE

def demonstrate_mev_protection():
    print("🧪 Demonstrating MEV Protection\n")

    pool = LiquidityPool({"ETH": 1000, "USDC": 200000})
    backtester = DexBacktester(pool, test_mode=True)

    # Normal trade
    out, price = backtester.execute_swap("ETH", 1)
    print(f"✅ Normal trade executed:")
    print(f"   Output: {out:.2f} USDC")
    print(f"   Price after: {price:.4f}")
    print(f"   Gas used so far: {SLIPPAGE_TOLERANCE*100:.2f}")

    # MEV attack attempt
    out, price = backtester.execute_swap("ETH", 200)  # 20% of pool
    if out == 0.0:
        print("\n❌ Risky trade of 200 ETH blocked")
        print("   Reason: Exceeded risk, slippage, or MEV check")
    else:
        print("\n⚠️ MEV attack went through!")
        print(f"   Output: {out:.2f} USDC")

    # Display config
    print("\n📊 Config Parameters in effect:")
    print(f"   Slippage tolerance: {SLIPPAGE_TOLERANCE*100:.2f}%")
    print(f"   Max position size: {RISK_PARAMS['max_position_size']*100:.2f}% of pool")
    print(f"   Max daily loss: {RISK_PARAMS['max_daily_loss']*100:.2f}%")

if __name__ == "__main__":
    demonstrate_mev_protection()
