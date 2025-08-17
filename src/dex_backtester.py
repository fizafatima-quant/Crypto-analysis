from mev_resistance import is_sandwich_safe
from typing import Dict, Tuple, List
import logging
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO)

class LiquidityPool:
    def __init__(self, reserves: Dict[str, float]):
        self.reserves = reserves.copy()
        self.initial_reserves = reserves.copy()  # Store initial reserves
        self.k = reserves[list(reserves.keys())[0]] * reserves[list(reserves.keys())[1]]  # Constant product
        
    def get_price(self, token_in: str, token_out: str) -> float:
        return self.reserves[token_out] / self.reserves[token_in]
        
    def swap(self, token_in: str, amount_in: float) -> float:
        token_out = [t for t in self.reserves.keys() if t != token_in][0]
        self.reserves[token_in] += amount_in
        amount_out = self.reserves[token_out] - (self.k / self.reserves[token_in])
        self.reserves[token_out] = self.k / self.reserves[token_in]
        return amount_out

    def reset(self):
        self.reserves = self.initial_reserves.copy()
        self.k = self.reserves[list(self.reserves.keys())[0]] * self.reserves[list(self.reserves.keys())[1]]

class DexBacktester:
    def __init__(self, pool: LiquidityPool):
        self.pool = pool
        self.swap_history = []
        
    def execute_swap(self, token_in: str, amount_in: float) -> Tuple[float, float]:
        """Execute a swap with MEV protection"""
        token_out = [t for t in self.pool.reserves.keys() if t != token_in][0]
        price_before = self.pool.get_price(token_in, token_out)
        
        # Check against INITIAL pool reserves for MEV risk
        if not is_sandwich_safe(amount_in, self.pool.initial_reserves):
            logging.warning(f"MEV risk detected! Swap {amount_in} too large for initial pool {self.pool.initial_reserves}")
            
            self.swap_history.append({
                'token_in': token_in,
                'amount_in': amount_in,
                'amount_out': 0.0,
                'price_before': price_before,
                'price_after': price_before,
                'price_impact': 0.0,
                'status': 'failed',
                'reason': 'MEV risk'
            })
            return 0.0, price_before
            
        amount_out = self.pool.swap(token_in, amount_in)
        price_after = self.pool.get_price(token_in, token_out)
        price_impact = (price_after - price_before) / price_before
        
        self.swap_history.append({
            'token_in': token_in,
            'amount_in': amount_in,
            'amount_out': amount_out,
            'price_before': price_before,
            'price_after': price_after,
            'price_impact': price_impact,
            'status': 'success',
            'reason': None
        })
        
        return amount_out, price_after
        
    def get_stats(self) -> Dict:
        """Returns trading statistics"""
        if not self.swap_history:
            return {}
            
        successful_swaps = [s for s in self.swap_history if s['status'] == 'success']
        
        stats = {
            'total_swaps': len(self.swap_history),
            'successful_swaps': len(successful_swaps),
            'failed_swaps': len(self.swap_history) - len(successful_swaps),
            'total_volume': sum(s['amount_in'] for s in self.swap_history),
            'executed_volume': sum(s['amount_in'] for s in successful_swaps),
            'current_pool_reserves': self.pool.reserves.copy()
        }
        
        if successful_swaps:
            stats['avg_price_impact'] = sum(s['price_impact'] for s in successful_swaps) / len(successful_swaps)
            stats['avg_successful_swap_size'] = sum(s['amount_in'] for s in successful_swaps) / len(successful_swaps)
            stats['total_output'] = sum(s['amount_out'] for s in successful_swaps)
        else:
            stats['avg_price_impact'] = 0
            stats['avg_successful_swap_size'] = 0
            stats['total_output'] = 0
            
        return stats
    
    def visualize_swaps(self):
        """Plots price impact over swap sequence"""
        if not self.swap_history:
            print("No swaps to visualize")
            return
            
        successful_indices = [i for i, s in enumerate(self.swap_history) if s['status'] == 'success']
        price_impacts = [self.swap_history[i]['price_impact'] for i in successful_indices]
        
        plt.figure(figsize=(10, 5))
        plt.plot(successful_indices, price_impacts, 'bo-')
        plt.xlabel('Successful Swap Index')
        plt.ylabel('Price Impact')
        plt.title('Price Impact Over Successful Swaps')
        plt.grid(True)
        plt.show()

    def reset(self):
        """Reset the backtester state"""
        self.pool.reset()
        self.swap_history = []

if __name__ == "__main__":
    # Initialize pool with 1000 ETH and 1000 USDC
    pool = LiquidityPool({'ETH': 1000.0, 'USDC': 1000.0})
    backtester = DexBacktester(pool)
    
    print("Starting pool reserves:", pool.initial_reserves)
    
    # Test safe swap (1 ETH)
    amount_out, price = backtester.execute_swap('ETH', 1.0)
    print(f"1. Swap 1 ETH -> Received {amount_out:.6f} USDC at price {price:.6f}")
    
    # Test dangerous swap (100 ETH - should trigger MEV warning)
    amount_out, price = backtester.execute_swap('ETH', 100.0)
    print(f"2. Swap 100 ETH -> Blocked (MEV risk)")
    
    # Test threshold swap (10 ETH - exactly 1% of initial pool)
    amount_out, price = backtester.execute_swap('ETH', 10.0)
    print(f"3. Swap 10 ETH -> Received {amount_out:.6f} USDC at price {price:.6f}")
    
    # Print stats
    stats = backtester.get_stats()
    print("\nFinal Statistics:")
    for k, v in stats.items():
        if k != 'current_pool_reserves':
            print(f"{k.replace('_', ' ').title()}: {v}")
    
    print("\nFinal Pool Reserves:", stats['current_pool_reserves'])
    
    # Visualize
    backtester.visualize_swaps()