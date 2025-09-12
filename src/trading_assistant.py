# src/trading_assistant.py
from src.data_fetcher import DataFetcher
import pandas as pd
import numpy as np
import ta
import os
from dotenv import load_dotenv
from datetime import datetime
import matplotlib.pyplot as plt

# -----------------------------
# Config
# -----------------------------
load_dotenv()
TICKERS = os.getenv("TICKERS", "BTC-USD,ETH-USD,SOL-USD").split(",")
OUTPUT_CSV = os.getenv("OUTPUT_CSV", "crypto_trading_signals.csv")
PLOT_DIR = os.getenv("PLOT_DIR", "crypto_plots")
os.makedirs(PLOT_DIR, exist_ok=True)

# -----------------------------
# Indicator & Signal Functions
# -----------------------------
def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df['MA5'] = df['Close'].rolling(5).mean()
    df['MA20'] = df['Close'].rolling(20).mean()
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df['Return'] = df['Close'].pct_change()
    df['Volatility'] = df['Return'].rolling(20).std() * np.sqrt(252)
    return df

def generate_signal(df: pd.DataFrame) -> dict:
    latest = df.iloc[-1]
    score = 0
    if latest['MA5'] > latest['MA20']:
        score += 1
    elif latest['MA5'] < latest['MA20']:
        score -= 1
    if latest['RSI'] < 30:
        score += 1
    elif latest['RSI'] > 70:
        score -= 1
    if latest['MACD'] > latest['MACD_signal']:
        score += 1
    elif latest['MACD'] < latest['MACD_signal']:
        score -= 1
    signal = 1 if score > 0 else (-1 if score < 0 else 0)
    confidence = abs(score) / 3
    return {"signal": signal, "confidence": confidence}

# -----------------------------
# Analysis & Dashboard
# -----------------------------
def analyze_ticker(ticker: str) -> dict:
    fetcher = DataFetcher(ticker)
    df = fetcher.get_historical_prices(period="3mo")
    df = calculate_indicators(df)
    sig_info = generate_signal(df)
    latest = df.iloc[-1]
    trend_strength = (latest['MA5'] - latest['MA20']) / latest['MA20'] * 100

    result = {
        "Ticker": ticker,
        "Date": latest['Date'],
        "Price": latest['Close'],
        "MA5": latest['MA5'],
        "MA20": latest['MA20'],
        "RSI": latest['RSI'],
        "MACD": latest['MACD'],
        "MACD_signal": latest['MACD_signal'],
        "Volatility": latest['Volatility'],
        "Signal": "BUY" if sig_info['signal'] == 1 else ("SELL" if sig_info['signal'] == -1 else "HOLD"),
        "Confidence": sig_info['confidence'],
        "Trend_strength_%": trend_strength
    }

    print(f"\n--- {ticker} Analysis ---")
    for k, v in result.items():
        if k != "Date":
            if isinstance(v, float):
                print(f"{k}: {v:.2f}")
            else:
                print(f"{k}: {v}")
    print("-------------------------")

    # Plot price & MAs
    plt.figure(figsize=(12,5))
    plt.plot(df['Date'], df['Close'], label='Close', color='blue')
    plt.plot(df['Date'], df['MA5'], label='MA5', color='green')
    plt.plot(df['Date'], df['MA20'], label='MA20', color='red')
    plt.title(f"{ticker} Price & Moving Averages")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, f"{ticker}_price_ma.png"))
    plt.close()

    # Plot RSI
    plt.figure(figsize=(12,3))
    plt.plot(df['Date'], df['RSI'], label='RSI', color='purple')
    plt.axhline(70, color='red', linestyle='--')
    plt.axhline(30, color='green', linestyle='--')
    plt.title(f"{ticker} RSI")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, f"{ticker}_RSI.png"))
    plt.close()

    return result

# -----------------------------
# Main execution
# -----------------------------
if __name__ == "__main__":
    dashboard = []
    for t in TICKERS:
        dashboard.append(analyze_ticker(t.strip()))

    df_dashboard = pd.DataFrame(dashboard)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = OUTPUT_CSV.replace(".csv", f"_{timestamp}.csv")
    df_dashboard.to_csv(output_file, index=False)
    print(f"\n✅ Crypto trading dashboard saved to: {output_file}")
    print(f"📊 Plots saved in folder: {PLOT_DIR}")
