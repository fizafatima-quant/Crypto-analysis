from mev_resistance import is_sandwich_safe
from typing import Dict, Tuple, List
import logging
import matplotlib.pyplot as plt
import sys

logging.basicConfig(level=logging.INFO)

class LiquidityPool:
    def __init__(self, reserves: Dict[str, float]):
        self.reserves = reserves.copy()
        self.initial_reserves = reserves.copy()
        self._validate_reserves()
        self.k = self.reserves[list(self.reserves.keys())[0]] * self.reserves[list(self.reserves.keys())[1]]
        
    def _validate_reserves(self):
        """Validate pool reserves on initialization"""
        if len(self.reserves) != 2:
            raise ValueError("Pool must contain exactly 2 tokens")
        if any(v <= 0 for v in self.reserves.values()):
            raise ValueError("Pool reserves must be positive")

    def get_price(self, token_in: str, token_out: str) -> float:
        """Get current price with validation"""
        if token_in not in self.reserves or token_out not in self.reserves:
            raise ValueError("Invalid token pair")
        return self.reserves[token_out] / self.reserves[token_in]
        
    def swap(self, token_in: str, amount_in: float) -> float:
        """Execute swap with validation and precise calculations"""
        if amount_in <= 0:
            raise ValueError("Swap amount must be positive")
            
        token_out = [t for t in self.reserves.keys() if t != token_in][0]
        new_reserve_in = self.reserves[token_in] + amount_in
        amount_out = self.reserves[token_out] - (self.k / new_reserve_in)
        
        if amount_out <= 0:
            raise ValueError("Insufficient liquidity")
            
        # Update reserves
        self.reserves[token_in] = new_reserve_in
        self.reserves[token_out] = self.k / new_reserve_in
        
        return amount_out

    def reset(self):
        """Reset pool to initial state"""
        self.reserves = self.initial_reserves.copy()
        self.k = self.reserves[list(self.reserves.keys())[0]] * self.reserves[list(self.reserves.keys())[1]]

class DexBacktester:
    def __init__(self, pool: LiquidityPool):
        self.pool = pool
        self.swap_history = []
        
    def _get_pair_token(self, token_in: str) -> str:
        """Get the other token in the pair with validation"""
        pair = [t for t in self.pool.reserves.keys() if t != token_in]
        if not pair:
            raise ValueError(f"No pair found for token {token_in}")
        return pair[0]
        
    def _log_failed_swap(self, token_in: str, amount_in: float, reason: str):
        """Record failed swaps with price snapshots"""
        try:
            token_out = self._get_pair_token(token_in)
            price = self.pool.get_price(token_in, token_out)
            self.swap_history.append({
                'token_in': token_in,
                'amount_in': amount_in,
                'amount_out': 0.0,
                'price_before': price,
                'price_after': price,
                'price_impact': 0.0,
                'status': 'failed',
                'reason': reason
            })
        except Exception as e:
            logging.error(f"Failed to log failed swap: {str(e)}")

    def execute_swap(self, token_in: str, amount_in: float) -> Tuple[float, float]:
        """Production-ready swap execution with MEV protection"""
        try:
            # Input validation
            if amount_in <= 0:
                raise ValueError(f"Invalid swap amount: {amount_in}")
                
            token_out = self._get_pair_token(token_in)
            price_before = self.pool.get_price(token_in, token_out)
            
            # MEV protection check
            if not is_sandwich_safe(amount_in, self.pool.initial_reserves):
                warning_msg = (
                    f"MEV RISK: Blocked {amount_in:.6f} {token_in} "
                    f"(>{0.5}% of initial reserves)"
                )
                logging.warning(warning_msg)
                self._log_failed_swap(token_in, amount_in, warning_msg)
                return 0.0, price_before
                
            # Execute safe swap
            amount_out = self.pool.swap(token_in, amount_in)
            price_after = self.pool.get_price(token_in, token_out)
            
            self.swap_history.append({
                'token_in': token_in,
                'amount_in': amount_in,
                'amount_out': amount_out,
                'price_before': price_before,
                'price_after': price_after,
                'price_impact': (price_after - price_before) / price_before,
                'status': 'success',
                'reason': None
            })
            
            return amount_out, price_after
            
        except ValueError as e:
            error_msg = f"Swap validation failed: {str(e)}"
            logging.error(error_msg)
            self._log_failed_swap(token_in, amount_in, error_msg)
            return 0.0, 0.0
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logging.critical(error_msg)
            self._log_failed_swap(token_in, amount_in, error_msg)
            return 0.0, 0.0       

    def get_stats(self) -> Dict:
        """Returns comprehensive trading statistics"""
        stats = {
            'total_swaps': 0,
            'successful_swaps': 0,
            'failed_swaps': 0,
            'total_volume': 0.0,
            'executed_volume': 0.0,
            'total_output': 0.0,
            'avg_price_impact': 0.0,
            'avg_successful_swap_size': 0.0,
            'current_pool_reserves': self.pool.reserves.copy()
        }
        
        if not self.swap_history:
            return stats
            
        successful_swaps = [s for s in self.swap_history if s['status'] == 'success']
        stats['total_swaps'] = len(self.swap_history)
        stats['successful_swaps'] = len(successful_swaps)
        stats['failed_swaps'] = len(self.swap_history) - len(successful_swaps)
        stats['total_volume'] = sum(s['amount_in'] for s in self.swap_history)
        stats['executed_volume'] = sum(s['amount_in'] for s in successful_swaps)
        
        if successful_swaps:
            stats['total_output'] = sum(s['amount_out'] for s in successful_swaps)
            stats['avg_price_impact'] = sum(s['price_impact'] for s in successful_swaps) / len(successful_swaps)
            stats['avg_successful_swap_size'] = stats['executed_volume'] / len(successful_swaps)
            
        return stats
    
    def visualize_swaps(self, save_path: str = None):
        """Enhanced visualization with optional saving"""
        if not self.swap_history:
            print("No swaps to visualize")
            return
            
        successful_swaps = [s for s in self.swap_history if s['status'] == 'success']
        if not successful_swaps:
            print("No successful swaps to visualize")
            return
            
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Price impact plot
        indices = [i for i, s in enumerate(self.swap_history) if s['status'] == 'success']
        impacts = [s['price_impact']*100 for s in successful_swaps]
        ax1.plot(indices, impacts, 'bo-')
        ax1.set_xlabel('Swap Index')
        ax1.set_ylabel('Price Impact (%)')
        ax1.set_title('Price Impact Over Swaps')
        ax1.grid(True)
        
        # Pool reserves plot
        eth_reserves = []
        usdc_reserves = []
        for swap in self.swap_history:
            if 'ETH' in self.pool.reserves:
                eth_reserves.append(self.pool.reserves['ETH'])
            if 'USDC' in self.pool.reserves:
                usdc_reserves.append(self.pool.reserves['USDC'])
                
        if eth_reserves:
            ax2.plot(eth_reserves, label='ETH Reserve')
        if usdc_reserves:
            ax2.plot(usdc_reserves, label='USDC Reserve')
        ax2.set_xlabel('Swap Sequence')
        ax2.set_ylabel('Amount')
        ax2.set_title('Pool Reserves Change')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()

    def reset(self):
        """Full reset of backtester state"""
        self.pool.reset()
        self.swap_history = []

if __name__ == "__main__":
    try:
        # Initialize pool
        pool = LiquidityPool({'ETH': 1000.0, 'USDC': 1000.0})
        backtester = DexBacktester(pool)
        
        print("=== Starting Simulation ===")
        print(f"Initial pool reserves: {pool.initial_reserves}")
        
        # Test cases
        test_swaps = [
            ('ETH', 1.0),    # Small safe swap
            ('ETH', 100.0),  # Large MEV-risk swap
            ('ETH', 5.0),    # Exactly 0.5% threshold
            ('ETH', 4.99),   # Just below threshold
            ('ETH', 5.01)    # Just above threshold
        ]
        
        for i, (token, amount) in enumerate(test_swaps, 1):
            print(f"\nSwap {i}: {amount} {token}")
            amount_out, price = backtester.execute_swap(token, amount)
            if amount_out > 0:
                print(f"Executed: Received {amount_out:.6f} USDC at price {price:.6f}")
            else:
                print("Blocked: MEV risk")
        
        # Print final stats
        stats = backtester.get_stats()
        print("\n=== Simulation Results ===")
        print(f"Total swaps attempted: {stats['total_swaps']}")
        print(f"Successful swaps: {stats['successful_swaps']}")
        print(f"Blocked swaps: {stats['failed_swaps']}")
        print(f"Total volume: {stats['total_volume']:.2f}")
        print(f"Executed volume: {stats['executed_volume']:.2f}")
        print(f"Average price impact: {stats['avg_price_impact']*100:.4f}%")
        print("\nFinal pool reserves:", stats['current_pool_reserves'])
        
        # Visualize
        backtester.visualize_swaps()
        
    except Exception as e:
        logging.error(f"Simulation failed: {str(e)}")
        sys.exit(1)