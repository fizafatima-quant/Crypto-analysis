import numpy as np 
from dataclasses import dataclass, field
from typing import Dict, Tuple
import math
from fork_detector import ForkDetector

@dataclass
class LPToken:
    """Tracks LP positions and pool state"""
    pair: str                  # e.g. "ETH-USDC"
    address: str               # Pool address
    reserves: Tuple[float, float]  # (reserve0, reserve1)
    total_supply: float = 0    # Total LP tokens minted
    fee_accumulated: float = 0 # Collected fees in token0

class AMM:
    def __init__(self, fee: float = 0.003, gas_fee: float = 0.0001):
        self.fee = fee          # 0.3% LP fee
        self.gas_fee = gas_fee  # 0.01% network fee
        self.pools: Dict[str, LPToken] = {}

    def execute_swap(self, token_in: str, token_out: str, amount_in: float) -> Tuple[float, LPToken]:
        """Execute swap with atomic reserve updates"""
        pair_name = f"{token_in}-{token_out}"
        if pair_name not in self.pools:
            raise ValueError(f"Pool {pair_name} not found")

        lp_token = self.pools[pair_name]
        reserve_in, reserve_out = lp_token.reserves

        # Calculate output with 0.3% fee
        amount_in_with_fee = amount_in * (1 - self.fee)
        amount_out = (amount_in_with_fee * reserve_out) / (reserve_in + amount_in_with_fee)

        # Update reserves and track fees
        lp_token.reserves = (
            reserve_in + amount_in,
            reserve_out - amount_out
        )
        lp_token.fee_accumulated += amount_in * self.fee

        # Apply gas fee
        return amount_out * (1 - self.gas_fee), lp_token

    def add_liquidity(self, token0: str, token1: str, amount0: float, amount1: float) -> LPToken:
        """Add liquidity with proper LP token minting"""
        pair_name = f"{token0}-{token1}"

        if pair_name not in self.pools:
            # Initial LP tokens = sqrt(amount0 * amount1)
            initial_supply = math.sqrt(amount0 * amount1)
            self.pools[pair_name] = LPToken(
                pair=pair_name,
                address=f"0x{pair_name[:8]}",
                reserves=(amount0, amount1),
                total_supply=initial_supply
            )
            return self.pools[pair_name]

        # Calculate LP tokens based on share
        reserve0, reserve1 = self.pools[pair_name].reserves
        lp_amount = min(
            amount0 / reserve0,
            amount1 / reserve1
        ) * self.pools[pair_name].total_supply

        # Update reserves
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
        self.user_balances: Dict[str, Dict[str, float]] = {}  # user -> {token: amount}
        self.user_lp_positions: Dict[str, Dict[str, float]] = {}  # user -> {pool: lp_tokens}

    def safe_swap(self, user: str, token_in: str, token_out: str, amount_in: float) -> float:
        """Secure swap with fork detection"""
        # 1. Check balances
        if self.user_balances.get(user, {}).get(token_in, 0) < amount_in:
            raise ValueError(f"Insufficient {token_in} balance")

        # 2. Check for forks
        pool_address = self.amm.pools[f"{token_in}-{token_out}"].address
        if self.fork_detector.is_vampire_fork(pool_address):
            raise ValueError(f"Security Alert: {token_in}-{token_out} pool is a fork")

        # 3. Execute swap
        amount_out, updated_pool = self.amm.execute_swap(token_in, token_out, amount_in)

        # 4. Update balances
        if user not in self.user_balances:
            self.user_balances[user] = {}
        self.user_balances[user][token_in] = self.user_balances[user].get(token_in, 0) - amount_in
        self.user_balances[user][token_out] = self.user_balances[user].get(token_out, 0) + amount_out

        print(f"✅ {user} swapped {amount_in} {token_in} → {amount_out:.2f} {token_out}")
        print(f"   New reserves: {updated_pool.reserves}")
        return amount_out

    def provide_liquidity(self, user: str, token0: str, token1: str, amount0: float, amount1: float):
        """Add liquidity with full LP tracking"""
        # 1. Check balances
        if self.user_balances.get(user, {}).get(token0, 0) < amount0 or \
           self.user_balances.get(user, {}).get(token1, 0) < amount1:
            raise ValueError("Insufficient token balance")

        # 2. Add liquidity
        lp_token = self.amm.add_liquidity(token0, token1, amount0, amount1)

        # 3. Update user balances
        if user not in self.user_balances:
            self.user_balances[user] = {}
        self.user_balances[user][token0] -= amount0
        self.user_balances[user][token1] -= amount1

        # 4. Track LP tokens
        if user not in self.user_lp_positions:
            self.user_lp_positions[user] = {}
        lp_amount = math.sqrt(amount0 * amount1) if lp_token.total_supply == 0 else \
                   min(amount0/lp_token.reserves[0], amount1/lp_token.reserves[1]) * lp_token.total_supply
        self.user_lp_positions[user][lp_token.pair] = self.user_lp_positions[user].get(lp_token.pair, 0) + lp_amount

        print(f"💰 {user} added {amount0} {token0} + {amount1} {token1}")
        print(f"   Received {lp_amount:.2f} {lp_token.pair} LP tokens")

if __name__ == "__main__":
    # Initialize backtester
    dex = DEXBacktester()
    
    # Setup test user
    dex.user_balances["alice"] = {"ETH": 100, "USDC": 50000}
    
    print("===== DEX Backtester =====")
    
    # 1. Create pool
    print("\n[1] Creating ETH-USDC pool")
    dex.provide_liquidity("alice", "ETH", "USDC", 10, 20000)
    
    # 2. Execute safe swap
    print("\n[2] Alice swaps ETH for USDC")
    try:
        dex.safe_swap("alice", "ETH", "USDC", 1)
    except ValueError as e:
        print(f"🚨 {e}")
    
    # 3. Show final state
    print("\n[Final State]")
    print("Alice balances:", {k: round(v, 2) for k, v in dex.user_balances["alice"].items() if v > 0})
    print("Alice LP positions:", {k: round(v, 2) for k, v in dex.user_lp_positions["alice"].items()})
    print("ETH-USDC pool reserves:", dex.amm.pools["ETH-USDC"].reserves)