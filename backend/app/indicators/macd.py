from dataclasses import dataclass

import pandas as pd


@dataclass
class MACDResult:
    """MACD 计算结果"""
    dif: pd.Series
    dea: pd.Series
    histogram: pd.Series


def calculate_macd(
    prices: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> MACDResult:
    """
    计算 MACD 指标（A 股约定）

    Args:
        prices: 收盘价序列
        fast: 快线 EMA 周期（默认 12）
        slow: 慢线 EMA 周期（默认 26）
        signal: DEA 的 EMA 周期（默认 9）
    """
    if fast <= 0 or slow <= 0 or signal <= 0:
        raise ValueError(
            f"fast/slow/signal 必须 > 0，当前 fast={fast}, slow={slow}, signal={signal}"
        )
    if fast >= slow:
        raise ValueError(f"fast({fast}) 必须 < slow({slow})")

    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    histogram = 2 * (dif - dea)

    return MACDResult(dif=dif, dea=dea, histogram=histogram)
