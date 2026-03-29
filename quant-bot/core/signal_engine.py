# core/signal_engine.py
# =============================================
# This is the decision-maker.
#
# It takes all individual indicator results,
# scores them based on weight, and outputs:
#   BUY / SELL / WAIT
#
# Think of it like a jury:
# Each indicator votes, and we tally the votes.
# =============================================

import pandas as pd
from core.indicators import (
    calculate_rsi,
    calculate_atr,
    calculate_ema,
    calculate_pivots,
    calculate_fibonacci,
    find_swing_points,
    get_monthly_closes,
)
from core.sweep_detector import detect_liquidity_sweep, is_near_level
from config.settings import (
    SIGNAL_WEIGHTS,
    MIN_SIGNAL_SCORE,
    MIN_SCORE_DIFFERENCE,
    ATR_STOP_MULTIPLIER,
    ATR_TARGET_MULTIPLIER,
    RSI_OVERSOLD,
    RSI_OVERBOUGHT,
)


def analyse_symbol(symbol: str, df_15m: pd.DataFrame, df_daily: pd.DataFrame) -> dict:
    """
    Runs the full strategy on one symbol and returns a signal.

    Args:
        symbol:   The asset name (e.g. "BTCUSDT" or "AAPL")
        df_15m:   DataFrame of 15-minute candles
        df_daily: DataFrame of daily candles

    Returns:
        A dictionary with the final signal and all reasoning
    """

    # -----------------------------------------------
    # STEP 1: CALCULATE ALL INDICATORS
    # -----------------------------------------------

    # Daily ATR — the volatility anchor for everything
    daily_atr_series = calculate_atr(df_daily, period=14)
    daily_atr = daily_atr_series.iloc[-1]

    # RSI on 15min chart
    rsi_series = calculate_rsi(df_15m, period=14)
    current_rsi = rsi_series.iloc[-2]  # Use completed candle

    # EMA 20 on 15min chart for trend direction
    ema_series = calculate_ema(df_15m, period=20)
    current_ema = ema_series.iloc[-2]
    current_close = df_15m["close"].iloc[-2]

    # Pivot points from yesterday's daily candle
    prev_day = df_daily.iloc[-2]  # Yesterday
    pivots = calculate_pivots(
        prev_high  = prev_day["high"],
        prev_low   = prev_day["low"],
        prev_close = prev_day["close"],
    )

    # Fibonacci levels from recent swing points
    swings = find_swing_points(df_15m, lookback=20)
    fib_levels = calculate_fibonacci(
        swing_high = swings["swing_high"],
        swing_low  = swings["swing_low"],
    )

    # Monthly demand zones
    monthly_closes = get_monthly_closes(df_daily)

    # -----------------------------------------------
    # STEP 2: RUN SWEEP DETECTION
    # -----------------------------------------------

    sweep = detect_liquidity_sweep(df_15m, daily_atr)

    # -----------------------------------------------
    # STEP 3: SCORE ALL CONDITIONS
    # -----------------------------------------------

    buy_score  = 0
    sell_score = 0
    conditions = []   # Log which conditions triggered

    # --- LIQUIDITY SWEEP ---
    if sweep["detected"] and sweep["confirmed"]:
        if sweep["direction"] == "BUY":
            buy_score += SIGNAL_WEIGHTS["liquidity_sweep"]
            conditions.append(f"✅ Liquidity sweep BUY ({sweep['sweep_percent']}% of ATR)")
        elif sweep["direction"] == "SELL":
            sell_score += SIGNAL_WEIGHTS["liquidity_sweep"]
            conditions.append(f"✅ Liquidity sweep SELL ({sweep['sweep_percent']}% of ATR)")
    else:
        conditions.append(f"⬜ No confirmed sweep")

    # --- RSI ---
    if current_rsi < RSI_OVERSOLD:
        buy_score += SIGNAL_WEIGHTS["rsi"]
        conditions.append(f"✅ RSI oversold ({current_rsi:.1f})")
    elif current_rsi > RSI_OVERBOUGHT:
        sell_score += SIGNAL_WEIGHTS["rsi"]
        conditions.append(f"✅ RSI overbought ({current_rsi:.1f})")
    else:
        conditions.append(f"⬜ RSI neutral ({current_rsi:.1f})")

    # --- EMA TREND ---
    if current_close > current_ema:
        buy_score += SIGNAL_WEIGHTS["trend_ema"]
        conditions.append(f"✅ Price above EMA20 (bullish trend)")
    else:
        sell_score += SIGNAL_WEIGHTS["trend_ema"]
        conditions.append(f"✅ Price below EMA20 (bearish trend)")

    # --- PIVOT LEVELS ---
    sweep_low  = sweep.get("sweep_low", current_close)
    sweep_high = sweep.get("sweep_high", current_close)

    if is_near_level(sweep_low, pivots["s1"]) or is_near_level(sweep_low, pivots["s2"]):
        buy_score += SIGNAL_WEIGHTS["pivot_level"]
        conditions.append(f"✅ Sweep near support pivot (S1={pivots['s1']}, S2={pivots['s2']})")
    elif is_near_level(sweep_high, pivots["r1"]) or is_near_level(sweep_high, pivots["r2"]):
        sell_score += SIGNAL_WEIGHTS["pivot_level"]
        conditions.append(f"✅ Sweep near resistance pivot (R1={pivots['r1']}, R2={pivots['r2']})")
    else:
        conditions.append(f"⬜ Not near pivot level")

    # --- FIBONACCI ---
    fib_buy_hit  = any(
        is_near_level(sweep_low, price)
        for name, price in fib_levels.items()
        if "retrace" in name
    )
    fib_sell_hit = any(
        is_near_level(sweep_high, price)
        for name, price in fib_levels.items()
        if "retrace" in name
    )

    if fib_buy_hit:
        buy_score += SIGNAL_WEIGHTS["fibonacci"]
        conditions.append(f"✅ Sweep at Fibonacci retracement (support)")
    elif fib_sell_hit:
        sell_score += SIGNAL_WEIGHTS["fibonacci"]
        conditions.append(f"✅ Sweep at Fibonacci retracement (resistance)")
    else:
        conditions.append(f"⬜ Not at Fibonacci level")

    # --- MONTHLY DEMAND ZONE ---
    near_monthly = any(
        is_near_level(current_close, level, tolerance_percent=1.0)
        for level in monthly_closes
        if level > 0
    )
    if near_monthly:
        buy_score += 15  # Small boost — monthly levels are context, not direction
        conditions.append(f"✅ Near monthly demand zone")
    else:
        conditions.append(f"⬜ Not near monthly demand zone")

    # --- CONFIRMATION CANDLE ---
    if sweep.get("confirmed"):
        if sweep["direction"] == "BUY":
            buy_score += SIGNAL_WEIGHTS["confirmation"]
            conditions.append(f"✅ Confirmation candle closed above sweep high")
        else:
            sell_score += SIGNAL_WEIGHTS["confirmation"]
            conditions.append(f"✅ Confirmation candle closed below sweep low")

    # -----------------------------------------------
    # STEP 4: MAKE THE DECISION
    # -----------------------------------------------

    score_diff = buy_score - sell_score
    action = "WAIT"
    confidence = 0

    if buy_score > sell_score + MIN_SCORE_DIFFERENCE and buy_score >= MIN_SIGNAL_SCORE:
        action     = "BUY"
        confidence = min(100, int(buy_score))
    elif sell_score > buy_score + MIN_SCORE_DIFFERENCE and sell_score >= MIN_SIGNAL_SCORE:
        action     = "SELL"
        confidence = min(100, int(sell_score))

    # -----------------------------------------------
    # STEP 5: CALCULATE RISK LEVELS
    # -----------------------------------------------

    entry      = current_close
    stop_loss  = None
    take_profit = None

    if action == "BUY":
        stop_loss   = round(entry - (daily_atr * ATR_STOP_MULTIPLIER),   4)
        take_profit = round(entry + (daily_atr * ATR_TARGET_MULTIPLIER), 4)
        # Use 1.618 Fib extension as target if available
        if "ext_1.618" in fib_levels:
            take_profit = fib_levels["ext_1.618"]

    elif action == "SELL":
        stop_loss   = round(entry + (daily_atr * ATR_STOP_MULTIPLIER),   4)
        take_profit = round(entry - (daily_atr * ATR_TARGET_MULTIPLIER), 4)

    # -----------------------------------------------
    # RETURN THE FULL SIGNAL
    # -----------------------------------------------

    return {
        "symbol":       symbol,
        "action":       action,
        "confidence":   confidence,
        "buy_score":    buy_score,
        "sell_score":   sell_score,
        "entry":        entry,
        "stop_loss":    stop_loss,
        "take_profit":  take_profit,
        "daily_atr":    round(daily_atr, 4),
        "current_rsi":  round(current_rsi, 2),
        "pivots":       pivots,
        "sweep":        sweep,
        "conditions":   conditions,
    }
