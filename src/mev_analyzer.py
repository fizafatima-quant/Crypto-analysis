import numpy as np
from typing import Dict, Optional

def is_sandwich_safe(
    trade_amount: float,
    pool_reserves: Dict[str, float],
    historical_data: Optional[Dict] = None,
    token_pair: Optional[Dict] = None
) -> bool:
    """
    Enhanced MEV detection with multiple protection layers
    
    Args:
        trade_amount: Amount of tokens being traded (in base token units)
        pool_reserves: Current pool reserves {token: amount}
        historical_data: Optional dict containing:
            - reserve_history: List of past reserve states
            - volume_history: List of past trade volumes
            - price_history: List of past prices
        token_pair: Dictionary with {'base': 'WETH', 'quote': 'USDC'} for price calculations
    
    Returns:
        bool: True if trade appears safe from MEV exploitation
    """
    
    # 1. Basic Parameter Validation
    if len(pool_reserves) != 2:
        raise ValueError("Pool must contain exactly 2 tokens")
    
    token_a, token_b = pool_reserves.keys()
    reserve_a, reserve_b = pool_reserves.values()
    
    # 2. Dynamic Imbalance Detection
    imbalance_ratio = max(reserve_a, reserve_b) / min(reserve_a, reserve_b)
    
    # Dynamic threshold based on pool size
    imbalance_threshold = 5 + (0.05 * (reserve_a + reserve_b) / 1e6)  # Scales with TVL
    if imbalance_ratio > imbalance_threshold:
        return False
    
    # 3. Trade Impact Analysis
    min_reserve = min(reserve_a, reserve_b)
    trade_impact = trade_amount / min_reserve
    
    # Adaptive threshold based on volatility
    max_impact = 0.005  # Base 0.5% threshold
    if historical_data and 'price_history' in historical_data:
        volatility = np.std(historical_data['price_history'])
        max_impact = max(0.001, 0.005 - (volatility * 0.1))  # Reduce threshold in volatile markets
    
    if trade_impact > max_impact:
        return False
    
    # 4. Historical Pattern Detection
    if historical_data:
        # Check for recent large reserve changes
        if 'reserve_history' in historical_data and len(historical_data['reserve_history']) > 2:
            last_change = abs(reserve_a - historical_data['reserve_history'][-1][token_a])
            avg_change = np.mean([abs(x[token_a] - y[token_a]) 
                               for x, y in zip(historical_data['reserve_history'][:-1], 
                                             historical_data['reserve_history'][1:])])
            
            if last_change > 3 * avg_change:
                return False
        
        # Check volume anomalies
        if 'volume_history' in historical_data:
            avg_volume = np.mean(historical_data['volume_history'])
            if trade_amount > 5 * avg_volume:
                return False
    
    # 5. Price Slippage Projection
    if token_pair and historical_data and 'price_history' in historical_data:
        current_price = reserve_b / reserve_a if token_pair['base'] == token_a else reserve_a / reserve_b
        expected_price = np.mean(historical_data['price_history'][-5:])  # 5-period moving average
        
        if abs(current_price - expected_price) / expected_price > 0.02:  # 2% deviation
            return False
    
    # 6. Liquidity Provider Protection
    if historical_data and 'reserve_history' in historical_data:
        # Check if reserves are being drained systematically
        reserve_trend = np.polyfit(
            range(len(historical_data['reserve_history'])),
            [r[token_a] for r in historical_data['reserve_history']],
            1
        )[0]  # Slope of reserve change
        
        if reserve_trend < -0.1 * reserve_a:  # More than 10% downward trend
            return False
    
    return True

# Example usage
if __name__ == "__main__":
    # Example data
    pool = {'WETH': 1000, 'USDC': 2000000}
    history = {
        'reserve_history': [{'WETH': 950, 'USDC': 1900000}, {'WETH': 980, 'USDC': 1960000}],
        'volume_history': [50000, 55000],
        'price_history': [1950, 1975]
    }
    pair = {'base': 'WETH', 'quote': 'USDC'}
    
    # Test with different trade amounts
    for amount in [5, 10, 20]:
        safe = is_sandwich_safe(amount, pool, history, pair)
        print(f"Trade of {amount} WETH is safe: {safe}")