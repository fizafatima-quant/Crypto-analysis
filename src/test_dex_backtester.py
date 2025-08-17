import pytest
from dex_backtester import LiquidityPool, DexBacktester
from mev_resistance import is_sandwich_safe

@pytest.fixture
def test_pool():
    """Pool with 100 ETH and 200,000 USDC (1:2000 price)"""
    return LiquidityPool({'ETH': 100.0, 'USDC': 200000.0})

@pytest.fixture
def test_backtester(test_pool):
    return DexBacktester(test_pool)

def test_blocks_mev_trades(test_backtester, monkeypatch):
    """Test MEV-risky trades are blocked"""
    monkeypatch.setattr('mev_resistance.is_sandwich_safe', lambda *args: False)
    amount_out, price = test_backtester.execute_swap('ETH', 50.0)  # 50% of pool
    assert amount_out == 0.0
    assert price == 0.0

def test_allows_safe_trades(test_backtester, monkeypatch):
    """Test safe trades execute normally"""
    monkeypatch.setattr('mev_resistance.is_sandwich_safe', lambda *args: True)
    amount_out, price = test_backtester.execute_swap('ETH', 0.01)  # 0.01% of pool
    assert amount_out > 0
    assert price > 0

def test_invalid_swaps(test_backtester):
    """Test invalid amounts are handled"""
    amount_out, price = test_backtester.execute_swap('ETH', -1.0)
    assert amount_out == 0.0
    assert price == 0.0
    
    amount_out, price = test_backtester.execute_swap('ETH', 0.0)
    assert amount_out == 0.0
    assert price == 0.0

def test_pool_state_after_swap(test_backtester, monkeypatch):
    """Test reserves update correctly after swap"""
    pool = test_backtester.pool
    initial_eth = pool.reserves['ETH']
    initial_usdc = pool.reserves['USDC']
    initial_k = pool.k
    
    # Bypass MEV check
    monkeypatch.setattr('mev_resistance.is_sandwich_safe', lambda *args: True)
    
    # Tiny swap (0.001 ETH)
    swap_amount = 0.001
    amount_out, _ = test_backtester.execute_swap('ETH', swap_amount)
    
    # Verify
    assert pool.reserves['ETH'] == pytest.approx(initial_eth + swap_amount)
    assert pool.reserves['USDC'] == pytest.approx(initial_k / (initial_eth + swap_amount))
    assert pool.k == pytest.approx(initial_k)  # Constant product maintained
    assert amount_out == pytest.approx(initial_usdc - pool.reserves['USDC'])