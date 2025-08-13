# backtester.py
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
import logging
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Trade:
    """Class to track individual trades"""
    entry_date: str
    entry_price: float
    exit_date: Optional[str] = None
    exit_price: Optional[float] = None
    position_size: float = 0.0
    fees: float = 0.0
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None

class Backtester:
    def __init__(
        self,
        data: pd.DataFrame,
        strategy: Callable[[pd.DataFrame], pd.Series],
        initial_capital: float = 10000.0,
        fee_rate: float = 0.001,
        price_column: str = "close",
        stop_loss: Optional[float] = 0.05,  # 5%
        take_profit: Optional[float] = 0.10,  # 10%
        position_size: float = 0.1  # 10% of capital
    ) -> None:
        """
        Initialize backtester with:
        - data: DataFrame with price data
        - strategy: Function that generates signals
        - fee_rate: Transaction fee (0.1% default)
        - stop_loss/take_profit: Risk management
        - position_size: % of capital per trade
        """
        self.data = data
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.fee_rate = fee_rate
        self.price_column = price_column
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.position_size = position_size
        self._validate_inputs()

    def _validate_inputs(self) -> None:
        """Validate all inputs"""
        if not isinstance(self.data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame")
        if self.price_column not in self.data.columns:
            raise ValueError(f"Price column '{self.price_column}' not found")
        if not 0 < self.position_size <= 1:
            raise ValueError("Position size must be between 0 and 1")

    def run_backtest(self) -> Dict[str, any]:
        """
        Run backtest and return:
        - performance metrics
        - list of all trades
        - equity curve
        """
        signals = self.strategy(self.data)
        portfolio = self.initial_capital
        position = 0.0
        active_trade = None
        trades = []
        equity_curve = []

        for i, (date, row) in enumerate(self.data.iterrows()):
            price = row[self.price_column]
            
            # Check for stop loss/take profit
            if active_trade and position > 0:
                current_pnl = (price - active_trade.entry_price) / active_trade.entry_price
                if self.stop_loss and current_pnl <= -self.stop_loss:
                    signals.iloc[i] = -1  # Force exit
                elif self.take_profit and current_pnl >= self.take_profit:
                    signals.iloc[i] = -1

            # Buy signal
            if signals.iloc[i] == 1 and position == 0:
                trade_size = portfolio * self.position_size
                fee = trade_size * self.fee_rate
                active_trade = Trade(
                    entry_date=date,
                    entry_price=price,
                    position_size=trade_size,
                    fees=fee
                )
                portfolio -= trade_size + fee
                position = trade_size / price

            # Sell signal
            elif signals.iloc[i] == -1 and position > 0:
                fee = position * price * self.fee_rate
                pnl = position * (price - active_trade.entry_price) - active_trade.fees - fee
                pnl_pct = (pnl / active_trade.position_size) * 100

                active_trade.exit_date = date
                active_trade.exit_price = price
                active_trade.pnl = pnl
                active_trade.pnl_pct = pnl_pct
                active_trade.fees += fee

                trades.append(active_trade)
                portfolio += position * price - fee
                position = 0.0
                active_trade = None

            equity_curve.append(portfolio)

        return {
            'metrics': self._calculate_metrics(equity_curve, trades),
            'trades': trades,
            'equity_curve': equity_curve
        }

    def _calculate_metrics(
        self,
        equity_curve: List[float],
        trades: List[Trade]
    ) -> Dict[str, float]:
        """Calculate performance metrics"""
        total_return = equity_curve[-1] - self.initial_capital
        return_pct = (total_return / self.initial_capital) * 100

        # Win rate
        win_rate = None
        if trades:
            winning_trades = [t for t in trades if t.pnl > 0]
            win_rate = (len(winning_trades) / len(trades)) * 100

        # Drawdown calculation
        equity = pd.Series(equity_curve)
        rolling_max = equity.cummax()
        drawdown = (equity - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100

        return {
            'initial_capital': round(self.initial_capital, 2),
            'final_value': round(equity_curve[-1], 2),
            'total_return': round(total_return, 2),
            'return_pct': round(return_pct, 2),
            'win_rate': round(win_rate, 2) if win_rate else None,
            'max_drawdown': round(max_drawdown, 2),
            'num_trades': len(trades),
            'total_fees': sum(t.fees for t in trades)
        }

    def save_trades(self, trades: List[Trade], filename: str = 'trades.csv') -> None:
        """Save trades to CSV"""
        pd.DataFrame([t.__dict__ for t in trades]).to_csv(filename, index=False)