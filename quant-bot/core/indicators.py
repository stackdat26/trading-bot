# core/indicators.py
# =============================================
# All indicator calculations live here.
# Each function takes a DataFrame of price data
# and returns the calculated values.
#
# A DataFrame is basically a table with columns:
# open, high, low, close, volume
# =============================================

import pandas as pd
import numpy as np


# -----------------------------------------------
# RSI — Relative Strength Index
# Measures momentum. Range: 0 to 100.
# Below 30 = oversold (potential buy)
# Above 70 = overbought (potential sell)
# -----------------------------------------------

def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculates RSI for each row in the DataFrame.

    Args:
        df:     DataFrame with a 'close' column
        period: Number of candles to look back (default 14)

    Returns:
        A Series of RSI values (one per row)
    """
    # Step 1: Find the change between each close price
    delta = df["close"].diff()

    # Step 2: Separate gains (up days) from losses (down days)
    gains = delta.where(delta > 0, 0)   # Keep positive changes, replace negatives with 0
    losses = -delta.where(delta < 0, 0) # Keep negative changes (made positive), replace with 0

    # Step 3: Average the gains and losses over the period
    avg_gain = gains.rolling(window=period).mean()
    avg_loss = losses.rolling(window=period).mean()

    # Step 4: RS = average gain / average loss
    rs = avg_gain / avg_loss

    # Step 5: RSI formula
    rsi = 100 - (100 / (1 + rs))

    return rsi


# -----------------------------------------------
# ATR — Average True Range
# Measures volatility. Tells you how much price
# typically moves in a given period.
# -----------------------------------------------

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculates ATR for each row in the DataFrame.

    Args:
        df:     DataFrame with 'high', 'low', 'close' columns
        period: Number of candles to average over (default 14)

    Returns:
        A Series of ATR values
    """
    high  = df["high"]
    low   = df["low"]
    close = df["close"]

    # True Range is the LARGEST of these three:
    tr1 = high - low                        # Current candle range
    tr2 = abs(high - close.shift(1))        # Distance from prev close to current high
    tr3 = abs(low  - close.shift(1))        # Distance from prev close to current low

    # Take the max of the three for each row
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # ATR = rolling average of true range
    atr = true_range.rolling(window=period).mean()

    return atr


# -----------------------------------------------
# EMA — Exponential Moving Average
# Follows the trend. Recent prices weighted more.
# Formula: EMA = Price(t) × k + EMA(yesterday) × (1 - k)
# where k = 2 / (N + 1)
# -----------------------------------------------

def calculate_ema(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """
    Calculates EMA using closing prices.

    Args:
        df:     DataFrame with a 'close' column
        period: Number of days (e.g. 20 for EMA20)

    Returns:
        A Series of EMA values
    """
    ema = df["close"].ewm(span=period, adjust=False).mean()
    return ema


# -----------------------------------------------
# PIVOT POINTS — Daily Support & Resistance
# Calculated from previous day's High, Low, Close.
# R1, R2 = resistance levels above price
# S1, S2 = support levels below price
# -----------------------------------------------

def calculate_pivots(prev_high: float, prev_low: float, prev_close: float) -> dict:
    """
    Calculates daily pivot points from the previous day's candle.

    Args:
        prev_high:  Previous day's high price
        prev_low:   Previous day's low price
        prev_close: Previous day's close price

    Returns:
        Dictionary with PP, R1, R2, S1, S2
    """
    # Pivot Point = average of High, Low, Close
    pp = (prev_high + prev_low + prev_close) / 3

    # Resistance levels (above pivot)
    r1 = (2 * pp) - prev_low
    r2 = pp + (prev_high - prev_low)

    # Support levels (below pivot)
    s1 = (2 * pp) - prev_high
    s2 = pp - (prev_high - prev_low)

    return {
        "pp": round(pp, 4),
        "r1": round(r1, 4),
        "r2": round(r2, 4),
        "s1": round(s1, 4),
        "s2": round(s2, 4),
    }


# -----------------------------------------------
# FIBONACCI LEVELS
# Based on a recent swing high and swing low.
# Retracements: where price might pull back to
# Extensions: where price might target after
# -----------------------------------------------

def calculate_fibonacci(swing_high: float, swing_low: float) -> dict:
    """
    Calculates Fibonacci retracement and extension levels.

    Args:
        swing_high: Recent high (the top of the move)
        swing_low:  Recent low (the bottom of the move)

    Returns:
        Dictionary of all fib levels with their prices
    """
    diff = swing_high - swing_low

    levels = {
        # Retracements — between swing_low and swing_high
        "retrace_0.236": round(swing_high - (diff * 0.236), 4),
        "retrace_0.382": round(swing_high - (diff * 0.382), 4),
        "retrace_0.500": round(swing_high - (diff * 0.500), 4),
        "retrace_0.618": round(swing_high - (diff * 0.618), 4),
        "retrace_0.786": round(swing_high - (diff * 0.786), 4),

        # Extensions — beyond swing_high (price targets)
        "ext_1.272": round(swing_high + (diff * 0.272), 4),
        "ext_1.414": round(swing_high + (diff * 0.414), 4),
        "ext_1.618": round(swing_high + (diff * 0.618), 4),
        "ext_2.000": round(swing_high + (diff * 1.000), 4),
        "ext_2.618": round(swing_high + (diff * 1.618), 4),
    }

    return levels


def find_swing_points(df: pd.DataFrame, lookback: int = 20) -> dict:
    """
    Finds the most recent swing high and swing low.
    Used as inputs to calculate_fibonacci().

    Args:
        df:       DataFrame with 'high' and 'low' columns
        lookback: How many candles to look back

    Returns:
        Dictionary with 'swing_high' and 'swing_low'
    """
    recent = df.tail(lookback)

    swing_high = recent["high"].max()
    swing_low  = recent["low"].min()

    return {
        "swing_high": swing_high,
        "swing_low":  swing_low,
    }


# -----------------------------------------------
# MONTHLY DEMAND ZONES
# Based on previous monthly candle closes.
# Monthly close = where value was accepted.
# -----------------------------------------------

def get_monthly_closes(df_daily: pd.DataFrame) -> list:
    """
    Gets the last 6 monthly candle closes from daily data.
    These are the key demand/supply zones.

    Args:
        df_daily: Daily DataFrame with 'close' column and datetime index

    Returns:
        List of monthly close prices (most recent last)
    """
    # Make sure index is datetime
    df_daily = df_daily.copy()
    df_daily.index = pd.to_datetime(df_daily.index)

    # Resample to monthly and get the close (last trading day of month)
    monthly = df_daily["close"].resample("ME").last()

    # Return last 6 months as a list
    return monthly.tail(6).tolist()
