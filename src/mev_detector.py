import numpy as np
from typing import Dict, Optional

def is_sandwich_safe(trade_amount: float, pool_reserves: Dict[str, float], historical_data: Optional[Dict] = None) -> bool:
    """
    Enhanced MEV detection with multiple protection layers
    """
    # 1. Basic validation
    if len(pool_reserves) != 2:
        return False
    
    token_a, token_b = pool_reserves.keys()
    reserve_a, reserve_b = pool_reserves.values()
    
    # 2. Pool Ratio Check - Prevent trades in imbalanced pools
    pool_ratio = reserve_b / reserve_a
    if not (1000 <= pool_ratio <= 3000):  # Reasonable WETH/USDC range
        return False
    
    # 3. Trade Impact Analysis - Prevent large trades that cause significant slippage
    min_reserve = min(reserve_a, reserve_b)
    trade_impact = trade_amount / min_reserve
    
    # Dynamic threshold: 1% for small pools, 0.5% for large pools
    max_impact = 0.01 if min_reserve < 5000 else 0.005
    if trade_impact > max_impact:
        return False
    
    # 4. Reserve Spike Detection - Prevent trades during abnormal reserve changes
    if historical_data and 'reserves' in historical_data and len(historical_data['reserves']) >= 2:
        last_reserve_a = historical_data['reserves'][-1][token_a]
        last_reserve_b = historical_data['reserves'][-1][token_b]
        
        # Calculate percentage changes
        current_change_a = abs(reserve_a - last_reserve_a) / last_reserve_a
        current_change_b = abs(reserve_b - last_reserve_b) / last_reserve_b
        
        # Always block extremely large changes regardless of history
        if current_change_a > 0.25 or current_change_b > 0.25:  # 25%+ change
            return False
        
        # Statistical detection for sufficient historical data
        if len(historical_data['reserves']) >= 3:
            changes_a = []
            for i in range(1, len(historical_data['reserves'])):
                prev = historical_data['reserves'][i-1][token_a]
                curr = historical_data['reserves'][i][token_a]
                change = abs(curr - prev) / prev
                if change > 0.0001:  # Include very small changes for stable pools
                    changes_a.append(change)
            
            if changes_a:
                avg_change = np.mean(changes_a)
                std_change = np.std(changes_a) if len(changes_a) > 1 else 0
                
                # For stable pools (low volatility), be more sensitive
                if avg_change < 0.01:  # Very stable pool (<1% avg change)
                    stability_threshold = 0.08  # 8% change is suspicious
                elif avg_change < 0.05:  # Moderately stable pool
                    stability_threshold = 0.12  # 12% change is suspicious
                else:  # Volatile pool
                    stability_threshold = avg_change + 2 * std_change
            else:
                # No historical variation → perfectly stable pool
                stability_threshold = 0.05  # 5% max allowed change
             
            # Block if change exceeds stability threshold
            if current_change_a > stability_threshold or current_change_b > stability_threshold:
                return False
        else:
            # Simple threshold for limited data
            if current_change_a > 0.15 or current_change_b > 0.15:
                return False
    
    return True


def analyze_trade_scenarios():
    """Test various trade scenarios to verify detection logic"""
    print("🔍 MEV Attack Detection System")
    print("=" * 50)
    
    # Test scenarios
    test_cases = [
        {
            "name": "Normal small trade in balanced pool",
            "trade_amount": 5,
            "pool": {"WETH": 1000, "USDC": 2000000},
            "history": {"reserves": [{"WETH": 990, "USDC": 1980000}]},
            "expected": True
        },
        {
            "name": "Large trade causing high slippage",
            "trade_amount": 50,
            "pool": {"WETH": 1000, "USDC": 2000000},
            "history": None,
            "expected": False
        },
        {
            "name": "Trade in extremely imbalanced pool",
            "trade_amount": 5,
            "pool": {"WETH": 100, "USDC": 2000000},  # 1:20,000 ratio
            "history": None,
            "expected": False
        },
        {
            "name": "Trade during 50% reserve drain attack",
            "trade_amount": 5,
            "pool": {"WETH": 500, "USDC": 1000000},  # 50% drop
            "history": {"reserves": [
                {"WETH": 1000, "USDC": 2000000},
                {"WETH": 1000, "USDC": 2000000}
            ]},
            "expected": False
        },
        {
            "name": "Trade with normal 1% reserve fluctuation",
            "trade_amount": 5,
            "pool": {"WETH": 990, "USDC": 1980000},  # 1% drop
            "history": {"reserves": [
                {"WETH": 1000, "USDC": 2000000},
                {"WETH": 1000, "USDC": 2000000},
                {"WETH": 1000, "USDC": 2000000}
            ]},
            "expected": True
        },
        {
            "name": "Trade during statistical anomaly (very stable pool)",
            "trade_amount": 5,
            "pool": {"WETH": 900, "USDC": 1800000},  # 10% drop in stable pool
            "history": {"reserves": [
                {"WETH": 1000, "USDC": 2000000},
                {"WETH": 1000, "USDC": 2000000},
                {"WETH": 1000, "USDC": 2000000},
                {"WETH": 1000, "USDC": 2000000},
                {"WETH": 1000, "USDC": 2000000}  # Perfectly stable history
            ]},
            "expected": False  # 10% drop in stable pool is anomalous
        },
        {
            "name": "Trade in volatile pool (normal 8% change)",
            "trade_amount": 5,
            "pool": {"WETH": 920, "USDC": 1840000},  # 8% drop
            "history": {"reserves": [
                {"WETH": 1000, "USDC": 2000000},
                {"WETH": 950, "USDC": 1900000},  # 5% drop
                {"WETH": 980, "USDC": 1960000},  # 3% rise
                {"WETH": 900, "USDC": 1800000},  # 8% drop
                {"WETH": 1000, "USDC": 2000000}  # 11% rise
            ]},
            "expected": True  # 8% change is normal for this volatile pool
        }
    ]
    
    results = []
    for i, test in enumerate(test_cases, 1):
        safe = is_sandwich_safe(test["trade_amount"], test["pool"], test["history"])
        status = "✅ PASS" if safe == test["expected"] else "❌ FAIL"
        results.append((i, test["name"], safe, test["expected"], status))
    
    # Print results
    print("\n📊 Test Results:")
    print("-" * 80)
    for i, name, actual, expected, status in results:
        print(f"{i:2d}. {status} {name}")
        print(f"    Expected: {expected}, Got: {actual}")
        print()
    
    # Summary
    passed = sum(1 for _, _, _, _, status in results if "PASS" in status)
    total = len(results)
    print(f"🎯 Summary: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    return all("PASS" in status for _, _, _, _, status in results)


if __name__ == "__main__":
    # Run comprehensive test suite
    success = analyze_trade_scenarios()
    
    if success:
        print("\n🎉 All tests passed! MEV detector is working correctly.")
        print("\n🛡️  Protection Layers:")
        print("  1. Pool ratio validation (1000-3000 USDC/WETH)")
        print("  2. Trade impact analysis (0.5-1.0% threshold)")
        print("  3. Reserve spike detection (stability-based thresholds)")
        print("  4. Statistical anomaly detection")
    else:
        print("\n⚠️  Some tests failed. Review the detection logic.")
