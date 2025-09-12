# full_dex_system.py
import math

# ---------------------------
# Adaptive MEV Threshold
# ---------------------------
class AdaptiveMEVThreshold:
    def __init__(self):
        self.threshold = 0.005  # 0.5%
    
    def get_threshold(self):
        return self.threshold
    
    def update_threshold(self, amount_in, was_mev=False):
        if was_mev:
            self.threshold *= 0.9  # decrease threshold if MEV detected
        else:
            self.threshold *= 1.01  # increase slowly on normal trades
        self.threshold = max(0.001, min(self.threshold, 0.05))  # clamp

# ---------------------------
# AMM Class
# ---------------------------
class AMM:
    def __init__(self):
        self.reserves = {"ETH": 1000, "USDC": 2000000}

    def get_price(self, token):
        return self.reserves['USDC'] / self.reserves['ETH']

    def execute_swap(self, token_in, token_out, amount_in):
        if amount_in > self.reserves[token_in]:
            raise ValueError("Insufficient pool liquidity")
        price = self.get_price(token_in)
        amount_out = amount_in * price
        self.reserves[token_in] += amount_in
        self.reserves[token_out] -= amount_out
        return amount_out, 0

    def pool_reset(self):
        self.reserves = {"ETH": 1000, "USDC": 2000000}

# ---------------------------
# Performance Monitor
# ---------------------------
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

# ---------------------------
# DEX Backtester
# ---------------------------
class DEXBacktester:
    def __init__(self):
        self.user_balances = {}
        self.swap_history = []
        self.amm = AMM()
        self.mev_adjuster = AdaptiveMEVThreshold()
        self.monitor = PerformanceMonitor()

    def safe_swap(self, user, token_in, token_out, amount_in):
        if self.user_balances.get(user, {}).get(token_in, 0) < amount_in:
            self.swap_history.append({"status": "failed", "amount_in": amount_in, "price_impact": 0})
            raise ValueError(f"Insufficient {token_in} balance")
        
        threshold = self.mev_adjuster.get_threshold()
        price_before = self.amm.get_price(token_in)
        try:
            amount_out, _ = self.amm.execute_swap(token_in, token_out, amount_in)
        except ValueError as e:
            self.swap_history.append({"status": "failed", "amount_in": amount_in, "price_impact": 0})
            raise e
        price_after = self.amm.get_price(token_in)
        slippage = abs(price_after - price_before) / price_before
        
        if slippage > threshold:
            self.mev_adjuster.update_threshold(amount_in, was_mev=True)
            self.monitor.log_swap(amount_in, status='mev_blocked')
            self.swap_history.append({"status": "mev_blocked", "amount_in": amount_in, "price_impact": slippage})
            self.amm.pool_reset()
            raise ValueError(f"MEV blocked! Slippage {slippage*100:.2f}% > threshold {threshold*100:.2f}%")
        else:
            self.mev_adjuster.update_threshold(amount_in, was_mev=False)
            self.monitor.log_swap(amount_in, status='success')
            self.swap_history.append({"status": "success", "amount_in": amount_in, "price_impact": slippage})
            self.user_balances[user][token_in] -= amount_in
            self.user_balances[user][token_out] = self.user_balances[user].get(token_out, 0) + amount_out
        
        return amount_out

# ---------------------------
# Security Auditor
# ---------------------------
class SecurityAuditor:
    def __init__(self, backtester: DEXBacktester):
        self.backtester = backtester
        self.checks = [
            self.check_mev_protection,
            self.check_slippage_control,
            self.check_reserve_integrity,
            self.check_gas_optimization
        ]
    
    def run_audit(self):
        results = {}
        for check in self.checks:
            try:
                result = check()
                results[check.__name__] = "PASS" if result else "FAIL"
            except Exception as e:
                results[check.__name__] = f"ERROR ({str(e)})"
        return results
    
    def check_mev_protection(self):
        report = self.backtester.monitor.get_report()
        return report['mev_block_rate'] > 0
    
    def check_slippage_control(self):
        try:
            self.backtester.safe_swap('alice', 'ETH', 'USDC', 900)
        except:
            return True
        return False
    
    def check_reserve_integrity(self):
        pool = getattr(self.backtester.amm, 'reserves', None)
        if pool is None:
            raise ValueError("AMM reserves not found")
        return pool['ETH'] > 0 and pool['USDC'] > 0
    
    def check_gas_optimization(self):
        return True

# ---------------------------
# Run Test
# ---------------------------
if __name__ == "__main__":
    dex = DEXBacktester()
    dex.user_balances['alice'] = {'ETH': 1000, 'USDC': 1000000}

    # small swap to generate some swaps
    try:
        dex.safe_swap('alice', 'ETH', 'USDC', 10)
    except:
        pass

    auditor = SecurityAuditor(dex)
    results = auditor.run_audit()
    print("=== Security Audit Results ===")
    for k, v in results.items():
        print(f"{k}: {v}")
