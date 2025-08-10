import os
import sys
import pandas as pd
import ccxt

def get_crypto_data(symbol='BTC/USDT', timeframe='1d', limit=100):
    """Debug version with verbose output"""
    try:
        print("\n=== Starting Data Fetch ===")
        
        # 1. Verify directory exists
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        print(f"[1/4] Data directory verified: {os.path.abspath(data_dir)}")

        # 2. Initialize API connection
        print("[2/4] Connecting to Binance API...")
        exchange = ccxt.binance({'timeout': 10000})  # 10 second timeout
        print("✓ API connected successfully")

        # 3. Fetch data
        print(f"[3/4] Fetching {limit} {timeframe} candles for {symbol}...")
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        print(f"✓ Received {len(ohlcv)} data points")

        # 4. Process and save data
        print("[4/4] Processing data...")
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        filename = os.path.join(data_dir, f'{symbol.replace("/", "-")}_{timeframe}.csv')
        df.to_csv(filename, index=False)
        print(f"✓ Data saved to:\n{os.path.abspath(filename)}")
        print(df.head(3))  # Show sample data
        
        return df

    except Exception as e:
        print(f"\n⚠️ Critical Error ⚠️\n{str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("\n🚀 Running Crypto Data Fetcher 🚀")
    data = get_crypto_data()
    if data is None:
        print("\n❌ Script failed - see errors above")
    input("\nPress Enter to exit...")