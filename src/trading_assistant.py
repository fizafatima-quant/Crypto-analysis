import time
import os
from dotenv import load_dotenv
import telebot
from .data_fetcher import DataFetcher 

# Load environment variables from .env
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_IDS = [
    os.getenv("TELEGRAM_CHAT_ID_ME"),
    os.getenv("TELEGRAM_CHAT_ID_FRIEND")
]

if TELEGRAM_BOT_TOKEN is None:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set! Check your .env file.")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Coin symbols
COINS = ["BTC", "ETH", "SOL", "ONDO", "MANA", "IP"]

# Dictionary to store entry prices
entry_prices = {}

# Function to send Telegram messages to all chat IDs
def send_telegram(msg):
    for chat_id in TELEGRAM_CHAT_IDS:
        if chat_id:
            try:
                bot.send_message(chat_id=chat_id, text=msg)
            except Exception as e:
                print(f"Telegram send failed: {e}")

# Function to calculate profit/loss percentage
def calculate_profit(current_price, entry_price):
    if entry_price is None:
        return 0.0
    return ((current_price - entry_price) / entry_price) * 100

# Analyze single coin
def analyze_coin(symbol):
    try:
        fetcher = DataFetcher(symbol)
        df = fetcher.get_historical_prices()  # should return a DataFrame with 'Close'

        if df.empty or 'Close' not in df.columns:
            print(f"No price data found for {symbol}")
            return

        current_price = df['Close'].iloc[-1]
        ma5 = df['Close'].rolling(window=5).mean().iloc[-1]
        ma20 = df['Close'].rolling(window=20).mean().iloc[-1]

        signal = "BUY ✅" if current_price > ma5 else "SELL ❌"

        entry_price = entry_prices.get(symbol)
        profit = calculate_profit(current_price, entry_price)

        # Print analysis
        print(f"--- {symbol} Analysis ---")
        print(f"Current Price: {current_price:.4f}")
        print(f"MA5: {ma5:.4f}, MA20: {ma20:.4f}")
        print(f"Signal: {signal}")
        print(f"Profit: {profit:.2f}%")
        print("-------------------------")

        # Telegram alert
        msg = f"{symbol} | Price: {current_price:.4f} | Signal: {signal} | Profit: {profit:.2f}%"
        send_telegram(msg)

        # Loss alert at -20%
        if profit <= -20:
            send_telegram(f"⚠️ ALERT! {symbol} has fallen -20% or more! Current Profit: {profit:.2f}%")

    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")

# Main loop
def run_trading_assistant(update_interval=600):
    print("Starting Trading Assistant...")

    # Ask for entry prices once
    for coin in COINS:
        try:
            price_input = input(f"Enter {coin} entry price or press Enter to skip: ").strip()
            if price_input:
                entry_prices[coin] = float(price_input)
            else:
                entry_prices[coin] = None
        except ValueError:
            entry_prices[coin] = None

    while True:
        for coin in COINS:
            analyze_coin(coin)
        print(f"Waiting {update_interval/60:.1f} minutes before next update...\n")
        time.sleep(update_interval)

if __name__ == "__main__":
    run_trading_assistant()
