import pandas as pd


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    计算相对强弱指数（RSI）- 使用 Wilder 平滑

    Args:
        prices: 收盘价序列
        period: 周期（默认 14）

    Returns:
        RSI 序列，取值范围 [0, 100]
    """
    if period <= 0:
        raise ValueError(f"period 必须 > 0，当前 period={period}")

    delta = prices.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)

    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()

    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.where(avg_loss != 0, 100.0)
    rsi = rsi.where(avg_gain != 0, 0.0)
    return rsi
