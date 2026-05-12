from app.indicators.macd import calculate_macd
from app.strategies.base import BaseStrategy, Signal, StockData, StrategyResult


class MACDStrategy(BaseStrategy):
    """MACD 策略"""

    name = "macd"

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9) -> None:
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def analyze(self, data: StockData) -> StrategyResult:
        closes = data.prices["close"].astype(float)
        min_required = self.slow + self.signal + 1

        if len(closes) < min_required:
            return StrategyResult(
                signal=Signal.HOLD, score=50.0,
                reason=f"数据不足：需要至少 {min_required} 条，当前 {len(closes)}",
            )

        result = calculate_macd(closes, self.fast, self.slow, self.signal)
        prev_dif = result.dif.iloc[-2]
        prev_dea = result.dea.iloc[-2]
        curr_dif = result.dif.iloc[-1]
        curr_dea = result.dea.iloc[-1]
        curr_hist = result.histogram.iloc[-1]

        if prev_dif <= prev_dea and curr_dif > curr_dea:
            score = min(100.0, 65.0 + abs(curr_hist))
            return StrategyResult(
                signal=Signal.BUY, score=score,
                reason=f"MACD 金叉（DIF={curr_dif:.3f}, DEA={curr_dea:.3f}）",
            )

        if prev_dif >= prev_dea and curr_dif < curr_dea:
            score = max(0.0, 35.0 - abs(curr_hist))
            return StrategyResult(
                signal=Signal.SELL, score=score,
                reason=f"MACD 死叉（DIF={curr_dif:.3f}, DEA={curr_dea:.3f}）",
            )

        if curr_dif > curr_dea:
            return StrategyResult(signal=Signal.HOLD, score=60.0,
                                  reason=f"MACD 多头持续（柱={curr_hist:.3f}）")
        return StrategyResult(signal=Signal.HOLD, score=40.0,
                              reason=f"MACD 空头持续（柱={curr_hist:.3f}）")
