# QuantBot

A multi-asset quantitative trading signal system designed to detect institutional "liquidity sweeps."

## Project Overview

The bot scans multiple asset classes (Crypto, Stocks, Forex, Indices) on a 15-minute timeframe. Its core strategy identifies candles that exceed a percentage of the daily Average True Range (ATR). When such a sweep is detected, the bot calculates a confluence score to generate BUY, SELL, or WAIT signals.

## Tech Stack

- **Language:** Python 3.11 (Replit environment)
- **Data Sources:** Yahoo Finance (yfinance) for stocks/forex/indices, Binance API for crypto
- **Data Processing:** pandas, numpy
- **Technical Indicators:** pandas-ta (RSI, ATR, EMA, etc.)
- **Scheduling:** schedule (runs analysis every 15 minutes)
- **Web Framework:** Flask (included for future TradingView webhook integration)

## Project Structure

```
quant-bot/
├── main.py              # Entry point — starts the scheduling loop
├── requirements.txt     # Python dependencies
├── config/
│   ├── settings.py      # Strategy constants, signal weights, symbol lists
│   └── secrets.example.py  # Template for API keys
├── core/
│   ├── data_feed.py     # Fetches OHLCV data from Yahoo Finance / Binance
│   ├── indicators.py    # RSI, ATR, Fibonacci, Pivot Points
│   ├── sweep_detector.py # Liquidity sweep detection logic
│   └── signal_engine.py # Signal scoring and BUY/SELL/WAIT decisions
├── models/
│   └── markov.py        # Markov chain regime classifier
└── tests/
    └── test_indicators.py
```

## Running the Bot

The workflow runs: `cd quant-bot && python main.py`

- Fetches data for all configured symbols
- Runs signal engine every 15 minutes
- Logs signals to `quant-bot/logs/signals.log`

## Configuration

Edit `quant-bot/config/settings.py` to:
- Add/remove symbols to watch
- Adjust signal scoring weights
- Tune risk management settings (ATR multipliers)
- Change Markov model lookback period

## API Keys

Binance API returns a 451 error in the Replit environment (geo-restriction). Stocks, Forex, and Indices via Yahoo Finance work without any API keys.

To add Binance API keys, copy `config/secrets.example.py` to `config/secrets.py` and fill in your keys.

## Notes

- Binance geo-restriction: The Replit environment may not have access to Binance API endpoints. Crypto symbols (BTCUSDT, ETHUSDT) will fail with a 451 error but all other symbols work fine.
- Yahoo Finance symbols: Stocks use ticker format (AAPL), Forex uses `=X` suffix (EURUSD=X), Indices use `^` prefix (^GSPC).
