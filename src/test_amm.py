import pytest
from amm import AMM
import math

def test_swap_updates_reserves():
    """Test that reserves update correctly after swap"""
    amm = AMM({"USDC": 1000.0, "ETH": 1.0})
    output = amm.execute_swap(100.0, "USDC")
    
    assert amm.reserves["USDC"] == 1100.0
    assert math.isclose(amm.reserves["ETH"], 0.9090909, rel_tol=1e-6)  # More precise expected value

def test_constant_product_invariant():
    """Test that x*y=k remains constant"""
    amm = AMM({"USDC": 1000.0, "ETH": 1.0})
    initial_k = amm.reserves["USDC"] * amm.reserves["ETH"]
    
    # Test multiple swaps
    test_amounts = [100.0, 50.0, 200.0]
    for amount in test_amounts:
        before_k = amm.reserves["USDC"] * amm.reserves["ETH"]
        output = amm.execute_swap(amount, "USDC")
        new_k = amm.reserves["USDC"] * amm.reserves["ETH"]
        assert math.isclose(new_k, initial_k, rel_tol=1e-6), f"Failed at amount {amount}"

def test_liquidity_provision():
    """Test LP token minting"""
    from dex_backtester import DexBacktester

    dex = DexBacktester()
    dex.add_liquidity("Alice", "USDC", "ETH", 1000.0, 1.0)
    
    pool = dex.pools["USDC-ETH"]
    assert math.isclose(pool.reserves["USDC"], 1000.0)
    assert math.isclose(pool.reserves["ETH"], 1.0)
    assert "USDC-ETH" in dex.lp_tokens
    assert "Alice" in dex.lp_positions