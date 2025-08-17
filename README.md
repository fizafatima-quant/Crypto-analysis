# 🔄 DEX Backtester & Liquidity Analysis Toolkit

**Quantifying vampire attacks and liquidity migration in decentralized exchanges**  
*(Project in active development - last updated MM/DD/YYYY)*  

## 🎯 Project Focus
- **Tracking** liquidity flows during DEX "vampire attacks" (e.g., SushiSwap vs Uniswap)
- **Backtesting** LP migration strategies
- **Analyzing** token incentive effectiveness

## 🛠️ Current Implementation
```bash
├── data/                   # Raw and processed on-chain datasets
├── notebooks/              # Jupyter analysis notebooks (WIP)
│   └── liquidity_flow.ipynb  # Initial TVL migration analysis
├── scripts/                # Python modules
│   ├── data_fetcher.py     # Fetch DEX data from APIs
│   └── metrics.py          # Calculate LP metrics
└── requirements.txt        # Python dependencies
