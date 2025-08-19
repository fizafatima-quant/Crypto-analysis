from dex_backtester import LiquidityPool, DexBacktester

def simulate_attack():
    pool = LiquidityPool({"ETH": 1000, "USDC": 1000})
    backtester = DexBacktester(pool)
    
    print("Normal swap (1 ETH):", backtester.execute_swap("ETH", 1))
    print("MEV attack (100 ETH):", backtester.execute_swap("ETH", 100))

if __name__ == "__main__":
    simulate_attack()
