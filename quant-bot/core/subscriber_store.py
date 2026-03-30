# core/subscriber_store.py
# =============================================
# Manages the list of Telegram subscribers.
# Stored in data/subscribers.json so it
# survives restarts.
# =============================================

import json
import os
import threading

SUBSCRIBERS_FILE = "data/subscribers.json"
_lock = threading.Lock()


def _load() -> list:
    if not os.path.exists(SUBSCRIBERS_FILE):
        return []
    try:
        with open(SUBSCRIBERS_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def _save(subscribers: list):
    os.makedirs("data", exist_ok=True)
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(subscribers, f, indent=2)


def add_subscriber(chat_id: str) -> bool:
    """
    Adds a chat_id to the subscriber list.
    Returns True if newly added, False if already subscribed.
    """
    with _lock:
        subs = _load()
        chat_id = str(chat_id)
        if chat_id not in subs:
            subs.append(chat_id)
            _save(subs)
            return True
        return False


def remove_subscriber(chat_id: str) -> bool:
    """
    Removes a chat_id from the subscriber list.
    Returns True if removed, False if wasn't subscribed.
    """
    with _lock:
        subs = _load()
        chat_id = str(chat_id)
        if chat_id in subs:
            subs.remove(chat_id)
            _save(subs)
            return True
        return False


def get_subscribers() -> list:
    """Returns the full list of subscriber chat IDs."""
    with _lock:
        return _load()


def subscriber_count() -> int:
    """Returns how many people are currently subscribed."""
    return len(get_subscribers())
