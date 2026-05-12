from app.indicators.ma import calculate_ma
from app.strategies.base import BaseStrategy, Signal, StockData, StrategyResult


class DualMAStrategy(BaseStrategy):
    """双均线策略"""

    name = "dual_ma"

    def __init__(self, short_period: int = 5, long_period: int = 20) -> None:
        if short_period <= 0 or long_period <= 0:
            raise ValueError(f"周期必须 > 0，当前 short={short_period}, long={long_period}")
        if short_period >= long_period:
            raise ValueError(f"short_period({short_period}) 必须 < long_period({long_period})")
        self.short_period = short_period
        self.long_period = long_period

    def analyze(self, data: StockData) -> StrategyResult:
        closes = data.prices["close"].astype(float)

        if len(closes) < self.long_period + 1:
            return StrategyResult(
                signal=Signal.HOLD, score=50.0,
                reason=f"数据不足：需要至少 {self.long_period + 1} 条，当前 {len(closes)}",
            )

        ma_short = calculate_ma(closes, self.short_period)
        ma_long = calculate_ma(closes, self.long_period)

        prev_short = ma_short.iloc[-2]
        prev_long = ma_long.iloc[-2]
        curr_short = ma_short.iloc[-1]
        curr_long = ma_long.iloc[-1]

        if prev_short <= prev_long and curr_short > curr_long:
            diff_pct = (curr_short - curr_long) / curr_long * 100
            return StrategyResult(
                signal=Signal.BUY,
                score=min(100.0, 60.0 + diff_pct * 10),
                reason=f"MA{self.short_period} 上穿 MA{self.long_period} 金叉（差距 {diff_pct:.2f}%）",
            )

        if prev_short >= prev_long and curr_short < curr_long:
            diff_pct = (curr_long - curr_short) / curr_long * 100
            return StrategyResult(
                signal=Signal.SELL,
                score=max(0.0, 40.0 - diff_pct * 10),
                reason=f"MA{self.short_period} 下穿 MA{self.long_period} 死叉（差距 {diff_pct:.2f}%）",
            )

        if curr_short > curr_long:
            return StrategyResult(signal=Signal.HOLD, score=60.0,
                                  reason=f"多头排列（MA{self.short_period} > MA{self.long_period}）")
        return StrategyResult(signal=Signal.HOLD, score=40.0,
                              reason=f"空头排列（MA{self.short_period} < MA{self.long_period}）")
