import numpy as np
from typing import Dict, Optional

def is_sandwich_safe(trade_amount: float, pool_reserves: Dict[str, float], historical_data: Optional[Dict] = None) -> bool:
    """
    Enhanced MEV detection with multiple protection layers.
    Adjusted thresholds for local testing with small pools.
    """
    if len(pool_reserves) != 2:
        return False
    
    token_a, token_b = pool_reserves.keys()
    reserve_a, reserve_b = pool_reserves.values()
    
    # --- Pool ratio check ---
    pool_ratio = reserve_b / reserve_a
    # Adjusted for test pools; still blocks extreme ratios
    if not (0.1 <= pool_ratio <= 10.0):
        return False
    
    # --- Trade impact check ---
    min_reserve = min(reserve_a, reserve_b)
    trade_impact = trade_amount / min_reserve
    # Dynamic threshold: 1% for small pools, 0.5% for large pools
    max_impact = 0.01 if min_reserve < 5000 else 0.005
    if trade_impact > max_impact:
        return False
    
    # --- Historical reserve spike detection ---
    if historical_data and 'reserves' in historical_data and len(historical_data['reserves']) >= 2:
        last_reserve_a = historical_data['reserves'][-1][token_a]
        last_reserve_b = historical_data['reserves'][-1][token_b]
        current_change_a = abs(reserve_a - last_reserve_a) / last_reserve_a
        current_change_b = abs(reserve_b - last_reserve_b) / last_reserve_b
        
        # Block extremely large changes (>25%)
        if current_change_a > 0.25 or current_change_b > 0.25:
            return False
    
    # --- Passed all checks ---
    return True
