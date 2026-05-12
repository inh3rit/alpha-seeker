import time
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import akshare as ak
import pandas as pd
from loguru import logger


@dataclass
class StockInfo:
    """股票基本信息"""
    code: str
    name: str
    industry: str | None = None
    sector: str | None = None
    list_date: date | None = None


@dataclass
class StockQuote:
    """股票日线行情"""
    code: str
    trade_date: date
    open: Decimal
    close: Decimal
    high: Decimal
    low: Decimal
    volume: int
    amount: Decimal


class AKShareFetcher:
    """AKShare 数据抓取器"""

    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0) -> None:
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _retry(self, func, *args, **kwargs):
        """带重试的调用"""
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    f"AKShare 调用失败（第 {attempt}/{self.max_retries} 次）: {exc}"
                )
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
        assert last_exc is not None
        raise last_exc

    def fetch_stock_list(self) -> list[StockInfo]:
        """抓取 A 股股票列表"""
        logger.info("抓取 A 股股票列表...")
        df: pd.DataFrame = self._retry(ak.stock_info_a_code_name)
        if df.empty:
            logger.warning("AKShare 返回空列表")
            return []

        stocks = [
            StockInfo(code=str(row["code"]), name=str(row["name"]))
            for _, row in df.iterrows()
        ]
        logger.info(f"抓取到 {len(stocks)} 只股票")
        return stocks

    def fetch_daily_quotes(
        self,
        code: str,
        start_date: date,
        end_date: date,
    ) -> list[StockQuote]:
        """抓取指定股票在日期区间内的日线行情（前复权）"""
        logger.info(f"抓取 {code} 日线行情: {start_date} ~ {end_date}")
        df: pd.DataFrame = self._retry(
            ak.stock_zh_a_hist,
            symbol=code,
            period="daily",
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
            adjust="qfq",
        )
        if df.empty:
            logger.warning(f"{code} 在 {start_date} ~ {end_date} 无数据")
            return []

        quotes: list[StockQuote] = []
        for _, row in df.iterrows():
            trade_date_str = str(row["日期"])
            quotes.append(
                StockQuote(
                    code=code,
                    trade_date=date.fromisoformat(trade_date_str[:10]),
                    open=Decimal(str(row["开盘"])),
                    close=Decimal(str(row["收盘"])),
                    high=Decimal(str(row["最高"])),
                    low=Decimal(str(row["最低"])),
                    volume=int(row["成交量"]),
                    amount=Decimal(str(row["成交额"])),
                )
            )
        logger.info(f"{code}: 抓取到 {len(quotes)} 条日线数据")
        return quotes
