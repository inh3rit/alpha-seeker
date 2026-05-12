from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.data.fetcher import StockInfo, StockQuote
from app.data.storage import DataStorage
from app.database import Base
from app.models import DailyQuote, Stock


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_upsert_stocks_inserts_new_records(db_session):
    storage = DataStorage(db_session)
    storage.upsert_stocks([
        StockInfo(code="600519", name="贵州茅台"),
        StockInfo(code="000001", name="平安银行"),
    ])
    assert db_session.query(Stock).count() == 2


def test_upsert_stocks_updates_existing_records(db_session):
    storage = DataStorage(db_session)
    storage.upsert_stocks([StockInfo(code="600519", name="旧名称")])
    storage.upsert_stocks([StockInfo(code="600519", name="贵州茅台")])
    stock = db_session.query(Stock).filter_by(code="600519").one()
    assert stock.name == "贵州茅台"
    assert db_session.query(Stock).count() == 1


def test_upsert_stocks_empty_list_is_noop(db_session):
    storage = DataStorage(db_session)
    storage.upsert_stocks([])
    assert db_session.query(Stock).count() == 0


def test_upsert_quotes_inserts_new_records(db_session):
    storage = DataStorage(db_session)
    storage.upsert_quotes([
        StockQuote(
            code="600519", trade_date=date(2026, 5, 10),
            open=Decimal("1800.00"), close=Decimal("1850.00"),
            high=Decimal("1860.00"), low=Decimal("1795.00"),
            volume=1000000, amount=Decimal("1850000000.00"),
        ),
    ])
    assert db_session.query(DailyQuote).count() == 1


def test_upsert_quotes_updates_existing_records(db_session):
    storage = DataStorage(db_session)
    q = StockQuote(
        code="600519", trade_date=date(2026, 5, 10),
        open=Decimal("1800.00"), close=Decimal("1850.00"),
        high=Decimal("1860.00"), low=Decimal("1795.00"),
        volume=1000000, amount=Decimal("1850000000.00"),
    )
    storage.upsert_quotes([q])

    q_updated = StockQuote(
        code="600519", trade_date=date(2026, 5, 10),
        open=Decimal("1800.00"), close=Decimal("9999.00"),
        high=Decimal("9999.00"), low=Decimal("1795.00"),
        volume=2000000, amount=Decimal("1850000000.00"),
    )
    storage.upsert_quotes([q_updated])

    records = db_session.query(DailyQuote).all()
    assert len(records) == 1
    assert records[0].close == Decimal("9999.00")


def test_get_quotes_returns_sorted_by_date(db_session):
    storage = DataStorage(db_session)
    storage.upsert_quotes([
        StockQuote(
            code="600519", trade_date=date(2026, 5, 11),
            open=Decimal("1850.00"), close=Decimal("1880.00"),
            high=Decimal("1890.00"), low=Decimal("1840.00"),
            volume=1200000, amount=Decimal("2256000000.00"),
        ),
        StockQuote(
            code="600519", trade_date=date(2026, 5, 10),
            open=Decimal("1800.00"), close=Decimal("1850.00"),
            high=Decimal("1860.00"), low=Decimal("1795.00"),
            volume=1000000, amount=Decimal("1850000000.00"),
        ),
    ])
    quotes = storage.get_quotes("600519", date(2026, 5, 10), date(2026, 5, 11))
    assert len(quotes) == 2
    assert quotes[0].trade_date == date(2026, 5, 10)
    assert quotes[1].trade_date == date(2026, 5, 11)


def test_list_stock_codes_returns_sorted_codes(db_session):
    storage = DataStorage(db_session)
    storage.upsert_stocks([
        StockInfo(code="000001", name="平安银行"),
        StockInfo(code="600519", name="贵州茅台"),
    ])
    codes = storage.list_stock_codes()
    assert codes == ["000001", "600519"]
