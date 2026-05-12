import pandas as pd
import pytest

from app.indicators.ma import calculate_ma


def test_calculate_ma_returns_series():
    prices = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0])
    ma3 = calculate_ma(prices, period=3)
    assert isinstance(ma3, pd.Series)
    assert len(ma3) == 5


def test_calculate_ma_correct_values():
    prices = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0])
    ma3 = calculate_ma(prices, period=3)
    assert pd.isna(ma3.iloc[0])
    assert pd.isna(ma3.iloc[1])
    assert ma3.iloc[2] == pytest.approx(11.0)
    assert ma3.iloc[3] == pytest.approx(12.0)
    assert ma3.iloc[4] == pytest.approx(13.0)


def test_calculate_ma_raises_on_invalid_period():
    prices = pd.Series([10.0, 11.0, 12.0])
    with pytest.raises(ValueError):
        calculate_ma(prices, period=0)
    with pytest.raises(ValueError):
        calculate_ma(prices, period=-1)


def test_calculate_ma_on_empty_series():
    result = calculate_ma(pd.Series([], dtype=float), period=3)
    assert len(result) == 0
