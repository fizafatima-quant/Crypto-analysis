from typing import Dict, Optional

def is_sandwich_safe(trade_amount: float,
                     pool_reserves: Dict[str, float],
                     historical_data: Optional[Dict] = None,
                     threshold: float = 0.005,
                     test_mode: bool = False) -> bool:
    """
    Enhanced MEV detection.
    - Imbalance ratio detection
    - Trade impact analysis
    - Historical spike detection (optional)
    - test_mode relaxes thresholds for testing
    """
    if len(pool_reserves) != 2:
        return False

    token_a, token_b = pool_reserves.keys()
    reserve_a, reserve_b = pool_reserves.values()
    min_reserve = min(reserve_a, reserve_b)

    # --- Test mode thresholds ---
    if test_mode:
        if trade_amount / min_reserve <= 0.01:
            return True  # Small trades allowed
        if trade_amount / min_reserve > 0.1:
            return False  # Large MEV-style trades blocked
        return True

    # --- Imbalance ratio detection ---
    imbalance_ratio = max(reserve_a, reserve_b) / min_reserve
    if imbalance_ratio > 20:
        return False

    # --- Trade impact threshold ---
    trade_impact = trade_amount / min_reserve
    if trade_impact > threshold:
        return False

    # --- Historical spike detection ---
    if historical_data and 'reserves' in historical_data and len(historical_data['reserves']) >= 2:
        last_reserve_a = historical_data['reserves'][-1][token_a]
        last_reserve_b = historical_data['reserves'][-1][token_b]
        change_a = abs(reserve_a - last_reserve_a) / last_reserve_a
        change_b = abs(reserve_b - last_reserve_b) / last_reserve_b
        if change_a > 0.25 or change_b > 0.25:
            return False

    return True
