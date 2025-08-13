# main.py
import pandas as pd
import logging
from backtester import Backtester
from strategies import moving_average_crossover
from reporting import generate_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting backtest...")
        
        # 1. Load data
        data = pd.read_csv("data.csv")
        logger.info(f"Data loaded successfully. Shape: {data.shape}")
        
        # 2. Initialize backtester
        backtester = Backtester(
            data=data,
            strategy=moving_average_crossover,
            stop_loss=0.05,
            take_profit=0.10
        )
        
        # 3. Run backtest
        results = backtester.run_backtest()
        logger.info("Backtest completed successfully")
        
        # 4. Generate reports
        if generate_report(results):
            logger.info("Reports generated successfully")
        else:
            logger.warning("Report generation completed with warnings")
            
        # 5. Print summary
        print("\n=== Backtest Results ===")
        for k, v in results['metrics'].items():
            print(f"{k:>20}: {v}")
            
    except Exception as e:
        logger.error(f"Backtest failed: {str(e)}", exc_info=True)
        return

if __name__ == "__main__":
    main()