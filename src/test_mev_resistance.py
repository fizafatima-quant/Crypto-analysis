import pytest
from mev_resistance import is_sandwich_safe

# Existing positive test cases
def test_safe_trade():
    assert is_sandwich_safe(100, {'ETH': 10000, 'USDC': 20000})

def test_unsafe_trade():
    assert not is_sandwich_safe(10000, {'ETH': 10000, 'USDC': 20000})

# New edge case tests
def test_negative_input():
    with pytest.raises(ValueError, match="Trade amount must be positive"):
        is_sandwich_safe(-100, {'ETH': 10000, 'USDC': 20000})

def test_zero_pool_liquidity():
    with pytest.raises(ValueError, match="All reserves must be positive"):
        is_sandwich_safe(100, {'ETH': 0, 'USDC': 20000})

def test_single_token_pool():
    with pytest.raises(ValueError, match="Pool must contain at least 2 tokens"):
        is_sandwich_safe(100, {'ETH': 10000})

def test_non_dict_pool():
    with pytest.raises(ValueError, match="Pool reserves must be a dictionary"):
        is_sandwich_safe(100, "not_a_dictionary")