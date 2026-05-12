from app.indicators.rsi import calculate_rsi
from app.strategies.base import BaseStrategy, Signal, StockData, StrategyResult


class RSIStrategy(BaseStrategy):
    """RSI 超买超卖策略"""

    name = "rsi"

    def __init__(
        self,
        period: int = 14,
        oversold_threshold: float = 30.0,
        overbought_threshold: float = 70.0,
    ) -> None:
        self.period = period
        self.oversold = oversold_threshold
        self.overbought = overbought_threshold

    def analyze(self, data: StockData) -> StrategyResult:
        closes = data.prices["close"].astype(float)
        min_required = self.period + 2

        if len(closes) < min_required:
            return StrategyResult(
                signal=Signal.HOLD, score=50.0,
                reason=f"数据不足：需要至少 {min_required} 条，当前 {len(closes)}",
            )

        rsi = calculate_rsi(closes, self.period)
        curr_rsi = float(rsi.iloc[-1])

        if curr_rsi < self.oversold:
            score = min(100.0, 70.0 + (self.oversold - curr_rsi))
            return StrategyResult(
                signal=Signal.BUY, score=score,
                reason=f"RSI={curr_rsi:.2f} 超卖（< {self.oversold}）",
            )

        if curr_rsi > self.overbought:
            score = max(0.0, 30.0 - (curr_rsi - self.overbought))
            return StrategyResult(
                signal=Signal.SELL, score=score,
                reason=f"RSI={curr_rsi:.2f} 超买（> {self.overbought}）",
            )

        score = 50.0 + (50.0 - curr_rsi) * 0.3
        return StrategyResult(
            signal=Signal.HOLD,
            score=max(0.0, min(100.0, score)),
            reason=f"RSI={curr_rsi:.2f} 中性",
        )
