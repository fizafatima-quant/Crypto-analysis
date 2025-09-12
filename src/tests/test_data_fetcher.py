# src/tests/test_data_fetcher.py
import pandas as pd
from data_fetcher import DataFetcher

def test_get_historical_prices():
    fetcher = DataFetcher("AAPL")
    df = fetcher.get_historical_prices(period="1mo")
    
    # Assertions
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "Close" in df.columns
    assert "Date" in df.columns

def test_get_option_chain():
    fetcher = DataFetcher("AAPL")
    expiries = fetcher.list_expiries()
    
    assert isinstance(expiries, list)
    assert len(expiries) > 0
    
    df = fetcher.get_option_chain(expiry=expiries[0])
    assert isinstance(df, pd.DataFrame)
    assert "contractSymbol" in df.columns
    assert "type" in df.columns

def test_list_expiries():
    fetcher = DataFetcher("AAPL")
    expiries = fetcher.list_expiries()
    
    assert isinstance(expiries, list)
    assert len(expiries) > 0
