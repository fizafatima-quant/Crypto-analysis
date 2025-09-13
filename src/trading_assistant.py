# src/trading_assistant.py

import json
import os
import pandas as pd
from src.data_fetcher import DataFetcher
from dotenv import load_dotenv

# Load environment variables (for future Telegram alerts)
load_dotenv()

# ----------------------------
# Portfolio functions
# ----------------------------
def load_portfolio(filename="src/portfolio.json"):
    """Load portfolio entry prices from JSON"""
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ portfolio.json not found. Using empty portfolio.")
        return {}

def calculate_profit(current_price, entry_price):
    """Calculate profit percentage"""
    if entry_price is None:
        return None
    return ((current_price - entry_price) / entry_price) * 100

def adjust_signal(signal, profit_pct):
    """Adjust SELL signal according to profit rules"""
    if signal == "SELL ❌":
        if profit_pct is not None:
            if profit_pct >= 50:
                return "TAKE PROFIT 💰 (≥50%)"
            elif profit_pct < 0:
                return "HOLD ⏸️ (Avoid selling at loss)"
            else:
                return "HOLD ⏸️ (Waiting for profit target)"
    return signal

# ----------------------------
# Indicator calculation
# ----------------------------
def calculate_indicators(df: pd.DataFrame) -> dict:
    """Calculate simple indicators: MA5, MA20, RSI, MACD"""
    # Moving averages
    df["MA5"] = df["Close"].rolling(5).mean()
    df["MA20"] = df["Close"].rolling(20).mean()
    
    # Simple RSI calculation
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    
    # Simple MACD
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    
    # Signal logic: simple example
    signal = "HOLD ⏸️"
    if df["Close"].iloc[-1] > df["MA5"].iloc[-1]:
        signal = "BUY ✅"
    elif df["Close"].iloc[-1] < df["MA5"].iloc[-1]:
        signal = "SELL ❌"
    
    return {"signal": signal, "MA5": df["MA5"].iloc[-1], "MA20": df["MA20"].iloc[-1],
            "RSI": df["RSI"].iloc[-1], "MACD": df["MACD"].iloc[-1], "MACD_signal": df["MACD_signal"].iloc[-1]}

# ----------------------------
# Coin analysis
# ----------------------------
def analyze_coin(symbol, data, entry_price=None):
    current_price = data["Close"].iloc[-1]

    # Calculate profit %
    profit_pct = calculate_profit(current_price, entry_price)

    # Compute indicators
    indicators = calculate_indicators(data)
    signal = adjust_signal(indicators["signal"], profit_pct)

    # Print analysis
    print(f"\n--- {symbol} Analysis ---")
    print(f"Current Price: {current_price:.2f}")
    if entry_price:
        print(f"Entry Price: {entry_price:.2f}")
        print(f"Profit: {profit_pct:+.2f}%")
    print(f"MA5: {indicators['MA5']:.2f}, MA20: {indicators['MA20']:.2f}")
    print(f"RSI: {indicators['RSI']:.2f}")
    print(f"MACD: {indicators['MACD']:.2f}, MACD_signal: {indicators['MACD_signal']:.2f}")
    print(f"Signal: {signal}")
    print("-------------------------")

# ----------------------------
# Main function
# ----------------------------
if __name__ == "__main__":
    # Load portfolio
    portfolio = load_portfolio()

    # List of coins
    symbols = ["BTC-USD", "ETH-USD", "MANA-USD", "ONDO-USD", "IP-USD"]

    # Analyze each coin
    for symbol in symbols:
        fetcher = DataFetcher(symbol)  # ✅ pass ticker here
        data = fetcher.get_historical_prices(period="1mo")
        entry_price = portfolio.get(symbol.split("-")[0], {}).get("entry_price")
        analyze_coin(symbol, data, entry_price)
