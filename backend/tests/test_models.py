from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.stock import Stock
from app.models.quote import DailyQuote
from app.models.indicator import Indicator


@pytest.fixture
def in_memory_db():
    """使用内存 SQLite 数据库进行模型测试"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


# --- Stock 模型测试 ---

def test_stock_can_be_created_with_required_fields(in_memory_db):
    stock = Stock(
        code="600519",
        name="贵州茅台",
        industry="食品饮料",
        sector="主板",
        list_date=date(2001, 8, 27),
    )
    in_memory_db.add(stock)
    in_memory_db.commit()

    result = in_memory_db.query(Stock).filter_by(code="600519").first()
    assert result is not None
    assert result.name == "贵州茅台"
    assert result.industry == "食品饮料"


def test_stock_code_is_primary_key(in_memory_db):
    stock1 = Stock(code="600519", name="贵州茅台")
    in_memory_db.add(stock1)
    in_memory_db.commit()

    stock2 = Stock(code="600519", name="不同名称")
    in_memory_db.add(stock2)
    with pytest.raises(Exception):
        in_memory_db.commit()


def test_stock_repr(in_memory_db):
    stock = Stock(code="600519", name="贵州茅台")
    assert "600519" in repr(stock)
    assert "贵州茅台" in repr(stock)


# --- DailyQuote 模型测试 ---

def test_daily_quote_can_be_created(in_memory_db):
    quote = DailyQuote(
        code="600519",
        trade_date=date(2026, 5, 12),
        open=Decimal("1800.00"),
        close=Decimal("1850.00"),
        high=Decimal("1860.00"),
        low=Decimal("1795.00"),
        volume=1000000,
        amount=Decimal("1850000000.00"),
    )
    in_memory_db.add(quote)
    in_memory_db.commit()

    result = in_memory_db.query(DailyQuote).filter_by(
        code="600519", trade_date=date(2026, 5, 12)
    ).first()
    assert result is not None
    assert result.close == Decimal("1850.00")


def test_daily_quote_unique_on_code_and_date(in_memory_db):
    q1 = DailyQuote(
        code="600519", trade_date=date(2026, 5, 12),
        open=Decimal("1800.00"), close=Decimal("1850.00"),
        high=Decimal("1860.00"), low=Decimal("1795.00"),
        volume=1000000, amount=Decimal("1850000000.00"),
    )
    in_memory_db.add(q1)
    in_memory_db.commit()

    q2 = DailyQuote(
        code="600519", trade_date=date(2026, 5, 12),
        open=Decimal("1810.00"), close=Decimal("1860.00"),
        high=Decimal("1870.00"), low=Decimal("1800.00"),
        volume=2000000, amount=Decimal("3720000000.00"),
    )
    in_memory_db.add(q2)
    with pytest.raises(Exception):
        in_memory_db.commit()


# --- Indicator 模型测试 ---

def test_indicator_can_be_created(in_memory_db):
    indicator = Indicator(
        code="600519",
        trade_date=date(2026, 5, 12),
        indicator_type="MA",
        indicator_value={"ma5": 1820.5, "ma20": 1780.3, "ma60": 1750.0},
    )
    in_memory_db.add(indicator)
    in_memory_db.commit()

    result = in_memory_db.query(Indicator).filter_by(
        code="600519", trade_date=date(2026, 5, 12), indicator_type="MA"
    ).first()
    assert result is not None
    assert result.indicator_value["ma5"] == 1820.5


def test_indicator_unique_on_code_date_type(in_memory_db):
    i1 = Indicator(
        code="600519", trade_date=date(2026, 5, 12),
        indicator_type="MA", indicator_value={"ma5": 1820.5},
    )
    in_memory_db.add(i1)
    in_memory_db.commit()

    i2 = Indicator(
        code="600519", trade_date=date(2026, 5, 12),
        indicator_type="MA", indicator_value={"ma5": 9999.0},
    )
    in_memory_db.add(i2)
    with pytest.raises(Exception):
        in_memory_db.commit()
