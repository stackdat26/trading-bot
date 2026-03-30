# core/signal_store.py
# =============================================
# In-memory store for recent signals.
# Shared between the analysis loop and the
# web dashboard so both can read/write signals
# within the same process.
# =============================================

import threading
from datetime import datetime

_lock    = threading.Lock()
_signals = []          # List of signal dicts, newest first
MAX_SIGNALS = 200      # Keep the last 200 signals in memory

# Bot start time for uptime display
START_TIME = datetime.now()


def add_signal(result: dict):
    """
    Stores a signal result in the in-memory list.
    Called by main.py whenever a BUY or SELL fires.
    """
    with _lock:
        entry = {
            "symbol":      result["symbol"],
            "action":      result["action"],
            "confidence":  result["confidence"],
            "entry":       result["entry"],
            "stop_loss":   result["stop_loss"],
            "take_profit": result["take_profit"],
            "rsi":         result["current_rsi"],
            "buy_score":   result["buy_score"],
            "sell_score":  result["sell_score"],
            "conditions":  result.get("conditions", []),
            "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        _signals.insert(0, entry)
        if len(_signals) > MAX_SIGNALS:
            _signals.pop()


def get_signals(limit: int = 50) -> list:
    """Returns the most recent signals."""
    with _lock:
        return _signals[:limit]


def get_stats() -> dict:
    """Returns summary stats across all stored signals."""
    with _lock:
        total = len(_signals)
        buys  = sum(1 for s in _signals if s["action"] == "BUY")
        sells = sum(1 for s in _signals if s["action"] == "SELL")

        uptime_secs = int((datetime.now() - START_TIME).total_seconds())
        hours, rem  = divmod(uptime_secs, 3600)
        mins, secs  = divmod(rem, 60)
        uptime_str  = f"{hours}h {mins}m {secs}s"

        return {
            "total_signals": total,
            "buy_signals":   buys,
            "sell_signals":  sells,
            "uptime":        uptime_str,
            "started_at":    START_TIME.strftime("%Y-%m-%d %H:%M:%S"),
        }


def add_webhook_signal(data: dict):
    """
    Stores a signal received from a TradingView webhook.
    The data dict comes straight from the webhook POST body.
    """
    with _lock:
        entry = {
            "symbol":      data.get("symbol", "UNKNOWN"),
            "action":      data.get("action", "BUY").upper(),
            "confidence":  data.get("confidence", 100),
            "entry":       float(data.get("price", 0)),
            "stop_loss":   float(data.get("stop_loss", 0)),
            "take_profit": float(data.get("take_profit", 0)),
            "rsi":         float(data.get("rsi", 0)),
            "buy_score":   0,
            "sell_score":  0,
            "conditions":  ["📡 Signal received from TradingView webhook"],
            "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source":      "TradingView",
        }
        _signals.insert(0, entry)
        if len(_signals) > MAX_SIGNALS:
            _signals.pop()
        return entry
