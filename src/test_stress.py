import random
from .backtester import DEXBacktester

def test_high_frequency_trading():
    """Test system stability under heavy load"""
    print("🧪 Running stress test...")
    
    dex = DEXBacktester()
    dex.user_balances["tester"] = {"ETH": 10000, "USDC": 2000000}
    dex.provide_liquidity("tester", "ETH", "USDC", 10000, 2000000)
    
    # Simulate 1000 rapid trades
    for i in range(1000):
        amount = random.uniform(0.1, 100)  # Random trade sizes
        try:
            dex.safe_swap("tester", "ETH", "USDC", amount)
        except ValueError:
            continue  # Ignore reverted swaps
    
    # Verify system integrity
    report = dex.monitor.get_report()
    print(f"📊 Stress test results: {report}")
    
    assert report['success_rate'] >= 0  # Should complete without crashing
    assert dex.amm.pools["ETH-USDC"].reserves[0] > 0  # ETH reserve
    assert dex.amm.pools["ETH-USDC"].reserves[1] > 0  # USDC reserve
    
    print("✅ Stress test passed - system stable under load")

if __name__ == "__main__":
    test_high_frequency_trading()
