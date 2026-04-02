# QuantBot

A multi-asset quantitative trading signal system that detects institutional "liquidity sweeps" across 333 symbols. Signals are scored against multiple technical confluence factors and broadcast via Telegram and a live web dashboard.

## Project Overview

The bot scans 6 asset classes on a 15-minute timeframe using dynamic, per-class ATR sweep thresholds. When a qualifying sweep is detected and confirmed, it calculates a weighted confluence score across RSI, EMA trend, Fibonacci levels, pivot points, and monthly demand zones to generate BUY, SELL, or WAIT decisions.

## Tech Stack

- **Language:** Python 3.11 (Replit environment)
- **Data Sources:** Yahoo Finance (`yfinance`) for stocks, forex, indices, and commodities; Binance API for crypto
- **Data Processing:** `pandas`, `numpy` (all indicators implemented from scratch — no pandas-ta dependency)
- **Scheduling:** `schedule` (runs full analysis every 15 minutes)
- **Web Framework:** Flask (live dashboard + TradingView webhook receiver)
- **Alerts:** Telegram Bot API via long-polling (no external library required)

## Project Structure

```
quant-bot/
├── main.py                    # Entry point — starts scheduler, dashboard, Telegram bot
├── requirements.txt           # Python dependencies
├── config/
│   ├── settings.py            # All symbols, dynamic thresholds, weights, strategy constants
│   └── secrets.example.py    # Template for API keys
├── core/
│   ├── data_feed.py           # Fetches OHLCV data from Yahoo Finance / Binance
│   ├── indicators.py          # RSI, ATR, EMA, Fibonacci, Pivot Points, Monthly closes
│   ├── sweep_detector.py      # Liquidity sweep detection and confirmation logic
│   ├── signal_engine.py       # Asset classifier, dynamic threshold lookup, signal scoring
│   ├── signal_store.py        # Thread-safe in-memory signal store (shared with dashboard)
│   ├── telegram_alerts.py     # Broadcasts signals to all Telegram subscribers
│   ├── bot_handler.py         # /start, /stop, /status command handler (long-polling)
│   ├── subscriber_store.py    # Subscriber list persistence (data/subscribers.json)
│   └── webhook_receiver.py    # Flask blueprint for TradingView webhook integration
├── dashboard/
│   └── app.py                 # Flask web dashboard — live signals, stats, symbol tags
├── models/
│   └── markov.py              # Time-inhomogeneous Markov chain regime classifier
├── backtest/
│   └── run_backtest.py        # Walk-forward backtester on historical data
└── tests/
    └── test_indicators.py     # Unit tests for indicator calculations
```

## Running the Bot

The workflow runs: `cd quant-bot && python main.py`

On startup it:
1. Launches the Flask dashboard in a background thread (port 5000)
2. Auto-subscribes the owner Telegram ID and starts the command handler
3. Immediately runs a full analysis pass across all 333 symbols
4. Schedules a repeat every 15 minutes

## Asset Coverage (333 symbols total)

| Category          | Count | Source         | Symbol Format       |
|-------------------|-------|----------------|---------------------|
| Crypto            | 40    | Binance API    | `BTCUSDT`, `ETHUSDT`|
| US Stocks (S&P)   | 98    | Yahoo Finance  | `AAPL`, `NVDA`      |
| UK Stocks (FTSE)  | 80    | Yahoo Finance  | `HSBA.L`, `BP.L`    |
| Forex             | 40    | Yahoo Finance  | `EURUSD=X`          |
| Global Indices    | 24    | Yahoo Finance  | `^GSPC`, `^N225`    |
| Commodities       | 20    | Yahoo Finance  | `GC=F`, `CL=F`      |

## Dynamic Sweep Thresholds

Each asset class uses a different minimum % of daily ATR to qualify a candle as a sweep:

| Asset Class | Threshold |
|-------------|-----------|
| Crypto      | 20%       |
| Stocks      | 15%       |
| Commodities | 15%       |
| Indices     | 12%       |
| Forex       | 10%       |

Symbol classification is done automatically in `core/signal_engine.py` by suffix/prefix pattern (`USDT` → crypto, `=X` → forex, `=F` → commodity, `^` → index, everything else → stock).

## Configuration

Edit `quant-bot/config/settings.py` to change:
- Symbol lists: `CRYPTO_SYMBOLS`, `STOCK_SYMBOLS`, `UK_STOCK_SYMBOLS`, `FOREX_SYMBOLS`, `INDEX_SYMBOLS`, `COMMODITY_SYMBOLS`
- Sweep thresholds: `SWEEP_THRESHOLDS` dict
- Signal scoring weights: `SIGNAL_WEIGHTS`
- Risk management: `ATR_STOP_MULTIPLIER`, `ATR_TARGET_MULTIPLIER`
- Regime model: `MARKOV_LOOKBACK_DAYS`, `MARKOV_MIN_PROBABILITY`

## API Keys / Secrets

Set these as Replit Secrets (environment variables):

| Variable | Purpose |
|----------|---------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Your personal chat ID — auto-subscribed as owner |

Binance API returns a 451 geo-restriction error on Replit's servers. All other asset classes (293 symbols) work without any API keys.

## Notes

- All indicator maths are implemented from scratch in `core/indicators.py` using pandas and numpy — no pandas-ta dependency
- The `asset_class` and `sweep_threshold` used are included in every signal result dict for full traceability
- Signals are stored in-memory in `core/signal_store.py` and served to the dashboard via `/api/signals` and `/api/stats`
- Yahoo Finance symbols: stocks use plain ticker (`AAPL`), UK stocks append `.L` (`BARC.L`), forex uses `=X` suffix, indices use `^` prefix, futures use `=F` suffix
