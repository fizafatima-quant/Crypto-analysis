import numpy as np 
from dataclasses import dataclass
from typing import Dict, Tuple
import math
from fork_detector import ForkDetector
from config import SLIPPAGE_TOLERANCE
from analytics import PerformanceMonitor  # Added for analytics

@dataclass
class LPToken:
    """Tracks LP positions and pool state"""
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

    def execute_swap(self, token_in: str, token_out: str, amount_in: float, max_slippage: float = None) -> Tuple[float, LPToken]:
        pair_name = f"{token_in}-{token_out}"
        if pair_name not in self.pools:
            raise ValueError(f"Pool {pair_name} not found")

        lp_token = self.pools[pair_name]
        reserve_in, reserve_out = lp_token.reserves

        price_before = reserve_out / reserve_in

        amount_in_with_fee = amount_in * (1 - self.fee)
        amount_out = (amount_in_with_fee * reserve_out) / (reserve_in + amount_in_with_fee)

        # Update reserves
        lp_token.reserves = (
            reserve_in + amount_in,
            reserve_out - amount_out
        )
        lp_token.fee_accumulated += amount_in * self.fee

        amount_out_net = amount_out * (1 - self.gas_fee)

        # Slippage protection
        if max_slippage is not None:
            price_after = lp_token.reserves[1] / lp_token.reserves[0]
            slippage = abs(price_after - price_before) / price_before
            if slippage > max_slippage:
                lp_token.reserves = (reserve_in, reserve_out)
                print(f"🚨 Swap reverted! Slippage {slippage:.2%} > max {max_slippage:.2%}")
                return 0.0, lp_token

        return amount_out_net, lp_token

    def add_liquidity(self, token0: str, token1: str, amount0: float, amount1: float) -> LPToken:
        pair_name = f"{token0}-{token1}"
        if pair_name not in self.pools:
            initial_supply = math.sqrt(amount0 * amount1)
            self.pools[pair_name] = LPToken(
                pair=pair_name,
                address=f"0x{pair_name[:8]}",
                reserves=(amount0, amount1),
                total_supply=initial_supply
            )
            return self.pools[pair_name]

        reserve0, reserve1 = self.pools[pair_name].reserves
        lp_amount = min(amount0 / reserve0, amount1 / reserve1) * self.pools[pair_name].total_supply
        self.pools[pair_name].reserves = (
            reserve0 + amount0,
            reserve1 + amount1
        )
        self.pools[pair_name].total_supply += lp_amount
        return self.pools[pair_name]

class DEXBacktester:
    def __init__(self):
        self.amm = AMM()
        self.fork_detector = ForkDetector()
        self.monitor = PerformanceMonitor()  # Analytics monitor
        self.user_balances: Dict[str, Dict[str, float]] = {}
        self.user_lp_positions: Dict[str, Dict[str, float]] = {}

    def safe_swap(self, user: str, token_in: str, token_out: str, amount_in: float, max_slippage: float = None) -> float:
        if max_slippage is None:
            max_slippage = SLIPPAGE_TOLERANCE

        if self.user_balances.get(user, {}).get(token_in, 0) < amount_in:
            raise ValueError(f"Insufficient {token_in} balance")

        pool_address = self.amm.pools[f"{token_in}-{token_out}"].address
        if self.fork_detector.is_vampire_fork(pool_address):
            self.monitor.log_swap(amount_in, status='mev_blocked')
            raise ValueError(f"Security Alert: {token_in}-{token_out} pool is a fork")

        amount_out, updated_pool = self.amm.execute_swap(token_in, token_out, amount_in, max_slippage)

        if amount_out > 0:
            self.user_balances[user][token_in] -= amount_in
            self.user_balances[user][token_out] = self.user_balances[user].get(token_out, 0) + amount_out
            self.monitor.log_swap(amount_in, status='success')
            print(f"✅ {user} swapped {amount_in} {token_in} → {amount_out:.2f} {token_out}")
            print(f"   New reserves: {updated_pool.reserves}")
        else:
            self.monitor.log_swap(amount_in, status='slippage_revert')

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
        self.user_lp_positions.setdefault(user, {})
        self.user_lp_positions[user][lp_token.pair] = self.user_lp_positions[user].get(lp_token.pair, 0) + lp_amount

        print(f"💰 {user} added {amount0} {token0} + {amount1} {token1}")
        print(f"   Received {lp_amount:.2f} {lp_token.pair} LP tokens")

if __name__ == "__main__":
    dex = DEXBacktester()
    dex.user_balances["alice"] = {"ETH": 100, "USDC": 50000}

    print("===== DEX Backtester =====")

    print("\n[1] Creating ETH-USDC pool")
    dex.provide_liquidity("alice", "ETH", "USDC", 10, 20000)

    print("\n[2] Alice swaps ETH for USDC")
    try:
        dex.safe_swap("alice", "ETH", "USDC", 1)
    except ValueError as e:
        print(f"🚨 {e}")

    print("\n[3] High-slippage swap test")
    try:
        dex.safe_swap("alice", "ETH", "USDC", 5, max_slippage=0.005)
    except ValueError as e:
        print(f"🚨 {e}")

    # Performance report
    report = dex.monitor.get_report()
    print("\n[Performance Report]")
    for k, v in report.items():
        print(f"{k}: {v:.2f}")

    print("\n[Final State]")
    print("Alice balances:", {k: round(v, 2) for k, v in dex.user_balances["alice"].items() if v > 0})
    print("Alice LP positions:", {k: round(v, 2) for k, v in dex.user_lp_positions["alice"].items()})
    print("ETH-USDC pool reserves:", dex.amm.pools["ETH-USDC"].reserves)
