# core/telegram_alerts.py
# =============================================
# Sends trading signals to all Telegram
# subscribers. Reads TELEGRAM_BOT_TOKEN from
# environment variables (Replit Secrets).
#
# Subscribers are managed in data/subscribers.json
# via /start and /stop commands.
# =============================================

import os
import requests
from core.subscriber_store import get_subscribers, add_subscriber

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID")  # Owner's ID — auto-subscribed

TELEGRAM_ENABLED = bool(TELEGRAM_BOT_TOKEN)


def ensure_owner_subscribed():
    """
    Auto-subscribes the owner (TELEGRAM_CHAT_ID) on startup
    so they always receive signals even before anyone sends /start.
    """
    if TELEGRAM_CHAT_ID:
        added = add_subscriber(TELEGRAM_CHAT_ID)
        if added:
            print(f"   ℹ️  Owner chat ID auto-subscribed.")


def _send_to(chat_id: str, text: str) -> bool:
    """Sends a message to a single chat ID."""
    if not TELEGRAM_BOT_TOKEN:
        return False
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"   ⚠️  Failed to send to {chat_id}: {e}")
        return False


def broadcast(text: str) -> int:
    """
    Sends a message to all subscribers.
    Returns the number of successful sends.
    """
    if not TELEGRAM_ENABLED:
        print("⚠️  Telegram not configured — skipping broadcast.")
        return 0

    subscribers = get_subscribers()
    if not subscribers:
        print("   ⚠️  No subscribers yet — nobody to alert.")
        return 0

    sent = sum(_send_to(chat_id, text) for chat_id in subscribers)
    return sent


def send_telegram(text: str, token: str = None, chat_id: str = None) -> bool:
    """
    Convenience test function.
    If chat_id is given, sends directly. Otherwise broadcasts to all subscribers.
    """
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10).raise_for_status()
            print("✅ Telegram message sent.")
            return True
        except Exception as e:
            print(f"❌ Telegram alert failed: {e}")
            return False

    count = broadcast(text)
    print(f"✅ Telegram message sent to {count} subscriber(s).")
    return count > 0


def send_signal_alert(result: dict) -> int:
    """
    Formats a BUY/SELL signal and broadcasts it to all subscribers.
    Returns the number of subscribers successfully alerted.
    """
    action = result.get("action")
    if action == "WAIT":
        return 0

    symbol      = result["symbol"]
    confidence  = result["confidence"]
    entry       = result["entry"]
    stop_loss   = result["stop_loss"]
    take_profit = result["take_profit"]
    rsi         = result["current_rsi"]
    buy_score   = result["buy_score"]
    sell_score  = result["sell_score"]
    conditions  = result.get("conditions", [])

    emoji           = "🟢" if action == "BUY" else "🔴"
    conditions_text = "\n".join(f"  {c}" for c in conditions)

    message = (
        f"{emoji} <b>SIGNAL: {action} {symbol}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Confidence:</b> {confidence}%\n"
        f"<b>Entry:</b>       {entry:.5f}\n"
        f"<b>Stop Loss:</b>   {stop_loss:.5f}\n"
        f"<b>Take Profit:</b> {take_profit:.5f}\n"
        f"<b>RSI:</b>         {rsi:.1f}\n"
        f"<b>Buy Score:</b>   {buy_score}  |  <b>Sell Score:</b> {sell_score}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Conditions:</b>\n{conditions_text}"
    )

    return broadcast(message)
