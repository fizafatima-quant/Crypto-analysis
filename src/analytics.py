from typing import Dict
import time

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'total_swaps': 0,
            'successful_swaps': 0,
            'mev_blocked': 0,
            'slippage_reverts': 0,
            'total_volume_eth': 0.0,
            'start_time': time.time()
        }
    
    def log_swap(self, amount_eth: float, status: str):
        self.metrics['total_swaps'] += 1
        self.metrics['total_volume_eth'] += amount_eth
        
        if status == 'success':
            self.metrics['successful_swaps'] += 1
        elif status == 'mev_blocked':
            self.metrics['mev_blocked'] += 1
        elif status == 'slippage_revert':
            self.metrics['slippage_reverts'] += 1
    
    def get_report(self) -> Dict:
        total_time = time.time() - self.metrics['start_time']
        return {
            'mev_block_rate': self.metrics['mev_blocked'] / self.metrics['total_swaps'] if self.metrics['total_swaps'] else 0,
            'slippage_revert_rate': self.metrics['slippage_reverts'] / self.metrics['total_swaps'] if self.metrics['total_swaps'] else 0,
            'success_rate': self.metrics['successful_swaps'] / self.metrics['total_swaps'] if self.metrics['total_swaps'] else 0,
            'avg_volume_per_swap': self.metrics['total_volume_eth'] / self.metrics['total_swaps'] if self.metrics['total_swaps'] else 0,
            'swaps_per_second': self.metrics['total_swaps'] / total_time if total_time > 0 else 0
        }
