import math
from ml_mev_adjuster import AdaptiveMEVThreshold
import matplotlib.pyplot as plt

class AMM:
    """Simple AMM with constant product formula"""
    def __init__(self, fee=0.003):
        self.pools = {}
        self.fee = fee

    def add_pool(self, token0, token1, reserve0, reserve1):
        self.pools[f"{token0}-{token1}"] = {"reserves": [reserve0, reserve1]}

    def get_price(self, token_in):
        # Returns price of token_in in terms of the other token
        for pool in self.pools.values():
            r0, r1 = pool["reserves"]
            return r1 / r0
        return 1.0

    def execute_swap(self, token_in, token_out, amount_in):
        pair_name = f"{token_in}-{token_out}"
        if pair_name not in self.pools:
            pair_name = f"{token_out}-{token_in}"
            if pair_name not in self.pools:
                raise ValueError(f"Pool {token_in}-{token_out} not found")

        pool = self.pools[pair_name]
        reserve_in, reserve_out = pool["reserves"]

        amount_in_with_fee = amount_in * (1 - self.fee)
        amount_out = (amount_in_with_fee * reserve_out) / (reserve_in + amount_in_with_fee)

        # Update reserves
        pool["reserves"] = [reserve_in + amount_in, reserve_out - amount_out]
        return amount_out, pool

    def pool_reset(self):
        # Optional: implement reverting logic if needed
        pass


class PerformanceMonitor:
    def __init__(self):
        self.swaps = []

    def log_swap(self, amount_in, status):
        self.swaps.append({"amount_in": amount_in, "status": status})

    def get_report(self):
        total = len(self.swaps)
        if total == 0:
            return {"success_rate": 0, "mev_block_rate": 0, "slippage_revert_rate": 0}
        success = sum(1 for s in self.swaps if s["status"] == "success")
        mev_block = sum(1 for s in self.swaps if s["status"] == "mev_blocked")
        slippage_revert = sum(1 for s in self.swaps if s["status"] == "slippage_reverted")
        return {
            "success_rate": success / total,
            "mev_block_rate": mev_block / total,
            "slippage_revert_rate": slippage_revert / total
        }


class DEXBacktester:
    def __init__(self):
        self.user_balances = {}
        self.user_lp_positions = {}
        self.swap_history = []
        self.amm = AMM()
        self.mev_adjuster = AdaptiveMEVThreshold()
        self.monitor = PerformanceMonitor()

    def provide_liquidity(self, user, token0, token1, amount0, amount1):
        if user not in self.user_balances:
            self.user_balances[user] = {}
        self.user_balances[user][token0] = self.user_balances[user].get(token0, 0) + amount0
        self.user_balances[user][token1] = self.user_balances[user].get(token1, 0) + amount1

        # Send tokens to AMM
        self.amm.add_pool(token0, token1, amount0, amount1)
        self.user_lp_positions[user] = {f"{token0}-{token1}": math.sqrt(amount0 * amount1)}
        print(f"💰 {user} added {amount0} {token0} + {amount1} {token1}")
        print(f"   Received {self.user_lp_positions[user][f'{token0}-{token1}']:.2f} LP tokens")

    def safe_swap(self, user, token_in, token_out, amount_in):
        if self.user_balances.get(user, {}).get(token_in, 0) < amount_in:
            self.swap_history.append({"status": "failed", "amount_in": amount_in, "price_impact": 0})
            raise ValueError(f"Insufficient {token_in} balance")

        threshold = self.mev_adjuster.get_threshold()
        price_before = self.amm.get_price(token_in)
        amount_out, _ = self.amm.execute_swap(token_in, token_out, amount_in)
        price_after = self.amm.get_price(token_in)
        slippage = abs(price_after - price_before) / price_before

        if slippage > threshold:
            self.mev_adjuster.update_threshold(amount_in, was_mev=True)
            self.monitor.log_swap(amount_in, "mev_blocked")
            self.swap_history.append({"status": "mev_blocked", "amount_in": amount_in, "price_impact": slippage})
            self.amm.pool_reset()
            raise ValueError(f"MEV blocked! Slippage {slippage*100:.2f}% > threshold {threshold*100:.2f}%")
        else:
            self.mev_adjuster.update_threshold(amount_in, was_mev=False)
            self.monitor.log_swap(amount_in, "success")
            self.swap_history.append({"status": "success", "amount_in": amount_in, "price_impact": slippage})
            self.user_balances[user][token_in] -= amount_in
            self.user_balances[user][token_out] = self.user_balances[user].get(token_out, 0) + amount_out

        return amount_out
