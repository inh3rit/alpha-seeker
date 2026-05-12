import pandas as pd


def calculate_ma(prices: pd.Series, period: int) -> pd.Series:
    """
    计算简单移动平均（SMA）

    Args:
        prices: 收盘价序列
        period: 周期（如 5、20、60）

    Returns:
        与输入等长的均线序列，前 period-1 个值为 NaN
    """
    if period <= 0:
        raise ValueError(f"period 必须 > 0，当前 period={period}")
    return prices.rolling(window=period, min_periods=period).mean()
