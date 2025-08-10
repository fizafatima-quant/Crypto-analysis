import pandas as pd
import talib
from typing import Optional

def calculate_indicators(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Calculate technical indicators for cryptocurrency data.
    
    Args:
        df: DataFrame with columns ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    
    Returns:
        DataFrame with added indicator columns or None if error occurs
    """
    try:
        print("\n🔮 Calculating indicators...")
        
        # 1. Relative Strength Index (RSI)
        df['rsi'] = talib.RSI(df['close'], timeperiod=14)
        print("✓ RSI (14-period) added")
        
        # 2. Moving Average Convergence Divergence (MACD)
        df['macd'], df['signal'], _ = talib.MACD(
            df['close'], 
            fastperiod=12, 
            slowperiod=26, 
            signalperiod=9
        )
        print("✓ MACD (12,26,9) added")
        
        # 3. Bollinger Bands
        df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(
            df['close'],
            timeperiod=20,
            nbdevup=2,
            nbdevdn=2
        )
        print("✓ Bollinger Bands (20,2) added")
        
        # 4. Simple Moving Average
        df['sma_50'] = talib.SMA(df['close'], timeperiod=50)
        print("✓ 50-day SMA added")
        
        print("✅ All indicators calculated successfully")
        return df
        
    except Exception as e:
        print(f"❌ Error calculating indicators: {e}")
        return None

# Test function
if __name__ == "__main__":
    from data_fetcher import get_crypto_data
    
    print("\n🧪 Testing indicators...")
    test_data = get_crypto_data(limit=30)  # Small sample for testing
    if test_data is not None:
        result = calculate_indicators(test_data)
        if result is not None:
            print("\nSample data with indicators:")
            print(result[['close', 'rsi', 'macd', 'upper_band']].tail())
