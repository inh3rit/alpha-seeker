import pandas as pd
import pytest

from app.indicators.rsi import calculate_rsi


def test_calculate_rsi_returns_series():
    prices = pd.Series([float(i) for i in range(1, 51)])
    rsi = calculate_rsi(prices, period=14)
    assert isinstance(rsi, pd.Series)
    assert len(rsi) == 50


def test_rsi_values_in_0_to_100_range():
    prices = pd.Series([100 + (i % 7) - 3 for i in range(100)], dtype=float)
    rsi = calculate_rsi(prices, period=14)
    valid = rsi.dropna()
    assert (valid >= 0).all()
    assert (valid <= 100).all()


def test_rsi_all_rising_prices_gives_high_rsi():
    prices = pd.Series([float(i) for i in range(1, 51)])
    rsi = calculate_rsi(prices, period=14)
    assert rsi.iloc[-1] == pytest.approx(100.0, abs=0.1)


def test_rsi_all_falling_prices_gives_low_rsi():
    prices = pd.Series([float(50 - i) for i in range(50)])
    rsi = calculate_rsi(prices, period=14)
    assert rsi.iloc[-1] == pytest.approx(0.0, abs=0.1)


def test_rsi_invalid_period():
    prices = pd.Series([float(i) for i in range(1, 20)])
    with pytest.raises(ValueError):
        calculate_rsi(prices, period=0)
