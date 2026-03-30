# main.py
# =============================================
# Run this file to start the bot.
#
# Usage:
#   python main.py
#
# What it does:
#   1. Loads your symbols from config/settings.py
#   2. Fetches data for each symbol
#   3. Runs the signal engine
#   4. Prints results and logs them to logs/signals.log
#   5. Waits 15 minutes and repeats
# =============================================

import time
import schedule
import logging
import os
from datetime import datetime

from config.settings import (
    CRYPTO_SYMBOLS,
    STOCK_SYMBOLS,
    FOREX_SYMBOLS,
    INDEX_SYMBOLS,
)
from core.data_feed import get_data
from core.signal_engine import analyse_symbol
from core.telegram_alerts import send_telegram, format_signal_message
from core.webhook_receiver import create_webhook_app, start_webhook_server, format_tradingview_signal_message
from dashboard.app import app as dashboard_app, add_signal as dashboard_add_signal
import threading as _threading


# Load Telegram credentials if available
try:
    from config.secrets import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
    TELEGRAM_ENABLED = True
except ImportError:
    TELEGRAM_ENABLED = False
    TELEGRAM_ENABLED = False

# Load webhook secret if available
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", None)

# -----------------------------------------------
# SET UP LOGGING
# Save every signal to a log file for later review
# -----------------------------------------------

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level    = logging.INFO,
    format   = "%(asctime)s — %(message)s",
    handlers = [
        logging.FileHandler("logs/signals.log"),  # Save to file
        logging.StreamHandler(),                   # Also print to screen
    ]
)
log = logging.getLogger(__name__)


# -----------------------------------------------
# COMBINE ALL SYMBOLS INTO ONE LIST
# -----------------------------------------------

ALL_SYMBOLS = CRYPTO_SYMBOLS + STOCK_SYMBOLS + FOREX_SYMBOLS + INDEX_SYMBOLS


# -----------------------------------------------
# MAIN ANALYSIS FUNCTION
# -----------------------------------------------

def run_analysis():
    """
    Runs the full signal analysis on every symbol.
    Called every 15 minutes by the scheduler.
    """
    print("\n" + "="*60)
    print(f"🔍 Running analysis at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    for symbol in ALL_SYMBOLS:
        try:
            print(f"\n📊 Analysing {symbol}...")

            # Fetch data
            df_15m, df_daily = get_data(symbol)

            # Skip if data fetch failed
            if df_15m.empty or df_daily.empty:
                print(f"⚠️  Skipping {symbol} — no data available")
                continue

            # Run signal engine
            result = analyse_symbol(symbol, df_15m, df_daily)

            # Print result
            print_signal(result)

            # Log to file and send Telegram alert
            if result["action"] != "WAIT":
                log.info(
                    f"SIGNAL | {symbol} | {result['action']} | "
                    f"Confidence: {result['confidence']}% | "
                    f"Entry: {result['entry']} | "
                    f"Stop: {result['stop_loss']} | "
                    f"Target: {result['take_profit']}"
                )

                # Send Telegram notification
                if TELEGRAM_ENABLED:
                    msg = format_signal_message(result)
                    send_telegram(msg, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
                    print(f"   📱 Telegram alert sent")

                # Add to dashboard
                try:
                    dashboard_add_signal(result)
except Exception:
                    pass

        except Exception as e:
            print(f"❌ Error analysing {symbol}: {e}")
            continue

    print("\n✅ Analysis complete. Next run in 15 minutes.\n")


def print_signal(result: dict):
    """
    Prints a formatted signal to the console.
    """
    symbol = result["symbol"]
    action = result["action"]

    if action == "WAIT":
        print(f"   ⬜ {symbol} — No signal (Buy: {result['buy_score']} | Sell: {result['sell_score']})")
        return

    # Only show full detail for actual signals
    emoji = "🟢" if action == "BUY" else "🔴"

    print(f"\n{'='*50}")
    print(f"{emoji} SIGNAL DETECTED — {symbol}")
    print(f"{'='*50}")
    print(f"   Action:      {action}")
    print(f"   Confidence:  {result['confidence']}%")
    print(f"   Buy Score:   {result['buy_score']}  |  Sell Score: {result['sell_score']}")
    print(f"   Entry:       {result['entry']}")
    print(f"   Stop Loss:   {result['stop_loss']}")
    print(f"   Take Profit: {result['take_profit']}")
    print(f"   Daily ATR:   {result['daily_atr']}")
    print(f"   RSI:         {result['current_rsi']}")
    print(f"\n   Conditions:")
    for c in result["conditions"]:
        print(f"   {c}")
    print(f"{'='*50}\n")



def on_tradingview_signal(signal: dict):
    """
    Called when TradingView sends a webhook alert.
    Broadcasts the signal to all Telegram subscribers.
    """
    print(f"\n📡 TradingView signal received: {signal['action']} {signal['symbol']}")
    if TELEGRAM_ENABLED:
        msg = format_tradingview_signal_message(signal)
        send_telegram(msg, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        print(f"   📱 Telegram alert sent")


if __name__ == "__main__":
    print("🚀 QuantBot started")
    print(f"   Watching {len(ALL_SYMBOLS)} symbols")
    print(f"   Symbols: {', '.join(ALL_SYMBOLS)}")
    print()

    # Start webhook server in background (ready for TradingView Pro)
    webhook_app = create_webhook_app(
        on_signal_callback=on_tradingview_signal,
        webhook_secret=WEBHOOK_SECRET,
    )
    start_webhook_server(webhook_app, port=8080)
    print("🌐 Webhook server running — ready for TradingView alerts")
    print()

    # Run analysis immediately on startup
    run_analysis()

    # Schedule every 15 minutes
    schedule.every(15).minutes.do(run_analysis)

    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped.")
