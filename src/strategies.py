import pandas as pd

def moving_average_crossover(data: pd.DataFrame) -> pd.Series:
    """Simple moving average crossover strategy"""
    close = data['close'] if 'close' in data.columns else data['Close']
    signals = pd.Series(0, index=data.index)
    short_ma = close.rolling(10).mean()
    long_ma = close.rolling(50).mean()
    signals[short_ma > long_ma] = 1   # Buy signal
    signals[short_ma <= long_ma] = -1 # Sell signal
    return signals