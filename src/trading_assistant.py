import os
import time
import pandas as pd
from dotenv import load_dotenv
from .data_fetcher import DataFetcher  # Make sure this file is in src/
import telebot

# Load environment variables
load_dotenv()

# Telegram setup
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_IDS = [cid.strip() for cid in os.getenv("TELEGRAM_CHAT_IDS", "").split(",")]

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_IDS:
    raise ValueError("Telegram token or chat IDs not set in .env!")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Trading setup
TICKERS = os.getenv("TICKERS", "BTC,ETH,SOL").split(",")
ENTRY_PRICES = {ticker.upper(): None for ticker in TICKERS}  # Set manually if bought
UPDATE_INTERVAL = 600  # seconds

def generate_signals(df):
    df['MA5'] = df['Close'].rolling(5).mean()
    df['MA20'] = df['Close'].rolling(20).mean()
    df['signal'] = ""
    df.loc[df['Close'] > df['MA5'], 'signal'] = "BUY"
    df.loc[df['Close'] < df['MA5'], 'signal'] = "SELL"
    return df

def analyze_coin(ticker):
    fetcher = DataFetcher(ticker)
    df = fetcher.get_historical_prices()  # returns a DataFrame with 'Close'
    if df.empty:
        print(f"No price data found for {ticker}")
        return

    df = generate_signals(df)
    current_price = df['Close'].iloc[-1]
    ma5 = df['MA5'].iloc[-1]
    ma20 = df['MA20'].iloc[-1]

    # Trend strength
    trend_strength = round(((ma5 - ma20)/ma20)*100, 2) if ma20 != 0 else 0

    # Profit/loss percentage
    entry_price = ENTRY_PRICES.get(ticker)
    profit_pct = round(((current_price - entry_price)/entry_price)*100, 2) if entry_price else 0

    # Print analysis
    print(f"--- {ticker} Analysis ---")
    print(f"Current Price: {current_price:.4f}")
    print(f"MA5: {ma5:.4f}, MA20: {ma20:.4f}")
    print(f"Signal: {df['signal'].iloc[-1]} {'✅' if df['signal'].iloc[-1]=='BUY' else '❌'}")
    print(f"Trend strength: {trend_strength}%")
    if entry_price:
        print(f"Profit/Loss: {profit_pct}%")
    print("-------------------------")

    # Send Telegram alerts
    msg = f"{ticker} | Price: {current_price:.4f} | Signal: {df['signal'].iloc[-1]} | Trend: {trend_strength}%"
    if entry_price:
        msg += f" | Profit/Loss: {profit_pct}%"
        if profit_pct >= 50:
            msg += " 🚀 +50% Profit!"
        elif profit_pct <= -20:
            msg += " ⚠️ -20% Loss!"

    for chat_id in TELEGRAM_CHAT_IDS:
        try:
            bot.send_message(chat_id, msg)
        except Exception as e:
            print(f"Failed to send alert to {chat_id}: {e}")

def run_trading_assistant():
    print("Starting Trading Assistant...")
    # Ask user to enter/update entry prices
    for ticker in TICKERS:
        user_input = input(f"Update entry price? Enter {ticker} price or press Enter to skip: ")
        if user_input:
            try:
                ENTRY_PRICES[ticker] = float(user_input)
            except ValueError:
                print(f"Invalid price entered for {ticker}, skipping.")

    while True:
        for ticker in TICKERS:
            try:
                analyze_coin(ticker)
            except Exception as e:
                print(f"Error analyzing {ticker}: {e}")
        print(f"Waiting {UPDATE_INTERVAL/60} minutes before next update...\n")
        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    run_trading_assistant()
