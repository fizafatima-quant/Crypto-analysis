from dex_backtester import LiquidityPool, DexBacktester

def demonstrate_mev_protection():
    print("🧪 Demonstrating MEV Protection\n")

    pool = LiquidityPool({"ETH": 1000, "USDC": 200000})
    backtester = DexBacktester(pool, test_mode=True)

    # Normal trade
    out, price = backtester.execute_swap("ETH", 1)
    print(f"✅ Normal trade: {out:.2f} USDC, Price after: {price:.4f}")

    # MEV attack attempt
    out, price = backtester.execute_swap("ETH", 200)  # 20% of pool
    if out == 0.0:
        print(f"❌ MEV attack blocked: {out} USDC")
    else:
        print(f"⚠️ MEV attack went through: {out:.2f} USDC")

if __name__ == "__main__":
    demonstrate_mev_protection()
