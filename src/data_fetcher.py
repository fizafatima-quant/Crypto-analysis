# src/data_fetcher.py
import yfinance as yf
import pandas as pd
from typing import List

class DataFetcher:
    """
    Fetch historical & option chain data for a given ticker.
    """
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.asset = yf.Ticker(ticker)
    
    def get_historical_prices(self, period: str = "1y") -> pd.DataFrame:
        """
        Fetch historical price data.
        period: '1y', '6mo', '1mo', etc.
        """
        df = self.asset.history(period=period)
        df.reset_index(inplace=True)
        return df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    
    def get_option_chain(self, expiry: str = None) -> pd.DataFrame:
        """
        Fetch options for given expiry. If expiry=None, fetch the nearest expiry.
        """
        if expiry is None:
            expiry = self.asset.options[0]  # nearest expiry
        chain = self.asset.option_chain(expiry)
        calls = chain.calls
        puts = chain.puts
        calls['type'] = 'call'
        puts['type'] = 'put'
        return pd.concat([calls, puts], ignore_index=True)

    def list_expiries(self) -> list:
        """
        List available option expiries
        """
        return list(self.asset.options)  # ensure a list is returned
