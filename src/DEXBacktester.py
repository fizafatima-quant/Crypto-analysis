# DEXBacktester.py
import math
from dataclasses import dataclass
from typing import Dict, Tuple
from fork_detector import ForkDetector
from ml_mev_adjuster import AdaptiveMEVThreshold
from analytics import PerformanceMonitor

@dataclass
class LPToken:
    pair: str
    address: str
    reserves: Tuple[float, float]
    total_supply: float = 0
    fee_accumulated: float = 0

class AMM:
    def __init__(self, fee: float = 0.003, gas_fee: float = 0.0001):
        self.fee = fee
        self.gas_fee = gas_fee
        self.pools: Dict[str, LPToken] = {}

    def execute_swap(self, token_in: str, token_out: str, amount_in: float) -> Tuple[float, LPToken]:
        pair_name = f"{token_in}-{token_out}"
        if pair_name not in self.pools:
            raise ValueError(f"Pool {pair_name} not found")

        lp_token = self.pools[pair_name]
        reserve_in, reserve_out = lp_token.reserves
        amount_in_with_fee = amount_in * (1 - self.fee)
        amount_out = (amount_in_with_fee * reserve_out) / (reserve_in + amount_in_with_fee)
        lp_token.reserves = (reserve_in + amount_in, reserve_out - amount_out)
        lp_token.fee_accumulated += amount_in * self.fee
        return amount_out * (1 - self.gas_fee), lp_token

    def add_liquidity(self, token0: str, token1: str, amount0: float, amount1: float) -> LPToken:
        pair_name = f"{token0}-{token1}"
        if pair_name not in self.pools:
            initial_supply = math.sqrt(amount0 * amount1)
            self.pools[pair_name] = LPToken(pair_name, f"0x{pair_name[:8]}", (amount0, amount1), initial_supply)
            return self.pools[pair_name]
        reserve0, reserve1 = self.pools[pair_name].reserves
        lp_amount = min(amount0 / reserve0, amount1 / reserve1) * self.pools[pair_name].total_supply
        self.pools[pair_name].reserves = (reserve0 + amount0, reserve1 + amount1)
        self.pools[pair_name].total_supply += lp_amount
        return self.pools[pair_name]

    def get_price(self, token: str) -> float:
        # Simple price approximation: reserve1/reserve0
        for pool in self.pools.values():
            if token in pool.pair:
                r0, r1 = pool.reserves
                return r1 / r0
        return 0.0

    def pool_reset(self):
        # For demo: do nothing
        pass

class DEXBacktester:
    def __init__(self):
        self.amm = AMM()
        self.user_balances: Dict[str, Dict[str, float]] = {}
        self.user_lp_positions: Dict[str, Dict[str, float]] = {}
        self.monitor = PerformanceMonitor()
        self.mev_adjuster = AdaptiveMEVThreshold()
        self.fork_detector = ForkDetector()

    def safe_swap(self, user: str, token_in: str, token_out: str, amount_in: float) -> float:
        if self.user_balances.get(user, {}).get(token_in, 0) < amount_in:
            raise ValueError(f"Insufficient {token_in} balance")

        threshold = self.mev_adjuster.get_threshold()
        price_before = self.amm.get_price(token_in)
        amount_out, updated_pool = self.amm.execute_swap(token_in, token_out, amount_in)
        price_after = self.amm.get_price(token_in)
        slippage = abs(price_after - price_before) / price_before

        if slippage > threshold:
            self.mev_adjuster.update_threshold(amount_in, was_mev=True)
            self.monitor.log_swap(amount_in, status='mev_blocked')
            self.amm.pool_reset()
            raise ValueError(f"MEV blocked! Slippage {slippage*100:.2f}% > adaptive threshold {threshold*100:.2f}%")
        else:
            self.mev_adjuster.update_threshold(amount_in, was_mev=False)
            self.monitor.log_swap(amount_in, status='success')
            self.user_balances[user][token_in] -= amount_in
            self.user_balances[user][token_out] = self.user_balances[user].get(token_out, 0) + amount_out

        return amount_out

    def provide_liquidity(self, user: str, token0: str, token1: str, amount0: float, amount1: float):
        if self.user_balances.get(user, {}).get(token0, 0) < amount0 or \
           self.user_balances.get(user, {}).get(token1, 0) < amount1:
            raise ValueError("Insufficient token balance")

        lp_token = self.amm.add_liquidity(token0, token1, amount0, amount1)
        self.user_balances[user][token0] -= amount0
        self.user_balances[user][token1] -= amount1
        lp_amount = math.sqrt(amount0 * amount1) if lp_token.total_supply == 0 else \
                    min(amount0/lp_token.reserves[0], amount1/lp_token.reserves[1]) * lp_token.total_supply
        if user not in self.user_lp_positions:
            self.user_lp_positions[user] = {}
        self.user_lp_positions[user][lp_token.pair] = self.user_lp_positions[user].get(lp_token.pair, 0) + lp_amount
        print(f"💰 {user} added {amount0} {token0} + {amount1} {token1}")
        print(f"   Received {lp_amount:.2f} {lp_token.pair} LP tokens")
