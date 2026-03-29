# tests/test_indicators.py
# =============================================
# Tests to verify your maths is correct.
# Run with: python -m pytest tests/
# =============================================

import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.indicators import calculate_rsi, calculate_atr, calculate_ema, calculate_pivots, calculate_fibonacci


# --- Sample data for testing ---
def make_sample_df():
    """Creates a simple DataFrame for testing"""
    closes = [45000, 46000, 47500, 49000, 48000, 50000, 51000, 52000, 53000, 54000,
              53500, 52000, 51000, 50500, 49000, 48500, 47000, 46500, 45500, 45000]
    highs  = [c * 1.01 for c in closes]
    lows   = [c * 0.99 for c in closes]
    opens  = [c * 0.995 for c in closes]

    return pd.DataFrame({
        "open":   opens,
        "high":   highs,
        "low":    lows,
        "close":  closes,
        "volume": [1000] * len(closes),
    })


def test_rsi_range():
    """RSI should always be between 0 and 100"""
    df = make_sample_df()
    rsi = calculate_rsi(df)
    valid = rsi.dropna()
    assert (valid >= 0).all() and (valid <= 100).all(), "RSI out of range!"
    print("✅ RSI range test passed")


def test_atr_positive():
    """ATR should always be a positive number"""
    df = make_sample_df()
    atr = calculate_atr(df)
    valid = atr.dropna()
    assert (valid > 0).all(), "ATR has negative values!"
    print("✅ ATR positive test passed")


def test_ema_follows_price():
    """EMA should be between recent low and high"""
    df = make_sample_df()
    ema = calculate_ema(df, period=5)
    last_ema = ema.iloc[-1]
    assert df["low"].min() < last_ema < df["high"].max(), "EMA out of price range!"
    print("✅ EMA range test passed")


def test_pivots():
    """Pivot R1 should be above PP, S1 should be below PP"""
    pivots = calculate_pivots(prev_high=51000, prev_low=49000, prev_close=50000)
    assert pivots["r1"] > pivots["pp"], "R1 should be above PP"
    assert pivots["s1"] < pivots["pp"], "S1 should be below PP"
    assert pivots["r2"] > pivots["r1"], "R2 should be above R1"
    assert pivots["s2"] < pivots["s1"], "S2 should be below S1"
    print("✅ Pivot levels test passed")


def test_fibonacci():
    """Fib 0.618 retracement should be below swing high, above swing low"""
    fibs = calculate_fibonacci(swing_high=50000, swing_low=40000)
    assert fibs["retrace_0.618"] < 50000, "0.618 retracement should be below swing high"
    assert fibs["retrace_0.618"] > 40000, "0.618 retracement should be above swing low"
    assert fibs["ext_1.618"] > 50000, "1.618 extension should be above swing high"
    print("✅ Fibonacci test passed")


if __name__ == "__main__":
    print("\n🧪 Running indicator tests...\n")
    test_rsi_range()
    test_atr_positive()
    test_ema_follows_price()
    test_pivots()
    test_fibonacci()
    print("\n✅ All tests passed!\n")
