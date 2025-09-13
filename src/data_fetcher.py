import pandas as pd
from pycoingecko import CoinGeckoAPI

# Mapping of coin symbols to CoinGecko IDs
COIN_MAPPING = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "ONDO": "ondo",
    "MANA": "decentraland",
    "IP": "illuvium",
    "ILLUVIUM": "illuvium",
    "DECENTRALAND": "decentraland"
}

class DataFetcher:
    def __init__(self, symbol):
        self.symbol = symbol.upper()
        if self.symbol not in COIN_MAPPING:
            raise ValueError(f"Coin ID not found for symbol: {self.symbol}")
        self.coin_id = COIN_MAPPING[self.symbol]
        self.cg = CoinGeckoAPI()

    def get_historical_prices(self, days=30):
        """
        Fetch historical market data for the coin.
        Returns a pandas DataFrame with 'Date' and 'Close' columns.
        """
        try:
            data = self.cg.get_coin_market_chart_by_id(
                id=self.coin_id,
                vs_currency='usd',
                days=days
            )
            if "prices" not in data:
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(data["prices"], columns=["timestamp", "Close"])
            df["Date"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("Date", inplace=True)
            df.drop("timestamp", axis=1, inplace=True)
            return df
        except Exception as e:
            print(f"Error fetching data for {self.symbol}: {e}")
            return pd.DataFrame()
