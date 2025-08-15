import numpy as np 
from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional
import math
import requests
from fork_detector import ForkDetector

@dataclass
class LPToken:
    """Tracks LP positions and pool state"""
    pair: str
    address: str
    reserves: Tuple[float, float]
    total_supply: float = 0
    fee_accumulated: float = 0

class AMM:
    def __init__(self, fee: float = 0.003):
        self.fee = fee
        self.pools: Dict[str, LPToken] = {}

    def add_liquidity(self, token0: str, token1: str, amount0: float, amount1: float) -> LPToken:
        """Add liquidity to pool"""
        pair_name = f"{token0}-{token1}"
        
        if pair_name not in self.pools:
            initial_supply = math.sqrt(amount0 * amount1)
            self.pools[pair_name] = LPToken(
                pair=pair_name,
                address=f"0x{pair_name[:8].lower()}",
                reserves=(amount0, amount1),
                total_supply=initial_supply
            )
            return self.pools[pair_name]
        
        reserve0, reserve1 = self.pools[pair_name].reserves
        lp_amount = min(
            (amount0 / reserve0),
            (amount1 / reserve1)
        ) * self.pools[pair_name].total_supply
        
        self.pools[pair_name].reserves = (
            reserve0 + amount0,
            reserve1 + amount1
        )
        self.pools[pair_name].total_supply += lp_amount
        return self.pools[pair_name]

    def execute_swap(self, token_in: str, token_out: str, amount_in: float) -> Tuple[float, LPToken]:
        """Execute swap with full state updates"""
        pair_name = f"{token_in}-{token_out}"
        if pair_name not in self.pools:
            raise ValueError("Pool does not exist")
            
        lp_token = self.pools[pair_name]
        reserve_in, reserve_out = lp_token.reserves
        
        amount_in_with_fee = amount_in * (1 - self.fee)
        amount_out = (amount_in_with_fee * reserve_out) / (reserve_in + amount_in_with_fee)
        
        # Update reserves and accumulate fees
        lp_token.reserves = (
            reserve_in + amount_in,
            reserve_out - amount_out
        )
        lp_token.fee_accumulated += amount_in * self.fee
        
        # Recalculate LP token value
        if lp_token.total_supply > 0:
            k_old = reserve_in * reserve_out
            k_new = lp_token.reserves[0] * lp_token.reserves[1]
            if k_new > k_old:
                lp_token.total_supply *= math.sqrt(k_new / k_old)
        
        return amount_out, lp_token

class DEXBacktester:
    def __init__(self):
        self.amm = AMM()
        self.fork_detector = ForkDetector()
        self.user_balances: Dict[str, Dict[str, float]] = {}

    def safe_swap(self, user: str, token_in: str, token_out: str, amount_in: float) -> float:
        """Secure swap with fork detection"""
        # Verify user balance
        if self.user_balances.get(user, {}).get(token_in, 0) < amount_in:
            raise ValueError("Insufficient balance")
        
        # Check for forks
        pool_address = self.amm.pools[f"{token_in}-{token_out}"].address
        if self.fork_detector.is_vampire_fork(pool_address):
            raise ValueError(f"Security Alert: {token_in}-{token_out} pool is a fork")
        
        # Execute swap
        amount_out, updated_pool = self.amm.execute_swap(token_in, token_out, amount_in)
        
        # Update balances
        if user not in self.user_balances:
            self.user_balances[user] = {}
        self.user_balances[user][token_in] = self.user_balances[user].get(token_in, 0) - amount_in
        self.user_balances[user][token_out] = self.user_balances[user].get(token_out, 0) + amount_out
        
        print(f"✅ Safe swap executed: {amount_in} {token_in} → {amount_out:.6f} {token_out}")
        print(f"Pool reserves: {updated_pool.reserves}")
        print(f"Fees accumulated: {updated_pool.fee_accumulated:.6f} {token_in}")
        return amount_out

    def provide_liquidity(self, user: str, token0: str, token1: str, amount0: float, amount1: float):
        """Add liquidity with balance checks"""
        if self.user_balances.get(user, {}).get(token0, 0) < amount0 or \
           self.user_balances.get(user, {}).get(token1, 0) < amount1:
            raise ValueError("Insufficient token balance")
        
        lp_token = self.amm.add_liquidity(token0, token1, amount0, amount1)
        
        # Update balances
        if user not in self.user_balances:
            self.user_balances[user] = {}
        self.user_balances[user][token0] -= amount0
        self.user_balances[user][token1] -= amount1
        
        print(f"💰 {user} added {amount0} {token0} + {amount1} {token1}")
        print(f"Received LP tokens for {lp_token.pair} (Total Supply: {lp_token.total_supply:.2f})")

if __name__ == "__main__":
    dex = DEXBacktester()
    
    # Initialize test environment
    dex.user_balances["alice"] = {"ETH": 100, "USDC": 50000}
    
    print("===== DEX Backtester with Fork Detection =====")
    
    # 1. Create genuine pool
    print("\n[1] Creating ETH-USDC pool")
    dex.amm.add_liquidity("ETH", "USDC", 1000, 2000000)
    
    # 2. Safe swap
    print("\n[2] Alice swaps safely")
    try:
        dex.safe_swap("alice", "ETH", "USDC", 10)
    except ValueError as e:
        print(f"🚨 {e}")
    
    # 3. Simulate fork scenario
    print("\n[3] Simulating fork detection")
    dex.amm.pools["ETH-USDC"].address = "0x123fork"  # Mock fork address
    try:
        dex.safe_swap("alice", "ETH", "USDC", 5)
    except ValueError as e:
        print(f"🚨 {e}")
    
    print("\n=== Final State ===")
    print("Alice balances:", {k: v for k, v in dex.user_balances["alice"].items() if v > 0})