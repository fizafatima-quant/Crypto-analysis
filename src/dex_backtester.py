from amm import AMM
import math

class DexBacktester:
    def __init__(self):
        self.pools = {}  # pool_id -> AMM instance
        self.lp_tokens = {}  # pool_id -> total supply
        self.lp_positions = {}  # user -> {pool_id: amount}

    def add_liquidity(self, user: str, token_a: str, token_b: str, amount_a: float, amount_b: float):
        pool_id = f"{token_a}-{token_b}"
        
        if pool_id not in self.pools:
            # Initialize new pool
            self.pools[pool_id] = AMM({token_a: amount_a, token_b: amount_b})
            self.lp_tokens[pool_id] = math.sqrt(amount_a * amount_b)
        else:
            # Add to existing pool
            pool = self.pools[pool_id]
            ratio = amount_a / pool.reserves[token_a]
            if not math.isclose(amount_b / pool.reserves[token_b], ratio, rel_tol=1e-6):
                raise ValueError("Imbalanced liquidity provision")
            
            pool.reserves[token_a] += amount_a
            pool.reserves[token_b] += amount_b
            self.lp_tokens[pool_id] += ratio * self.lp_tokens[pool_id]

        # Track user's position
        if user not in self.lp_positions:
            self.lp_positions[user] = {}
        self.lp_positions[user][pool_id] = self.lp_positions[user].get(pool_id, 0) + self.lp_tokens[pool_id]