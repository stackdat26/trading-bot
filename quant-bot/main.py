# main.py
# =============================================
# Run this file to start the bot.
#
# What it does:
#   1. Starts the web dashboard on port 5000
#   2. Starts the Telegram command handler
#   3. Fetches data and runs the signal engine
#   4. Sends signals to Telegram + logs them
#   5. Displays signals on the web dashboard
#   6. Waits 15 minutes and repeats
# =============================================

import time
import schedule
import logging
import os
from datetime import datetime

from config.settings import (
    CRYPTO_SYMBOLS,
    STOCK_SYMBOLS,
    UK_STOCK_SYMBOLS,
    FOREX_SYMBOLS,
    INDEX_SYMBOLS,
    COMMODITY_SYMBOLS,
)
from core.data_feed import get_data
from core.signal_engine import analyse_symbol
from core.telegram_alerts import send_signal_alert, TELEGRAM_ENABLED, ensure_owner_subscribed
from core.bot_handler import start_bot_handler
from core.subscriber_store import subscriber_count
from core.signal_store import add_signal
from dashboard.app import start_dashboard


# -----------------------------------------------
# SET UP LOGGING
# -----------------------------------------------

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level    = logging.INFO,
    format   = "%(asctime)s — %(message)s",
    handlers = [
        logging.FileHandler("logs/signals.log"),
        logging.StreamHandler(),
    ]
)
log = logging.getLogger(__name__)


# -----------------------------------------------
# COMBINE ALL SYMBOLS INTO ONE LIST
# -----------------------------------------------

ALL_SYMBOLS = (
    CRYPTO_SYMBOLS
    + STOCK_SYMBOLS
    + UK_STOCK_SYMBOLS
    + FOREX_SYMBOLS
    + INDEX_SYMBOLS
    + COMMODITY_SYMBOLS
)


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

            df_15m, df_daily = get_data(symbol)

            if df_15m.empty or df_daily.empty:
                print(f"⚠️  Skipping {symbol} — no data available")
                continue

            result = analyse_symbol(symbol, df_15m, df_daily)

            print_signal(result)

            if result["action"] != "WAIT":
                # Store in dashboard
                add_signal(result)

                # Log to file
                log.info(
                    f"SIGNAL | {symbol} | {result['action']} | "
                    f"Confidence: {result['confidence']}% | "
                    f"Entry: {result['entry']} | "
                    f"Stop: {result['stop_loss']} | "
                    f"Target: {result['take_profit']}"
                )

                # Send Telegram alerts
                if TELEGRAM_ENABLED:
                    sent = send_signal_alert(result)
                    if sent:
                        print(f"   📲 Telegram alert sent to {sent} subscriber(s) for {symbol}")

        except Exception as e:
            print(f"❌ Error analysing {symbol}: {e}")
            continue

    print("\n✅ Analysis complete. Next run in 15 minutes.\n")


def print_signal(result: dict):
    """Prints a formatted signal to the console."""
    symbol = result["symbol"]
    action = result["action"]

    if action == "WAIT":
        print(f"   ⬜ {symbol} — No signal (Buy: {result['buy_score']} | Sell: {result['sell_score']})")
        return

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


# -----------------------------------------------
# STARTUP
# -----------------------------------------------

if __name__ == "__main__":
    # Start web dashboard on port 5000
    start_dashboard()

    # Auto-subscribe owner and start Telegram command handler
    ensure_owner_subscribed()
    start_bot_handler()

    print("🚀 QuantBot started")
    print(f"   Watching {len(ALL_SYMBOLS)} symbols")
    print(f"   Symbols: {', '.join(ALL_SYMBOLS)}")
    print(f"   Telegram alerts: {'✅ enabled' if TELEGRAM_ENABLED else '❌ not configured'}")
    print(f"   Subscribers: {subscriber_count()}")
    print(f"   Dashboard: http://0.0.0.0:5000")
    print()

    # Run immediately on startup
    run_analysis()

    # Then every 15 minutes
    schedule.every(15).minutes.do(run_analysis)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped.")
