# config.py

# MEV and trade parameters
MEV_THRESHOLD = 0.005          # 0.5% default
MAX_IMBALANCE_RATIO = 20.0     # 20x imbalance limit
SLIPPAGE_TOLERANCE = 0.01      # 1% max slippage
GAS_LIMIT = 300000             # Max gas per swap

# Risk management parameters
RISK_PARAMS = {
    'stop_loss_pct': 0.05,       # 5%
    'take_profit_pct': 0.10,     # 10%
    'max_position_size': 0.2,    # 20% of capital
    'max_daily_loss': 0.1        # 10% daily loss
}
