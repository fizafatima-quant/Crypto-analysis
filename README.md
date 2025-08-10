# Crypto Technical Analysis Toolkit

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Backtrader](https://img.shields.io/badge/backtrader-2.0-green)
![Status](https://img.shields.io/badge/status-active-brightgreen)

A Python-based cryptocurrency analysis system implementing:
- Real-time data fetching
- Technical indicators (RSI, MACD, Bollinger Bands)
- Automated trading signals
- Backtesting framework (Step 8 coming soon)

## 📦 Current Implementation (Steps 1-7)

### Implemented Modules
| File | Purpose | Status |
|------|---------|--------|
| `data_fetcher.py` | Fetches OHLCV data from Binance | ✅ Working |
| `indicators.py` | Calculates technical indicators | ✅ Working |
| `signals.py` | Generates buy/sell signals | ✅ Working |

## 🛠️ Setup

### Prerequisites
```bash
git clone https://github.com/yourusername/crypto-analysis.git
cd crypto-analysis
python -m venv venv
venv\Scripts\activate  # Windows

