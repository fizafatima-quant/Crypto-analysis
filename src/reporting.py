# reporting.py
import pandas as pd
import matplotlib.pyplot as plt
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_report(results, file_prefix='backtest'):
    """Generate visual and CSV reports"""
    try:
        # 1. Save trades to CSV
        trades_df = pd.DataFrame([t.__dict__ for t in results['trades']])
        trades_csv = f'{file_prefix}_trades.csv'
        trades_df.to_csv(trades_csv, index=False)
        
        # 2. Plot equity curve
        plt.figure(figsize=(12, 6))
        plt.plot(results['equity_curve'], label='Portfolio Value')
        plt.title('Equity Curve')
        plt.xlabel('Time')
        plt.ylabel('Value ($)')
        plt.grid(True)
        equity_png = f'{file_prefix}_equity.png'
        plt.savefig(equity_png)
        plt.close()
        
        logger.info(f"Generated report files:\n- {trades_csv}\n- {equity_png}")
        return True
        
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        return False