# src/dex_backtester.py
import os
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional
import matplotlib.pyplot as plt

class DexBacktester:
    def __init__(self, min_tvl: float = 1_000_000):
        self.min_tvl = min_tvl
        self.active_forks = []
        self.known_forks = []
        self.historical_data = pd.DataFrame()
        self.last_updated = None
        
        # Proper path handling
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.project_root, 'data')
        os.makedirs(self.data_dir, exist_ok=True)

    def _safe_get(self, data: dict, keys: list, default=None):
        """Safely get nested dictionary values"""
        for key in keys:
            try:
                data = data[key]
            except (KeyError, TypeError):
                return default
        return data

    def refresh_forks(self) -> List[Dict]:
        """Fetch forks with robust error handling"""
        try:
            response = requests.get("https://api.llama.fi/protocols", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            self.active_forks = []
            for protocol in data:
                try:
                    tvl = float(self._safe_get(protocol, ['tvl'], 0))
                    name = str(self._safe_get(protocol, ['name'], '')).lower()
                    
                    if tvl > self.min_tvl and 'uni' in name:
                        self.active_forks.append({
                            'name': protocol.get('name', 'unknown'),
                            'tvl': tvl,
                            'chain': protocol.get('chain', 'unknown')
                        })
                except (TypeError, ValueError) as e:
                    continue
                    
            self.last_updated = datetime.now()
            print(f"✅ Found {len(self.active_forks)} active forks")
            return self.active_forks
            
        except Exception as e:
            print(f"❌ API Error: {str(e)}")
            return []

    def load_known_forks(self) -> List[Dict]:
        """Load historical data with validation"""
        try:
            filepath = os.path.join(self.data_dir, "known_forks.json")
            with open(filepath) as f:
                data = json.load(f)
                
            self.known_forks = []
            for fork in data:
                if isinstance(fork, dict):
                    self.known_forks.append({
                        'name': fork.get('name', 'unknown'),
                        'stolen_tvl': float(fork.get('stolen_tvl', 0)),
                        'parent': fork.get('parent', 'unknown'),
                        'chain': fork.get('chain', 'unknown')
                    })
                    
            print(f"✅ Loaded {len(self.known_forks)} historical forks")
            return self.known_forks
            
        except Exception as e:
            print(f"❌ File Error: {str(e)}")
            return []

    def analyze_tvl_growth(self, days: int = 30) -> pd.DataFrame:
        """Safer growth analysis"""
        if not self.active_forks:
            self.refresh_forks()
            
        results = []
        for fork in self.active_forks:
            try:
                current_tvl = float(fork['tvl'])
                daily_returns = [0]
                
                for _ in range(1, days):
                    prev_return = daily_returns[-1]
                    new_return = prev_return * 0.7 + np.random.normal(0, 0.05)
                    daily_returns.append(new_return)
                
                simulated_tvl = [current_tvl * (1 + r) for r in daily_returns]
                results.append({
                    'name': fork['name'],
                    'start_tvl': current_tvl,
                    'end_tvl': simulated_tvl[-1],
                    'growth_pct': ((simulated_tvl[-1] - current_tvl) / current_tvl) * 100,
                    'chain': fork.get('chain', 'unknown')
                })
                
            except Exception as e:
                print(f"⚠️ Skipping {fork.get('name')}: {str(e)}")
                continue
                
        self.historical_data = pd.DataFrame(results)
        return self.historical_data

    def visualize_results(self):
        """Generate visualizations with error handling"""
        try:
            if self.historical_data.empty:
                self.analyze_tvl_growth()
                
            if not self.historical_data.empty:
                # Basic growth plot
                plt.figure(figsize=(12, 6))
                self.historical_data.sort_values('growth_pct').plot.barh(
                    x='name', 
                    y='growth_pct',
                    title='TVL Growth Simulation'
                )
                plt.tight_layout()
                plt.savefig(os.path.join(self.data_dir, 'growth_comparison.png'))
                plt.close()
                
        except Exception as e:
            print(f"❌ Visualization failed: {str(e)}")

    def save_results(self):
        """Save data with validation"""
        try:
            if not self.historical_data.empty:
                self.historical_data.to_csv(
                    os.path.join(self.data_dir, 'backtest_results.csv'),
                    index=False
                )
                print(f"💾 Saved results to {self.data_dir}")
        except Exception as e:
            print(f"❌ Failed to save results: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting DEX Backtester")
    
    backtester = DexBacktester(min_tvl=1_000_000)
    
    # Load data
    backtester.refresh_forks()
    backtester.load_known_forks()
    
    # Run analysis
    backtester.analyze_tvl_growth(days=30)
    
    # Generate outputs
    backtester.visualize_results()
    backtester.save_results()
    
    print("✅ Analysis completed")