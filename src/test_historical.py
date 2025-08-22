from historical_backtester import HistoricalBacktester

# Dummy strategy: buy 1 ETH if price < 2005
def simple_strategy(price, volume):
    if price < 2005:
        return {'amount': 1}
    return None

# Initialize backtester
backtester = HistoricalBacktester("historical_data.csv")

# Run backtest
results = backtester.run_backtest(simple_strategy)

# Print results
for r in results:
    print(r)
