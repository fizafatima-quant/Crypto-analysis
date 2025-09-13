import pandas as pd
from pycoingecko import CoinGeckoAPI

class DataFetcher:
    # Map ticker symbols to CoinGecko IDs
    COIN_ID_MAP = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "ONDO": "ondo",
        "MANA": "decentraland",
        "IP": "illuvium"
    }

    def __init__(self, symbol):
        self.symbol = symbol.upper()
        self.cg = CoinGeckoAPI()
        self.coin_id = self.COIN_ID_MAP.get(self.symbol)
        if not self.coin_id:
            raise ValueError(f"Coin ID not found for symbol: {self.symbol}")

    def get_historical_prices(self, days=30):
        """Fetches historical market data for the coin for the last `days` days."""
        try:
            data = self.cg.get_coin_market_chart_by_id(
                id=self.coin_id,
                vs_currency='usd',
                days=days
            )
            prices = data['prices']  # list of [timestamp, price]
            df = pd.DataFrame(prices, columns=['time', 'Close'])
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            df.set_index('time', inplace=True)
            return df
        except Exception as e:
            print(f"Error fetching data for {self.symbol}: {e}")
            return pd.DataFrame()  # return empty DataFrame on error
