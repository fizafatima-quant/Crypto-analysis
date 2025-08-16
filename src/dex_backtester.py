# src/dex_backtester.py
from fork_detector import get_recent_forks
from typing import List, Dict, Optional
import pandas as pd
import numpy as np  # Added missing import
from datetime import datetime
import matplotlib.pyplot as plt

class DexBacktester:
    def __init__(self, min_tvl: float = 1_000_000):
        """
        Initialize backtester with minimum TVL threshold.
        
        Args:
            min_tvl (float): Minimum TVL in USD to consider a fork (default: $1M)
        """
        self.min_tvl = min_tvl
        self.active_forks: List[Dict] = []
        self.historical_data = pd.DataFrame()
        self.last_updated: Optional[datetime] = None

    def refresh_forks(self) -> List[Dict]:
        """
        Fetch latest forks from DeFiLlama and update active_forks.
        Returns list of forks with TVL > min_tvl.
        """
        self.active_forks = get_recent_forks(min_tvl=self.min_tvl)
        self.last_updated = datetime.now()
        
        if not self.active_forks:
            print("Warning: No forks found matching criteria")
        return self.active_forks

    def analyze_tvl_growth(self, days: int = 30) -> pd.DataFrame:
        """
        Simulate TVL growth analysis with realistic random walk model.
        
        Args:
            days (int): Number of days to simulate (default: 30)
        
        Returns:
            pd.DataFrame: Analysis results with growth metrics
        """
        if not self.active_forks:
            self.refresh_forks()
            
        results = []
        for fork in self.active_forks:
            # More realistic simulation with volatility clustering
            daily_returns = [0]
            current_tvl = fork["tvl"]
            
            for _ in range(1, days):
                # Random walk with momentum effect
                prev_return = daily_returns[-1]
                new_return = prev_return * 0.7 + np.random.normal(0, 0.05)
                daily_returns.append(new_return)
            
            # Calculate metrics
            simulated_tvl = [current_tvl * (1 + r) for r in daily_returns]
            peak_tvl = max(simulated_tvl)
            drawdown = (peak_tvl - simulated_tvl[-1]) / peak_tvl
            
            results.append({
                "name": fork["name"],
                "start_tvl": current_tvl,
                "end_tvl": simulated_tvl[-1],
                "growth_pct": (simulated_tvl[-1] - current_tvl) / current_tvl * 100,
                "max_drawdown": drawdown * 100,
                "volatility": np.std(daily_returns) * 100
            })
        
        self.historical_data = pd.DataFrame(results)
        return self.historical_data

    def visualize_growth(self, top_n: int = 10):
        """
        Plot TVL growth for top forks by current TVL.
        
        Args:
            top_n (int): Number of top forks to visualize
        """
        if self.historical_data.empty:
            self.analyze_tvl_growth()
            
        top_forks = self.historical_data.nlargest(top_n, "start_tvl")
        plt.figure(figsize=(12, 6))
        plt.barh(top_forks["name"], top_forks["growth_pct"])
        plt.xlabel("Growth Percentage (%)")
        plt.title(f"Top {top_n} Forks by TVL Growth (Last 30 Days)")
        plt.tight_layout()
        plt.savefig("tvl_growth.png")
        plt.close()

    def save_results(self, filename: str = "backtest_results.csv"):
        """Save analysis results to CSV with timestamp metadata."""
        if not self.historical_data.empty:
            self.historical_data.to_csv(filename, index=False)
            print(f"Results saved to {filename} (Updated: {self.last_updated})")

if __name__ == "__main__":
    # Example usage
    backtester = DexBacktester(min_tvl=5_000_000)  # $5M threshold
    backtester.refresh_forks()
    backtester.analyze_tvl_growth()
    backtester.visualize_growth()
    backtester.save_results()