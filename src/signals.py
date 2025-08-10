import pandas as pd
from typing import Optional, Tuple

def generate_signals(df: pd.DataFrame) -> Optional[Tuple[pd.DataFrame, dict]]:
    """
    Generate trading signals based on indicators.
    
    Args:
        df: DataFrame with indicator columns from indicators.py
    
    Returns:
        Tuple: (DataFrame with signals, statistics dictionary) or None if error
    """
    try:
        print("\n🎯 Generating trading signals...")
        
        # Initialize signals (0=hold, 1=buy, -1=sell)
        df['signal'] = 0
        stats = {'buy': 0, 'sell': 0, 'hold': len(df)}
        
        # 1. RSI Strategy (Overbought/Oversold)
        df.loc[df['rsi'] < 30, 'signal'] = 1   # Buy when oversold
        df.loc[df['rsi'] > 70, 'signal'] = -1  # Sell when overbought
        
        # 2. MACD Crossover
        df.loc[df['macd'] > df['signal'], 'signal'] = 1   # MACD above signal → Buy
        df.loc[df['macd'] < df['signal'], 'signal'] = -1  # MACD below signal → Sell
        
        # 3. Bollinger Band Strategy
        df.loc[df['close'] < df['lower_band'], 'signal'] = 1    # Price below lower band → Buy
        df.loc[df['close'] > df['upper_band'], 'signal'] = -1  # Price above upper band → Sell
        
        # Update statistics
        stats['buy'] = len(df[df['signal'] == 1])
        stats['sell'] = len(df[df['signal'] == -1])
        stats['hold'] = len(df) - stats['buy'] - stats['sell']
        
        print("✅ Signals generated successfully")
        print(f"📊 Signal counts: BUY={stats['buy']}, SELL={stats['sell']}, HOLD={stats['hold']}")
        
        return df, stats
        
    except Exception as e:
        print(f"❌ Error generating signals: {e}")
        return None

# Test function
if __name__ == "__main__":
    from data_fetcher import get_crypto_data
    from indicators import calculate_indicators
    
    print("\n🧪 Testing signal generation...")
    test_data = get_crypto_data(limit=100)
    if test_data is not None:
        test_data = calculate_indicators(test_data)
        if test_data is not None:
            result, stats = generate_signals(test_data)
            if result is not None:
                print("\nSample signals:")
                print(result[['close', 'rsi', 'macd', 'signal']].tail(10))
