def is_sandwich_safe(swap_amount, pool_reserves):
    """
    Determine if a swap is safe from sandwich attacks by checking if the swap amount
    exceeds a threshold percentage of the pool's smaller reserve.
    
    Args:
        swap_amount (float): The amount of token being swapped
        pool_reserves (dict): Dictionary with pool reserves for both tokens (e.g. {'ETH': 1000, 'USDC': 1000})
        
    Returns:
        bool: True if swap is safe (≤1% of pool), False if vulnerable (>1%)
    
    Example:
        >>> is_sandwich_safe(50, {'ETH': 5000, 'USDC': 5000})
        True
        >>> is_sandwich_safe(100, {'ETH': 1000, 'USDC': 1000})
        False
    """
    min_reserve = min(pool_reserves.values())
    swap_percentage = swap_amount / min_reserve
    return swap_percentage <= 0.01  # 1% threshold