import pytest
from mev_resistance import is_sandwich_safe

def test_normal_operations():
    """Test normal ETH/USDC pool"""
    assert is_sandwich_safe(5, {'ETH': 1000, 'USDC': 1000}) is True      # 0.5% of pool
    assert is_sandwich_safe(5.01, {'ETH': 1000, 'USDC': 1000}) is False  # >0.5%
    assert is_sandwich_safe(4.99, {'ETH': 1000, 'USDC': 1000}) is True   # <0.5%

def test_stablecoin_pools():
    """Test stablecoin pool with large reserves"""
    # 0.5% of 950,000 is 4,750 - so 4,750 should be allowed but 4,751 blocked
    assert is_sandwich_safe(4750, {'USDC': 1_000_000, 'USDT': 950_000}) is True
    assert is_sandwich_safe(4751, {'USDC': 1_000_000, 'USDT': 950_000}) is False
    assert is_sandwich_safe(5000, {'USDC': 1_000_000, 'USDT': 1_000_000}) is True  # 0.5% of 1M

def test_edge_cases():
    """Test edge cases"""
    with pytest.raises(ValueError):
        is_sandwich_safe(0, {'ETH': 1000, 'USDC': 1000})  # Zero amount
    with pytest.raises(ValueError):
        is_sandwich_safe(-1, {'ETH': 1000, 'USDC': 1000})  # Negative amount
    with pytest.raises(ValueError):
        is_sandwich_safe(10, {'ETH': -1000, 'USDC': 1000})  # Negative reserve

if __name__ == "__main__":
    pytest.main(["-v"])