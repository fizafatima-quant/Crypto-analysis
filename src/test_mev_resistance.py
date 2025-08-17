from mev_resistance import is_sandwich_safe

def test_mev_resistance():
    # Test small safe swap
    assert is_sandwich_safe(5, {'ETH': 1000, 'USDC': 1000}) == True
    
    # Test dangerous large swap (from your task)
    assert is_sandwich_safe(100, {'ETH': 1000, 'USDC': 1000}) == False
    
    # Test exactly at threshold
    assert is_sandwich_safe(10, {'ETH': 1000, 'USDC': 1000}) == True
    
    # Test uneven pools
    assert is_sandwich_safe(5, {'ETH': 100, 'USDC': 1000}) == False
    
    print("All tests passed!")

test_mev_resistance()