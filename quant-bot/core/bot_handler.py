# core/bot_handler.py
# =============================================
# Listens for Telegram commands in a background
# thread using long-polling (no extra library).
#
# Commands:
#   /start  — subscribe to signals
#   /stop   — unsubscribe from signals
#   /status — show subscriber count
# =============================================

import os
import time
import threading
import requests
from core.subscriber_store import add_subscriber, remove_subscriber, subscriber_count

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

_offset = 0


def _send(chat_id: str, text: str):
    """Sends a reply message back to a user."""
    if not TELEGRAM_BOT_TOKEN:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10,
        )
    except Exception:
        pass


def _handle_update(update: dict):
    """Processes a single incoming Telegram update."""
    message = update.get("message") or update.get("edited_message")
    if not message:
        return

    chat_id = str(message["chat"]["id"])
    text    = message.get("text", "").strip().lower()
    name    = message["chat"].get("first_name", "there")

    if text.startswith("/start"):
        if add_subscriber(chat_id):
            _send(chat_id,
                f"👋 Welcome, {name}!\n\n"
                f"✅ You're now subscribed to QuantBot signals.\n\n"
                f"You'll receive BUY and SELL alerts as they're detected "
                f"across stocks, forex, and indices.\n\n"
                f"Send /stop at any time to unsubscribe."
            )
        else:
            _send(chat_id,
                f"✅ You're already subscribed, {name}!\n"
                f"Signals will keep coming your way.\n\n"
                f"Send /stop to unsubscribe."
            )

    elif text.startswith("/stop"):
        if remove_subscriber(chat_id):
            _send(chat_id,
                f"👋 You've been unsubscribed, {name}.\n"
                f"You won't receive any more signals.\n\n"
                f"Send /start anytime to re-subscribe."
            )
        else:
            _send(chat_id,
                f"You're not currently subscribed.\n"
                f"Send /start to subscribe to signals."
            )

    elif text.startswith("/status"):
        count = subscriber_count()
        _send(chat_id, f"📊 QuantBot is running.\n👥 Subscribers: {count}")

    else:
        _send(chat_id,
            f"👋 Hi {name}! I'm QuantBot — a trading signal bot.\n\n"
            f"/start — subscribe to signals\n"
            f"/stop  — unsubscribe\n"
            f"/status — bot status"
        )


def _poll_loop():
    """
    Runs forever in a background thread, polling Telegram for
    new messages and dispatching them to _handle_update.
    """
    global _offset

    if not TELEGRAM_BOT_TOKEN:
        print("⚠️  Bot handler: no token — command handling disabled.")
        return

    print("🤖 Bot command handler started (listening for /start, /stop, /status)")

    while True:
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates",
                params={"offset": _offset, "timeout": 30},
                timeout=40,
            )
            data = response.json()

            for update in data.get("result", []):
                _offset = update["update_id"] + 1
                _handle_update(update)

        except Exception as e:
            print(f"⚠️  Bot handler poll error: {e}")
            time.sleep(5)


def start_bot_handler():
    """
    Launches the polling loop in a daemon thread.
    Call this once from main.py before the scheduler starts.
    """
    thread = threading.Thread(target=_poll_loop, daemon=True, name="BotHandler")
    thread.start()
