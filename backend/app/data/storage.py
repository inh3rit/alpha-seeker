from datetime import date

import pandas as pd
from loguru import logger
from sqlalchemy.orm import Session

from app.data.fetcher import StockInfo, StockQuote
from app.models import DailyQuote, Stock


class DataStorage:
    """数据存储层，实现 upsert 和查询"""

    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert_stocks(self, stocks: list[StockInfo]) -> None:
        """插入或更新股票基本信息"""
        if not stocks:
            return

        for info in stocks:
            existing = self.session.get(Stock, info.code)
            if existing is None:
                self.session.add(Stock(
                    code=info.code,
                    name=info.name,
                    industry=info.industry,
                    sector=info.sector,
                    list_date=info.list_date,
                ))
            else:
                existing.name = info.name
                if info.industry is not None:
                    existing.industry = info.industry
                if info.sector is not None:
                    existing.sector = info.sector
                if info.list_date is not None:
                    existing.list_date = info.list_date

        self.session.commit()
        logger.info(f"upsert {len(stocks)} 只股票")

    def upsert_quotes(self, quotes: list[StockQuote]) -> None:
        """插入或更新日线行情"""
        if not quotes:
            return

        for q in quotes:
            existing = (
                self.session.query(DailyQuote)
                .filter_by(code=q.code, trade_date=q.trade_date)
                .one_or_none()
            )
            if existing is None:
                self.session.add(DailyQuote(
                    code=q.code,
                    trade_date=q.trade_date,
                    open=q.open,
                    close=q.close,
                    high=q.high,
                    low=q.low,
                    volume=q.volume,
                    amount=q.amount,
                ))
            else:
                existing.open = q.open
                existing.close = q.close
                existing.high = q.high
                existing.low = q.low
                existing.volume = q.volume
                existing.amount = q.amount

        self.session.commit()
        logger.info(f"upsert {len(quotes)} 条行情")

    def get_quotes(
        self, code: str, start_date: date, end_date: date
    ) -> list[DailyQuote]:
        """查询指定股票在日期区间内的日线行情（按日期升序）"""
        return (
            self.session.query(DailyQuote)
            .filter(
                DailyQuote.code == code,
                DailyQuote.trade_date >= start_date,
                DailyQuote.trade_date <= end_date,
            )
            .order_by(DailyQuote.trade_date.asc())
            .all()
        )

    def list_stock_codes(self) -> list[str]:
        """返回 stocks 表中所有股票代码"""
        return [s.code for s in self.session.query(Stock).order_by(Stock.code).all()]

    def load_stock_data(self, code: str, start_date: date, end_date: date):
        """从数据库加载并构造 StockData 供策略使用"""
        from app.strategies.base import StockData

        quotes = self.get_quotes(code, start_date, end_date)

        df = pd.DataFrame([
            {
                "trade_date": q.trade_date,
                "open": float(q.open),
                "close": float(q.close),
                "high": float(q.high),
                "low": float(q.low),
                "volume": int(q.volume),
            }
            for q in quotes
        ], columns=["trade_date", "open", "close", "high", "low", "volume"])

        return StockData(code=code, prices=df)
