# core/telegram_alerts.py
# =============================================
# Sends trading signals to Telegram.
# Reads TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
# from environment variables (Replit Secrets).
# =============================================

import os
import requests


TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID")

TELEGRAM_ENABLED = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)


def send_telegram_message(text: str) -> bool:
    """
    Sends a plain text message to the configured Telegram chat.

    Returns True if successful, False otherwise.
    """
    if not TELEGRAM_ENABLED:
        print("⚠️  Telegram not configured — skipping alert.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       text,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Telegram alert failed: {e}")
        return False


def send_signal_alert(result: dict) -> bool:
    """
    Formats a signal result dict and sends it to Telegram.

    Only sends for BUY or SELL signals, not WAIT.
    """
    action = result.get("action")
    if action == "WAIT":
        return False

    symbol     = result["symbol"]
    confidence = result["confidence"]
    entry      = result["entry"]
    stop_loss  = result["stop_loss"]
    take_profit = result["take_profit"]
    rsi        = result["current_rsi"]
    buy_score  = result["buy_score"]
    sell_score = result["sell_score"]
    conditions = result.get("conditions", [])

    emoji = "🟢" if action == "BUY" else "🔴"

    conditions_text = "\n".join(f"  {c}" for c in conditions)

    message = (
        f"{emoji} <b>SIGNAL: {action} {symbol}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Confidence:</b> {confidence}%\n"
        f"<b>Entry:</b>      {entry:.5f}\n"
        f"<b>Stop Loss:</b>  {stop_loss:.5f}\n"
        f"<b>Take Profit:</b> {take_profit:.5f}\n"
        f"<b>RSI:</b>        {rsi:.1f}\n"
        f"<b>Buy Score:</b>  {buy_score}  |  <b>Sell Score:</b> {sell_score}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Conditions:</b>\n{conditions_text}"
    )

    return send_telegram_message(message)
