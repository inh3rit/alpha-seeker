from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar

import pandas as pd


class Signal(Enum):
    """买卖信号"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class StockData:
    """策略输入：股票的价量数据

    prices 应包含列：trade_date, open, close, high, low, volume
    按 trade_date 升序排列（最近的数据在最后）
    """
    code: str
    prices: pd.DataFrame


@dataclass
class StrategyResult:
    """策略输出：信号、评分、理由"""
    signal: Signal
    score: float  # 0-100
    reason: str


class BaseStrategy(ABC):
    """策略基类"""

    name: ClassVar[str] = ""

    @abstractmethod
    def analyze(self, data: StockData) -> StrategyResult:
        """分析股票数据，返回信号、评分和理由"""
        raise NotImplementedError


class StrategyRegistry:
    """策略注册和查找"""

    _strategies: ClassVar[dict[str, BaseStrategy]] = {}

    @classmethod
    def register(cls, strategy: BaseStrategy) -> None:
        if not strategy.name:
            raise ValueError("策略必须设置非空的 name")
        cls._strategies[strategy.name] = strategy

    @classmethod
    def get(cls, name: str) -> BaseStrategy | None:
        return cls._strategies.get(name)

    @classmethod
    def get_all(cls) -> list[BaseStrategy]:
        return list(cls._strategies.values())
