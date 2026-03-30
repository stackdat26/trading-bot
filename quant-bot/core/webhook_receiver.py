# core/webhook_receiver.py
# =============================================
# TradingView Webhook Receiver
#
# TradingView sends a POST request to your URL
# when an alert fires. This receives it, stores
# the signal, and sends it to Telegram.
#
# Webhook URL (when on TradingView Pro+):
#   https://YOUR-REPLIT-URL/webhook
#
# TradingView alert message format (JSON):
#   {
#     "symbol":      "{{ticker}}",
#     "action":      "BUY",
#     "price":       {{close}},
#     "stop_loss":   0,
#     "take_profit": 0,
#     "rsi":         0
#   }
# =============================================

from flask import Blueprint, request, jsonify
from core.signal_store import add_webhook_signal
from core.telegram_alerts import broadcast

webhook_bp = Blueprint("webhook", __name__)


@webhook_bp.route("/webhook", methods=["POST"])
def receive_webhook():
    """
    Receives a TradingView alert and forwards it as a signal.
    """
    try:
        data = request.get_json(force=True, silent=True) or {}

        if not data:
            return jsonify({"error": "No JSON body received"}), 400

        symbol = data.get("symbol", "UNKNOWN")
        action = data.get("action", "").upper()

        if action not in ("BUY", "SELL"):
            return jsonify({"error": f"Invalid action: {action}. Must be BUY or SELL"}), 400

        # Store the signal
        signal = add_webhook_signal(data)

        # Send to all Telegram subscribers
        emoji = "🟢" if action == "BUY" else "🔴"
        price      = signal["entry"]
        stop_loss  = signal["stop_loss"]
        take_profit = signal["take_profit"]

        message = (
            f"{emoji} <b>TRADINGVIEW ALERT: {action} {symbol}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>Price:</b>       {price:.5f}\n"
        )
        if stop_loss:
            message += f"<b>Stop Loss:</b>   {stop_loss:.5f}\n"
        if take_profit:
            message += f"<b>Take Profit:</b> {take_profit:.5f}\n"
        message += f"📡 Source: TradingView webhook"

        sent = broadcast(message)

        print(f"📡 Webhook received: {action} {symbol} — alerted {sent} subscriber(s)")

        return jsonify({
            "status":       "ok",
            "signal":       action,
            "symbol":       symbol,
            "subscribers_alerted": sent,
        }), 200

    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return jsonify({"error": str(e)}), 500
