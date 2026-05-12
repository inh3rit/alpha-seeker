from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from app.data.fetcher import AKShareFetcher, StockInfo, StockQuote


def test_stock_info_dataclass():
    info = StockInfo(code="600519", name="贵州茅台", industry="食品饮料")
    assert info.code == "600519"
    assert info.name == "贵州茅台"


def test_stock_quote_dataclass():
    quote = StockQuote(
        code="600519", trade_date=date(2026, 5, 12),
        open=Decimal("1800.00"), close=Decimal("1850.00"),
        high=Decimal("1860.00"), low=Decimal("1795.00"),
        volume=1000000, amount=Decimal("1850000000.00"),
    )
    assert quote.close == Decimal("1850.00")


def test_fetch_stock_list_parses_dataframe():
    fake_df = pd.DataFrame([
        {"code": "600519", "name": "贵州茅台"},
        {"code": "000001", "name": "平安银行"},
    ])
    with patch("app.data.fetcher.ak.stock_info_a_code_name", return_value=fake_df):
        fetcher = AKShareFetcher()
        stocks = fetcher.fetch_stock_list()
        assert len(stocks) == 2
        assert stocks[0].code == "600519"
        assert stocks[1].code == "000001"


def test_fetch_stock_list_handles_empty_response():
    with patch("app.data.fetcher.ak.stock_info_a_code_name", return_value=pd.DataFrame()):
        fetcher = AKShareFetcher()
        stocks = fetcher.fetch_stock_list()
        assert stocks == []


def test_fetch_stock_list_retries_on_failure():
    mock_fn = MagicMock(side_effect=[
        ConnectionError("network error"),
        pd.DataFrame([{"code": "600519", "name": "贵州茅台"}]),
    ])
    with patch("app.data.fetcher.ak.stock_info_a_code_name", mock_fn):
        fetcher = AKShareFetcher(max_retries=2, retry_delay=0)
        stocks = fetcher.fetch_stock_list()
        assert len(stocks) == 1
        assert mock_fn.call_count == 2


def test_fetch_stock_list_raises_after_max_retries():
    with patch(
        "app.data.fetcher.ak.stock_info_a_code_name",
        side_effect=ConnectionError("persistent error"),
    ):
        fetcher = AKShareFetcher(max_retries=2, retry_delay=0)
        with pytest.raises(ConnectionError):
            fetcher.fetch_stock_list()


def test_fetch_daily_quotes_parses_dataframe():
    fake_df = pd.DataFrame([
        {
            "日期": "2026-05-10",
            "开盘": 1800.00, "收盘": 1850.00,
            "最高": 1860.00, "最低": 1795.00,
            "成交量": 1000000, "成交额": 1850000000.00,
        },
        {
            "日期": "2026-05-11",
            "开盘": 1850.00, "收盘": 1880.00,
            "最高": 1890.00, "最低": 1840.00,
            "成交量": 1200000, "成交额": 2256000000.00,
        },
    ])
    with patch("app.data.fetcher.ak.stock_zh_a_hist", return_value=fake_df):
        fetcher = AKShareFetcher()
        quotes = fetcher.fetch_daily_quotes(
            code="600519", start_date=date(2026, 5, 10), end_date=date(2026, 5, 11),
        )
        assert len(quotes) == 2
        assert quotes[0].code == "600519"
        assert quotes[0].trade_date == date(2026, 5, 10)
        assert quotes[0].close == Decimal("1850.00")


def test_fetch_daily_quotes_empty_returns_empty_list():
    with patch("app.data.fetcher.ak.stock_zh_a_hist", return_value=pd.DataFrame()):
        fetcher = AKShareFetcher()
        quotes = fetcher.fetch_daily_quotes(
            code="600519", start_date=date(2026, 5, 10), end_date=date(2026, 5, 11),
        )
        assert quotes == []


def test_fetch_daily_quotes_passes_formatted_dates():
    mock_fn = MagicMock(return_value=pd.DataFrame())
    with patch("app.data.fetcher.ak.stock_zh_a_hist", mock_fn):
        fetcher = AKShareFetcher()
        fetcher.fetch_daily_quotes(
            code="600519", start_date=date(2026, 5, 10), end_date=date(2026, 5, 11),
        )
        call_kwargs = mock_fn.call_args.kwargs
        assert call_kwargs["symbol"] == "600519"
        assert call_kwargs["start_date"] == "20260510"
        assert call_kwargs["end_date"] == "20260511"
        assert call_kwargs["adjust"] == "qfq"
