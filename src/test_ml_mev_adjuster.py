import sys, os
sys.path.append(os.path.dirname(__file__))

from ml_mev_adjuster import AdaptiveMEVThreshold

# test_ml_mev_adjuster.py
from ml_mev_adjuster import AdaptiveMEVThreshold

def test_threshold_adjustment():
    adjuster = AdaptiveMEVThreshold(initial_threshold=0.01)

    # Simulate trades with MEV detected
    for _ in range(5):
        adjuster.update_threshold(trade_amount=2000, was_mev=True)
    tightened = adjuster.get_threshold()

    # Simulate safe trades (no MEV)
    for _ in range(5):
        adjuster.update_threshold(trade_amount=100, was_mev=False)
    loosened = adjuster.get_threshold()

    assert tightened < 0.01  # Threshold should tighten after MEV
    assert loosened > tightened  # Should loosen slightly after safe trades
