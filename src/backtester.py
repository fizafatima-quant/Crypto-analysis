import numpy as np 
from typing import Dict, Tuple
from dataclasses import dataclass
import math
from fork_detector import ForkDetector

@dataclass
class LPToken:
    """Represents a liquidity provider token"""
    token_pair: str          # e.g. "ETH-USDC"
    pool_address: str        # Mock address
    total_supply: float = 0  # Total LP tokens minted

class AMM:
    def __init__(self, fee: float = 0.003):
        self.fee = fee
        self.lp_tokens: Dict[str, LPToken] = {}
        self.pools = {
            'ETH': {'USDC': (1000.0, 2_000_000.0)},
            'USDC': {'ETH': (2_000_000.0, 1000.0)}
        }

    def add_liquidity(self, token_a: str, token_b: str, amount_a: float, amount_b: float) -> Tuple[LPToken, float]:
        """Add liquidity to pool"""
        pool_id = f"{token_a}-{token_b}"
        
        if pool_id not in self.lp_tokens:
            lp_amount = math.sqrt(amount_a * amount_b)
            self.lp_tokens[pool_id] = LPToken(
                token_pair=pool_id,
                pool_address=f"0x{pool_id[:8].lower()}",
                total_supply=lp_amount
            )
            return self.lp_tokens[pool_id], lp_amount
        
        reserve_a, reserve_b = self.pools[token_a][token_b]
        total_lp = self.lp_tokens[pool_id].total_supply
        lp_amount = min((amount_a/reserve_a), (amount_b/reserve_b)) * total_lp
        self.lp_tokens[pool_id].total_supply += lp_amount
        return self.lp_tokens[pool_id], lp_amount

    def remove_liquidity(self, token_pair: str, lp_amount: float) -> Tuple[float, float]:
        """Remove liquidity from pool"""
        if token_pair not in self.lp_tokens:
            raise ValueError("Pool does not exist")
            
        lp_token = self.lp_tokens[token_pair]
        if lp_amount > lp_token.total_supply:
            raise ValueError("Insufficient LP tokens")
        
        token_a, token_b = token_pair.split('-')
        reserve_a, reserve_b = self.pools[token_a][token_b]
        
        share = lp_amount / lp_token.total_supply
        amount_a = reserve_a * share
        amount_b = reserve_b * share
        
        lp_token.total_supply -= lp_amount
        return amount_a, amount_b

    def execute_swap(self, token_in: str, token_out: str, amount_in: float) -> Tuple[float, float]:
        """Execute a token swap"""
        reserve_in, reserve_out = self.pools[token_in][token_out]
        amount_out = (amount_in * 0.997 * reserve_out) / (reserve_in + amount_in * 0.997)
        
        # Update reserves
        self.pools[token_in][token_out] = (reserve_in + amount_in, reserve_out - amount_out)
        self.pools[token_out][token_in] = (reserve_out - amount_out, reserve_in + amount_in)
        
        return amount_out, (reserve_out/reserve_in)  # Return amount and price

class DEXBacktester:
    def __init__(self):
        self.amm = AMM()
        self.fork_detector = ForkDetector()
        self.user_lp_balances: Dict[str, float] = {}

    def safe_swap(self, token_in: str, token_out: str, amount_in: float) -> Tuple[float, float]:
        """Safe swap with fork detection"""
        pool_id = f"{token_in}-{token_out}"
        if pool_id not in self.amm.lp_tokens:
            raise ValueError("Pool does not exist")
            
        if self.fork_detector.detect_fork(self.amm.lp_tokens[pool_id].pool_address):
            raise ValueError("Cannot trade on forked pool")
            
        return self.amm.execute_swap(token_in, token_out, amount_in)

    def provide_liquidity(self, token_a: str, token_b: str, amount_a: float, amount_b: float):
        """Add liquidity to pool"""
        # Verify ratio is within 1% of pool ratio
        pool_ratio = self.amm.pools[token_a][token_b][0] / self.amm.pools[token_a][token_b][1]
        input_ratio = amount_a / amount_b
        if abs(input_ratio - pool_ratio) / pool_ratio > 0.01:
            raise ValueError(f"Must maintain pool ratio (~{pool_ratio:.2f})")
        
        # Update reserves
        self.amm.pools[token_a][token_b] = (
            self.amm.pools[token_a][token_b][0] + amount_a,
            self.amm.pools[token_a][token_b][1] + amount_b
        )
        
        # Mint LP tokens
        lp_token, lp_amount = self.amm.add_liquidity(token_a, token_b, amount_a, amount_b)
        self.user_lp_balances[lp_token.token_pair] = self.user_lp_balances.get(lp_token.token_pair, 0) + lp_amount
        
        print(f"Added liquidity: {amount_a} {token_a} + {amount_b} {token_b}")
        print(f"Received {lp_amount:.2f} {lp_token.token_pair} LP tokens")

    def remove_liquidity(self, token_pair: str, lp_amount: float):
        """Remove liquidity from pool"""
        if lp_amount > self.user_lp_balances.get(token_pair, 0):
            raise ValueError("Insufficient LP tokens")
        
        amount_a, amount_b = self.amm.remove_liquidity(token_pair, lp_amount)
        self.user_lp_balances[token_pair] -= lp_amount
        
        print(f"Withdrew {amount_a:.2f} {token_a} and {amount_b:.2f} {token_b}")

if __name__ == "__main__":
    dex = DEXBacktester()
    
    # Test 1: Add liquidity
    print("=== Adding Liquidity ===")
    dex.provide_liquidity("ETH", "USDC", 10.0, 20000.0)
    
    # Test 2: Safe swap
    print("\n=== Safe Swap ===")
    try:
        amount, price = dex.safe_swap("ETH", "USDC", 1.0)
        print(f"Swapped 1 ETH → {amount:.2f} USDC @ {price:.2f}")
    except ValueError as e:
        print("Swap blocked:", e)
    
    # Test 3: Remove liquidity
    print("\n=== Removing Liquidity ===")
    dex.remove_liquidity("ETH-USDC", 5.0)