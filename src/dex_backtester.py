from typing import Dict, Tuple
import logging
from mev_resistance import is_sandwich_safe
from config import SLIPPAGE_TOLERANCE, GAS_LIMIT, RISK_PARAMS

logging.basicConfig(level=logging.INFO)

class LiquidityPool:
    def __init__(self, reserves: Dict[str, float]):
        self.reserves = reserves.copy()
        self.initial_reserves = reserves.copy()
        self._validate_reserves()
        self.k = self.reserves['ETH'] * self.reserves['USDC']

    def _validate_reserves(self):
        if len(self.reserves) != 2:
            raise ValueError("Pool must contain exactly 2 tokens")
        if any(v <= 0 for v in self.reserves.values()):
            raise ValueError("All reserves must be positive")
        if 'ETH' not in self.reserves or 'USDC' not in self.reserves:
            raise ValueError("Pool must contain ETH and USDC")

    def swap(self, token_in: str, amount_in: float) -> float:
        """
        AMM swap maintaining constant product.
        GAS OPTIMIZATION: Cache reserves to reduce dict reads
        """
        token_out = 'USDC' if token_in == 'ETH' else 'ETH'

        reserve_in = self.reserves[token_in]   # 1 read
        reserve_out = self.reserves[token_out] # 1 read

        new_reserve_in = reserve_in + amount_in
        amount_out = reserve_out - (self.k / new_reserve_in)

        # --- Slippage protection ---
        expected_price = reserve_out / reserve_in
        actual_price = (reserve_out - amount_out) / new_reserve_in
        slippage = abs(actual_price - expected_price) / expected_price
        if slippage > SLIPPAGE_TOLERANCE:
            raise ValueError(f"Swap slippage {slippage:.4f} exceeds tolerance {SLIPPAGE_TOLERANCE}")

        # Update reserves
        self.reserves[token_in] = new_reserve_in
        self.reserves[token_out] = self.k / new_reserve_in

        return amount_out

    def reset(self):
        self.reserves = self.initial_reserves.copy()
        self.k = self.reserves['ETH'] * self.reserves['USDC']


class DexBacktester:
    def __init__(self, pool: LiquidityPool, test_mode: bool = False):
        self.pool = pool
        self.swap_history = []
        self.test_mode = test_mode
        self.gas_used = 0.0

    def execute_swap(self, token_in: str, amount_in: float) -> Tuple[float, float]:
        """
        Executes swap if MEV detection & risk checks pass.
        Returns: (amount_out, price_after)
        """
        try:
            if amount_in <= 0:
                raise ValueError("Invalid swap amount")

            # --- Position sizing (risk parameter) ---
            capital = sum(self.pool.reserves.values())  # proxy for capital
            if amount_in > capital * RISK_PARAMS['max_position_size']:
                raise ValueError("Position size exceeds max risk allocation")

            token_out = 'USDC' if token_in == 'ETH' else 'ETH'
            price_before = self.pool.reserves[token_out] / self.pool.reserves[token_in]

            # --- MEV Protection ---
            if not is_sandwich_safe(amount_in, self.pool.reserves, test_mode=self.test_mode):
                raise ValueError("MEV risk detected")

            # --- Swap execution ---
            amount_out = self.pool.swap(token_in, amount_in)
            price_after = self.pool.reserves[token_out] / self.pool.reserves[token_in]

            # --- Gas cost simulation ---
            self.gas_used += GAS_LIMIT * 0.001  # mock consumption

            self.swap_history.append({
                'token_in': token_in,
                'amount_in': amount_in,
                'amount_out': amount_out,
                'price_before': price_before,
                'price_after': price_after,
                'gas_used': self.gas_used
            })

            return amount_out, price_after

        except ValueError as e:
            logging.warning(f"Blocked swap: {str(e)}")
            return 0.0, 0.0
