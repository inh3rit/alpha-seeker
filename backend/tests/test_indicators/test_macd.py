import pandas as pd
import pytest

from app.indicators.macd import MACDResult, calculate_macd


def test_calculate_macd_returns_result():
    prices = pd.Series([float(i) for i in range(1, 51)])
    result = calculate_macd(prices)
    assert isinstance(result, MACDResult)
    assert len(result.dif) == 50
    assert len(result.dea) == 50
    assert len(result.histogram) == 50


def test_macd_histogram_equals_2x_dif_minus_dea():
    prices = pd.Series([float(i) for i in range(1, 51)])
    result = calculate_macd(prices)
    last_idx = len(prices) - 1
    expected_hist = 2 * (result.dif.iloc[last_idx] - result.dea.iloc[last_idx])
    assert result.histogram.iloc[last_idx] == pytest.approx(expected_hist)


def test_calculate_macd_invalid_periods():
    prices = pd.Series([float(i) for i in range(1, 51)])
    with pytest.raises(ValueError):
        calculate_macd(prices, fast=0, slow=26, signal=9)
    with pytest.raises(ValueError):
        calculate_macd(prices, fast=26, slow=12, signal=9)
