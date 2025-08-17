def is_sandwich_safe(trade_amount: float, pool_reserves: dict, threshold: float = 0.005) -> bool:
    """
    MEV protection with input validation and threshold checking.
    Returns True if trade is safe from sandwich attacks.
    """
    # Input validation
    if not isinstance(pool_reserves, dict):
        raise ValueError("Pool reserves must be a dictionary")
    if len(pool_reserves) < 2:
        raise ValueError("Pool must contain at least 2 tokens")
    if any(v <= 0 for v in pool_reserves.values()):
        raise ValueError("All reserves must be positive")
    if trade_amount <= 0:
        raise ValueError("Trade amount must be positive")

    # MEV vulnerability check
    min_reserve = min(pool_reserves.values())
    trade_impact = trade_amount / min_reserve
    
    return trade_impact <= threshold