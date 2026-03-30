# backtest/run_backtest.py
# =============================================
# Backtests the QuantBot signal strategy on
# historical data and reports performance.
#
# Usage:
#   python backtest/run_backtest.py
#
# What it does:
#   1. Fetches historical 15min + daily data
#   2. Slides a window through the data
#   3. Runs the signal engine at each step
#   4. Simulates trades (entry, TP, SL)
#   5. Prints a full performance report
# =============================================

import sys
import os

# Allow imports from the quant-bot root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from core.signal_engine import analyse_symbol
from config.settings import (
    STOCK_SYMBOLS,
    FOREX_SYMBOLS,
    INDEX_SYMBOLS,
)


# -----------------------------------------------
# SETTINGS
# -----------------------------------------------

WINDOW_SIZE    = 100    # Candles fed to the signal engine each step
STEP_SIZE      = 1      # Move forward 1 candle per step (thorough)
DAYS_BACK_15M  = 55     # Max ~60 days for yfinance 15m data
DAYS_BACK_DAILY = 365   # 1 year of daily data for ATR, pivots

SYMBOLS_TO_TEST = STOCK_SYMBOLS + FOREX_SYMBOLS + INDEX_SYMBOLS


# -----------------------------------------------
# DATA FETCHING (extended history for backtest)
# -----------------------------------------------

def fetch_15m_history(symbol: str, days_back: int = DAYS_BACK_15M) -> pd.DataFrame:
    end   = datetime.now()
    start = end - timedelta(days=days_back)
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start, end=end, interval="15m")
    if df.empty:
        return pd.DataFrame()
    df.columns = [c.lower() for c in df.columns]
    df = df[["open", "high", "low", "close", "volume"]].dropna()
    return df


def fetch_daily_history(symbol: str, days_back: int = DAYS_BACK_DAILY) -> pd.DataFrame:
    end   = datetime.now()
    start = end - timedelta(days=days_back)
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start, end=end, interval="1d")
    if df.empty:
        return pd.DataFrame()
    df.columns = [c.lower() for c in df.columns]
    df = df[["open", "high", "low", "close", "volume"]].dropna()
    return df


# -----------------------------------------------
# TRADE SIMULATION
# -----------------------------------------------

def simulate_trade(df_15m: pd.DataFrame, entry_idx: int, signal: dict) -> dict:
    """
    Simulates a trade from entry_idx forward.
    Checks subsequent candles to see if TP or SL is hit first.

    Returns a dict with: result ('WIN'/'LOSS'/'OPEN'), pnl_pct, bars_held
    """
    action     = signal["action"]
    entry      = signal["entry"]
    stop_loss  = signal["stop_loss"]
    take_profit = signal["take_profit"]

    if entry == 0 or stop_loss is None or take_profit is None:
        return {"result": "SKIP", "pnl_pct": 0, "bars_held": 0}

    risk   = abs(entry - stop_loss)
    reward = abs(take_profit - entry)

    if risk == 0:
        return {"result": "SKIP", "pnl_pct": 0, "bars_held": 0}

    # Walk forward from the candle after entry
    future = df_15m.iloc[entry_idx + 1:]

    for bars_held, (_, candle) in enumerate(future.iterrows(), start=1):
        if action == "BUY":
            if candle["low"] <= stop_loss:
                pnl_pct = -(risk / entry) * 100
                return {"result": "LOSS", "pnl_pct": round(pnl_pct, 3), "bars_held": bars_held}
            if candle["high"] >= take_profit:
                pnl_pct = (reward / entry) * 100
                return {"result": "WIN", "pnl_pct": round(pnl_pct, 3), "bars_held": bars_held}
        elif action == "SELL":
            if candle["high"] >= stop_loss:
                pnl_pct = -(risk / entry) * 100
                return {"result": "LOSS", "pnl_pct": round(pnl_pct, 3), "bars_held": bars_held}
            if candle["low"] <= take_profit:
                pnl_pct = (reward / entry) * 100
                return {"result": "WIN", "pnl_pct": round(pnl_pct, 3), "bars_held": bars_held}

    # Trade never closed — mark as open
    last_close = df_15m["close"].iloc[-1]
    if action == "BUY":
        pnl_pct = ((last_close - entry) / entry) * 100
    else:
        pnl_pct = ((entry - last_close) / entry) * 100

    return {"result": "OPEN", "pnl_pct": round(pnl_pct, 3), "bars_held": len(future)}


# -----------------------------------------------
# BACKTEST ONE SYMBOL
# -----------------------------------------------

def backtest_symbol(symbol: str) -> list:
    """
    Runs the full backtest for one symbol.
    Returns a list of trade result dicts.
    """
    print(f"\n{'='*55}")
    print(f"  Backtesting {symbol}...")
    print(f"{'='*55}")

    df_15m  = fetch_15m_history(symbol)
    df_daily = fetch_daily_history(symbol)

    if df_15m.empty or df_daily.empty:
        print(f"  ⚠️  No data for {symbol} — skipping.")
        return []

    print(f"  15m candles : {len(df_15m)}")
    print(f"  Daily candles: {len(df_daily)}")

    trades      = []
    in_trade    = False
    trade_end_i = 0

    max_i = len(df_15m) - WINDOW_SIZE
    if max_i <= 0:
        print(f"  ⚠️  Not enough candles to backtest (need >{WINDOW_SIZE}).")
        return []

    for i in range(0, max_i, STEP_SIZE):

        # Skip steps while we're still in a trade
        if in_trade and i < trade_end_i:
            continue

        window_15m = df_15m.iloc[i : i + WINDOW_SIZE].copy()

        # Align daily data to the window's end date
        window_end  = window_15m.index[-1]
        window_daily = df_daily[df_daily.index <= window_end].copy()

        if len(window_daily) < 15:
            continue

        try:
            result = analyse_symbol(symbol, window_15m, window_daily)
        except Exception as e:
            continue

        if result["action"] == "WAIT":
            continue

        # Signal fired — simulate the trade
        entry_idx = i + WINDOW_SIZE - 1   # Index in full df_15m
        trade = simulate_trade(df_15m, entry_idx, result)
        trade["symbol"]     = symbol
        trade["action"]     = result["action"]
        trade["confidence"] = result["confidence"]
        trade["entry"]      = result["entry"]
        trade["stop_loss"]  = result["stop_loss"]
        trade["take_profit"] = result["take_profit"]
        trade["candle_time"] = str(window_15m.index[-1])

        trades.append(trade)
        print(
            f"  {'🟢' if result['action'] == 'BUY' else '🔴'} "
            f"{result['action']} @ {result['entry']:.4f}  →  "
            f"{'✅ WIN' if trade['result'] == 'WIN' else '❌ LOSS' if trade['result'] == 'LOSS' else '⬜ OPEN'}  "
            f"({trade['pnl_pct']:+.2f}%)"
        )

        # Don't enter another trade until this one closes
        in_trade    = True
        trade_end_i = entry_idx + trade["bars_held"] + 1
        if trade["result"] in ("WIN", "LOSS"):
            in_trade = False

    return trades


# -----------------------------------------------
# PERFORMANCE REPORT
# -----------------------------------------------

def print_report(all_trades: list):
    if not all_trades:
        print("\n⚠️  No trades were generated during the backtest period.")
        return

    df = pd.DataFrame(all_trades)

    closed = df[df["result"].isin(["WIN", "LOSS"])]
    wins   = df[df["result"] == "WIN"]
    losses = df[df["result"] == "LOSS"]
    open_  = df[df["result"] == "OPEN"]

    total_closed  = len(closed)
    win_rate      = (len(wins) / total_closed * 100) if total_closed > 0 else 0
    avg_win       = wins["pnl_pct"].mean()   if len(wins)   > 0 else 0
    avg_loss      = losses["pnl_pct"].mean() if len(losses) > 0 else 0
    total_pnl     = df["pnl_pct"].sum()
    avg_bars      = closed["bars_held"].mean() if total_closed > 0 else 0
    rr_ratio      = abs(avg_win / avg_loss) if avg_loss != 0 else 0

    print("\n" + "="*55)
    print("  BACKTEST RESULTS")
    print("="*55)
    print(f"  Period         : Last {DAYS_BACK_15M} days (15m candles)")
    print(f"  Symbols tested : {df['symbol'].nunique()}")
    print(f"  Total signals  : {len(df)}")
    print(f"  Closed trades  : {total_closed}  (Wins: {len(wins)}  Losses: {len(losses)})")
    print(f"  Open trades    : {len(open_)}")
    print(f"  Win rate       : {win_rate:.1f}%")
    print(f"  Avg win        : {avg_win:+.2f}%")
    print(f"  Avg loss       : {avg_loss:+.2f}%")
    print(f"  Risk/Reward    : {rr_ratio:.2f}x")
    print(f"  Avg bars held  : {avg_bars:.0f} candles (~{avg_bars * 15 / 60:.1f} hrs)")
    print(f"  Total P&L      : {total_pnl:+.2f}%")
    print("="*55)

    print("\n  Results by symbol:")
    by_symbol = df.groupby("symbol").agg(
        trades   = ("result", "count"),
        wins     = ("result", lambda x: (x == "WIN").sum()),
        losses   = ("result", lambda x: (x == "LOSS").sum()),
        total_pnl = ("pnl_pct", "sum"),
    ).reset_index()
    by_symbol["win_rate"] = (by_symbol["wins"] / by_symbol["trades"] * 100).round(1)

    for _, row in by_symbol.iterrows():
        print(
            f"  {row['symbol']:<12}  "
            f"Trades: {int(row['trades']):<3}  "
            f"Wins: {int(row['wins']):<3}  "
            f"Win%: {row['win_rate']:.0f}%  "
            f"P&L: {row['total_pnl']:+.2f}%"
        )

    print()


# -----------------------------------------------
# MAIN
# -----------------------------------------------

if __name__ == "__main__":
    print("🔬 QuantBot Backtester")
    print(f"   Symbols : {', '.join(SYMBOLS_TO_TEST)}")
    print(f"   Window  : {WINDOW_SIZE} candles")
    print(f"   Period  : Last {DAYS_BACK_15M} days\n")

    all_trades = []

    for symbol in SYMBOLS_TO_TEST:
        trades = backtest_symbol(symbol)
        all_trades.extend(trades)

    print_report(all_trades)
