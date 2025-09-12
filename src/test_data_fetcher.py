import pytest
from data_fetcher import DataFetcher

def test_historical_prices():
    df = DataFetcher("AAPL").get_historical_prices(period="1mo")
    assert not df.empty
    for col in ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']:
        assert col in df.columns

def test_option_chain():
    df = DataFetcher("AAPL").get_option_chain()
    assert not df.empty
    assert 'type' in df.columns
    types = set(df['type'].unique())
    assert 'call' in types and 'put' in types

def test_list_expiries():
    expiries = DataFetcher("AAPL").list_expiries()
    assert isinstance(expiries, list)
    assert len(expiries) > 0
