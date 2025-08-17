from typing import Dict, Tuple
import logging
from mev_resistance import is_sandwich_safe

logging.basicConfig(level=logging.INFO)

class LiquidityPool:
    def __init__(self, reserves: Dict[str, float]):
        self.reserves = reserves.copy()
        self.initial_reserves = reserves.copy()
        self._validate_reserves()
        self.k = self.reserves['ETH'] * self.reserves['USDC']  # Store constant product
        
    def _validate_reserves(self):
        if len(self.reserves) != 2:
            raise ValueError("Pool must contain exactly 2 tokens")
        if any(v <= 0 for v in self.reserves.values()):
            raise ValueError("All reserves must be positive")
        if 'ETH' not in self.reserves or 'USDC' not in self.reserves:
            raise ValueError("Pool must contain ETH and USDC")

    def swap(self, token_in: str, amount_in: float) -> float:
        """Proper AMM swap implementation maintaining constant product"""
        if amount_in <= 0:
            raise ValueError("Swap amount must be positive")
            
        token_out = 'USDC' if token_in == 'ETH' else 'ETH'
        new_reserve_in = self.reserves[token_in] + amount_in
        amount_out = self.reserves[token_out] - (self.k / new_reserve_in)
        
        # Update reserves
        self.reserves[token_in] = new_reserve_in
        self.reserves[token_out] = self.k / new_reserve_in
        
        return amount_out

    def reset(self):
        self.reserves = self.initial_reserves.copy()
        self.k = self.reserves['ETH'] * self.reserves['USDC']

class DexBacktester:
    def __init__(self, pool: LiquidityPool):
        self.pool = pool
        self.swap_history = []
        
    def execute_swap(self, token_in: str, amount_in: float) -> Tuple[float, float]:
        try:
            if amount_in <= 0:
                raise ValueError("Invalid swap amount")
                
            token_out = 'USDC' if token_in == 'ETH' else 'ETH'
            price_before = self.pool.reserves[token_out] / self.pool.reserves[token_in]
            
            if not is_sandwich_safe(amount_in, self.pool.reserves):
                raise ValueError("MEV risk detected")
                
            amount_out = self.pool.swap(token_in, amount_in)
            price_after = self.pool.reserves[token_out] / self.pool.reserves[token_in]
            
            self.swap_history.append({
                'token_in': token_in,
                'amount_in': amount_in,
                'amount_out': amount_out,
                'price_before': price_before,
                'price_after': price_after
            })
            
            return amount_out, price_after
            
        except ValueError as e:
            logging.warning(f"Blocked swap: {str(e)}")
            return 0.0, 0.0