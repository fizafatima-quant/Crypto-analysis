def is_sandwich_safe(trade_amount: float, pool_reserves: dict, threshold: float = 0.005) -> bool:
    """
    MEV protection with precise threshold handling.
    Now uses <= for threshold comparison to match test expectations.
    """
    # Input validation
    if not isinstance(pool_reserves, dict) or len(pool_reserves) != 2:
        raise ValueError("Pool must contain exactly 2 tokens")
    if any(v <= 0 for v in pool_reserves.values()):
        raise ValueError("All reserves must be positive")
    if trade_amount <= 0:
        raise ValueError("Trade amount must be positive")

    # Calculate minimum reserve with floating-point safety
    min_reserve = min(pool_reserves.values())
    trade_percentage = trade_amount / min_reserve
    
    # Changed to <= to allow exact threshold matches
    return trade_percentage <= threshold