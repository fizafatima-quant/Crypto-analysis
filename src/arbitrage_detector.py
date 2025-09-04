 
from typing import Dict

class ArbitrageDetector:
    def __init__(self):
        self.known_pools: Dict[str, 'LiquidityPool'] = {}
    
    def add_pool(self, name: str, pool: 'LiquidityPool'):
        self.known_pools[name] = pool
    
    def find_arbitrage_opportunities(self):
        """Find price discrepancies between pools"""
        opportunities = []
        pool_names = list(self.known_pools.keys())
        
        for i in range(len(pool_names)):
            for j in range(i + 1, len(pool_names)):
                pool_a = self.known_pools[pool_names[i]]
                pool_b = self.known_pools[pool_names[j]]
                
                price_a = pool_a.reserves['USDC'] / pool_a.reserves['ETH']
                price_b = pool_b.reserves['USDC'] / pool_b.reserves['ETH']
                
                spread = abs(price_a - price_b) / min(price_a, price_b)
                if spread > 0.01:  # 1% price difference
                    opportunities.append({
                        'pool_a': pool_names[i],
                        'pool_b': pool_names[j],
                        'spread': spread,
                        'profit_opportunity': spread * 1000  # Example calculation
                    })
        
        return opportunities
