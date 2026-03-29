# core/sweep_detector.py
# =============================================
# This is the heart of the bot.
#
# Your formula:
#   Sweep % = (Candle High - Candle Low) / Daily ATR × 100
#
# If Sweep % > 20 → potential institutional move
# Wait for next candle to confirm direction
# =============================================

import pandas as pd


def detect_liquidity_sweep(df: pd.DataFrame, daily_atr: float, threshold: float = 20.0) -> dict:
    """
    Detects a liquidity sweep on the most recently COMPLETED candle.

    A sweep happens when a 15-minute candle's range (high - low) is
    unusually large relative to the daily ATR — suggesting institutions
    just forced through a lot of retail stop losses.

    We then check the NEXT candle for confirmation.

    Args:
        df:          DataFrame of 15min candles (needs high, low, open, close)
        daily_atr:   The current daily ATR value (single number)
        threshold:   Minimum sweep % to count (default 20%)

    Returns:
        Dictionary with sweep details
    """

    # We need at least 2 completed candles to check sweep + confirmation
    if len(df) < 3:
        return {"detected": False, "reason": "Not enough candles"}

    # The candle we're checking for a sweep (second to last = most recently completed)
    sweep_candle = df.iloc[-2]

    # The candle after it (the confirmation candle — still forming or just closed)
    confirm_candle = df.iloc[-1]

    # --- YOUR FORMULA ---
    candle_range    = sweep_candle["high"] - sweep_candle["low"]
    sweep_percent   = (candle_range / daily_atr) * 100

    # --- Did it exceed the threshold? ---
    if sweep_percent < threshold:
        return {
            "detected":       False,
            "sweep_percent":  round(sweep_percent, 2),
            "threshold":      threshold,
            "reason":         f"Sweep only {sweep_percent:.1f}% of ATR (need >{threshold}%)"
        }

    # --- What direction was the sweep candle? ---
    is_bullish_candle = sweep_candle["close"] > sweep_candle["open"]

    # --- Confirmation logic ---
    # Bullish sweep: price swept down (took out stops below), then reversed up
    # Confirmation = next candle closes ABOVE the sweep candle's high
    bullish_confirmed = (
        is_bullish_candle and
        confirm_candle["close"] > sweep_candle["high"]
    )

    # Bearish sweep: price swept up (took out stops above), then reversed down
    # Confirmation = next candle closes BELOW the sweep candle's low
    bearish_confirmed = (
        not is_bullish_candle and
        confirm_candle["close"] < sweep_candle["low"]
    )

    direction = None
    confirmed = False

    if bullish_confirmed:
        direction = "BUY"
        confirmed = True
    elif bearish_confirmed:
        direction = "SELL"
        confirmed = True

    return {
        "detected":         True,
        "confirmed":        confirmed,
        "direction":        direction,
        "sweep_percent":    round(sweep_percent, 2),
        "candle_range":     round(candle_range, 4),
        "daily_atr":        round(daily_atr, 4),
        "sweep_high":       sweep_candle["high"],
        "sweep_low":        sweep_candle["low"],
        "sweep_close":      sweep_candle["close"],
        "confirm_close":    confirm_candle["close"],
    }


def is_near_level(price: float, level: float, tolerance_percent: float = 0.5) -> bool:
    """
    Checks if a price is within a % tolerance of a key level.
    Used to check if sweep is near a pivot or Fibonacci level.

    Args:
        price:             The current price
        level:             The key level to check against
        tolerance_percent: How close counts as "near" (default 0.5%)

    Returns:
        True if within tolerance, False otherwise
    """
    if level == 0:
        return False

    distance_percent = abs(price - level) / level * 100
    return distance_percent <= tolerance_percent
