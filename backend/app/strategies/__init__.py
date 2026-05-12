from app.strategies.base import (
    BaseStrategy,
    Signal,
    StockData,
    StrategyRegistry,
    StrategyResult,
)
from app.strategies.dual_ma import DualMAStrategy
from app.strategies.macd_strategy import MACDStrategy
from app.strategies.rsi_strategy import RSIStrategy


def register_builtin_strategies() -> None:
    """注册所有内置策略（幂等）"""
    for strategy_cls in [DualMAStrategy, MACDStrategy, RSIStrategy]:
        instance = strategy_cls()
        if StrategyRegistry.get(instance.name) is None:
            StrategyRegistry.register(instance)


__all__ = [
    "BaseStrategy",
    "Signal",
    "StockData",
    "StrategyResult",
    "StrategyRegistry",
    "DualMAStrategy",
    "MACDStrategy",
    "RSIStrategy",
    "register_builtin_strategies",
]
