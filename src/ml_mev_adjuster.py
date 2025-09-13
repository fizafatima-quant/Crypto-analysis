# ml_mev_adjuster.py
from typing import List
import numpy as np

class AdaptiveMEVThreshold:
    def __init__(self, initial_threshold: float = 0.005):
        self.threshold = initial_threshold
        self.past_trades: List[float] = []

    def update_threshold(self, trade_amount: float, was_mev: bool):
        """Adjust threshold based on recent trade patterns"""
        self.past_trades.append(trade_amount)
        if len(self.past_trades) > 100:
            self.past_trades.pop(0)

        avg_trade = np.mean(self.past_trades) if self.past_trades else 0
        if was_mev and trade_amount > avg_trade:
            self.threshold *= 0.9  # tighten
        elif not was_mev and trade_amount < avg_trade:
            self.threshold *= 1.1  # loosen slightly

    def get_threshold(self) -> float:
        return min(max(self.threshold, 0.001), 0.1)
