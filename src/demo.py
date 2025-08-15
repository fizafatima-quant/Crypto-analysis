from dex_backtester import DexBacktester

dex = DexBacktester()

# 1. Add liquidity
dex.add_liquidity("Alice", "USDC", "ETH", 1000.0, 1.0)

# 2. Execute swap
pool = dex.pools["USDC-ETH"]
output = pool.execute_swap(100.0, "USDC")

print(f"Received {output:.6f} ETH")
print(f"New reserves: {pool.reserves}")
print(f"Alice's LP tokens: {dex.lp_positions['Alice']['USDC-ETH']}")