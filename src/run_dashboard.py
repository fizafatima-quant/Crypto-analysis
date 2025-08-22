from backtester import DEXBacktester
from visualizer import PerformanceVisualizer

dex = DEXBacktester()
dex.user_balances["alice"] = {"ETH": 10, "USDC": 50000}

print("===== DEX Backtester for Dashboard =====")

# Provide partial liquidity
dex.provide_liquidity("alice", "ETH", "USDC", 5, 10000)

# Perform multiple swaps safely
swap_amounts = [1, 0.5, 1, 0.5, 1]
for amt in swap_amounts:
    try:
        dex.safe_swap("alice", "ETH", "USDC", amt)
        print(f"✅ Swapped {amt} ETH for USDC")
    except ValueError as e:
        print(f"🚨 {e}")

# Generate dashboard
visualizer = PerformanceVisualizer(dex)
visualizer.create_dashboard()
print("✅ Dashboard created as 'performance_dashboard.png'")
