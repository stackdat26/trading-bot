# QuantBot — Multi-Asset Liquidity Sweep Trading System

> Built by a 17-year-old. Designed like a prop firm.

A quantitative trading signal bot that detects **institutional liquidity sweeps** across 333 symbols spanning crypto, stocks, forex, indices, and commodities — using dynamic ATR-based thresholds, RSI, Fibonacci retracements, pivot points, and Markov chain regime detection. Signals are broadcast live to all Telegram subscribers and displayed on a real-time web dashboard.

---

## Status: LIVE

Bot is actively running and broadcasting signals to subscribers.  
Subscribe: [t.me/Stackdat_bot](https://t.me/Stackdat_bot)

### Live Signal Example
<img width="300" height="2400" alt="image" src="https://github.com/user-attachments/assets/864031fe-d75e-4b26-a2b1-5cb4a94f4058" />
<img width="300" height="2400" alt="image" src="https://github.com/user-attachments/assets/353d531c-3a64-457d-83e5-260e59329dff" />

---

## The Core Idea

Retail traders react to price. Institutions **cause** price to move.

This bot detects the fingerprint institutions leave behind:
- Large candles that exceed a **dynamic % of the daily ATR** (tuned per asset class) on a 15-minute timeframe
- These are **liquidity sweeps** — forced stop runs that trap retail traders
- After confirmation, the bot scores confluence across multiple indicators
- Only fires a signal when enough conditions align → **high-probability trades**

---

## What It Detects

| Signal Component | What It Does |
|-----------------|-------------|
| **Liquidity Sweep** | 15min candle range exceeds a dynamic % of daily ATR (varies by asset class) |
| **RSI** | Momentum filter — oversold/overbought conditions |
| **ATR** | Daily volatility anchor — everything is measured relative to this |
| **EMA (20)** | Trend direction filter |
| **Fibonacci Levels** | Retracement confluence (0.236, 0.382, 0.5, 0.618, 0.786) + extensions |
| **Pivot Points** | Daily R1, R2, S1, S2 — key institutional levels |
| **Monthly Demand** | Monthly candle close zones — where real money settled |
| **Markov Regime** | Time-inhomogeneous state model — adapts to current market conditions |

---

## Dynamic Sweep Thresholds

Each asset class has its own sweep threshold, calibrated to its typical volatility:

| Asset Class | ATR Threshold | Reasoning |
|-------------|--------------|-----------|
| Crypto | 20% | Highly volatile — needs a larger candle to qualify |
| Stocks (US & UK) | 15% | Standard equity moves |
| Commodities | 15% | Similar volatility profile to stocks |
| Indices | 12% | Tighter than single stocks |
| Forex | 10% | FX pairs move in tight ATR-relative ranges |

---

## Asset Coverage (333 symbols)

| Asset Class | Count | Source | Format |
|-------------|-------|--------|--------|
| Crypto | 40 | Binance API | `BTCUSDT`, `ETHUSDT`, ... |
| US Stocks | 98 | Yahoo Finance | `AAPL`, `NVDA`, `JPM`, ... |
| UK Stocks (FTSE 100) | 80 | Yahoo Finance | `HSBA.L`, `BP.L`, ... |
| Forex | 40 | Yahoo Finance | `EURUSD=X`, `GBPJPY=X`, ... |
| Global Indices | 24 | Yahoo Finance | `^GSPC`, `^N225`, `^FTSE`, ... |
| Commodities | 20 | Yahoo Finance | `GC=F`, `CL=F`, `ZC=F`, ... |

> Binance API returns a 451 geo-restriction error on some hosting environments. All other asset classes work without API keys.

---

## Project Structure

```
quant-bot/
├── README.md                  ← You are here
├── requirements.txt           ← Python libraries needed
├── main.py                    ← Entry point — starts scheduler, dashboard, and Telegram bot
│
├── config/
│   ├── settings.py            ← All symbols, thresholds, weights, and strategy constants
│   └── secrets.example.py    ← Template for API keys (never commit the real one)
│
├── core/
│   ├── data_feed.py           ← Fetches OHLCV data (Yahoo Finance + Binance)
│   ├── indicators.py          ← RSI, ATR, EMA, Fibonacci, Pivot Points (pure pandas/numpy)
│   ├── sweep_detector.py      ← Core liquidity sweep detection logic
│   ├── signal_engine.py       ← Classifies asset, applies dynamic threshold, scores signal
│   ├── signal_store.py        ← In-memory signal store shared between bot and dashboard
│   ├── telegram_alerts.py     ← Broadcasts BUY/SELL signals to all Telegram subscribers
│   ├── bot_handler.py         ← Handles /start, /stop, /status commands (long-polling)
│   ├── subscriber_store.py    ← Saves/loads subscriber list (data/subscribers.json)
│   └── webhook_receiver.py    ← Flask blueprint for TradingView webhook integration
│
├── dashboard/
│   └── app.py                 ← Flask web dashboard — live signals, stats, symbol list
│
├── models/
│   └── markov.py              ← Time-inhomogeneous Markov chain regime model
│
├── backtest/
│   └── run_backtest.py        ← Backtests strategy on historical data
│
└── tests/
    └── test_indicators.py     ← Unit tests for indicator calculations
```

---

## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/quant-bot.git
cd quant-bot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your secrets

You'll need:
- **`TELEGRAM_BOT_TOKEN`** — create a bot via [@BotFather](https://t.me/BotFather) on Telegram
- **`TELEGRAM_CHAT_ID`** — your personal Telegram chat ID (auto-subscribed as owner)

**On Linux/Mac:**
```bash
export TELEGRAM_BOT_TOKEN="your_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
```

**On Windows:**
```cmd
set TELEGRAM_BOT_TOKEN=your_token_here
set TELEGRAM_CHAT_ID=your_chat_id_here
```

**On Replit:** Add them in the Secrets tab — they're loaded automatically.

### 4. Run the bot
```bash
python main.py
```

### 5. Test Telegram connection
```bash
python -c "from core.telegram_alerts import send_telegram; send_telegram('QuantBot working!')"
```

### 6. Run the backtester
```bash
python backtest/run_backtest.py
```

---

## Telegram Multi-User System

Anyone can subscribe to receive signals by messaging your bot:

| Command | What it does |
|---------|-------------|
| `/start` | Subscribe to signals |
| `/stop` | Unsubscribe |
| `/status` | Show how many subscribers there are |

- Share your bot link (`t.me/YourBotName`) with anyone
- Every subscriber receives all BUY/SELL signals in real time
- The owner (`TELEGRAM_CHAT_ID`) is auto-subscribed on startup
- Subscriber list persists across restarts in `data/subscribers.json`

---

## Web Dashboard

The bot runs a live Flask dashboard on port 5000 showing:
- Bot uptime and start time
- Total signals, buy signals, sell signals, subscriber count
- All 333 watched symbols displayed as tags
- Live signal table with entry, stop loss, take profit, RSI, and confidence
- TradingView webhook URL for external signal integration

---

## Example Signal Output

```
==================================================
SIGNAL DETECTED — AAPL
==================================================
   Action:      BUY
   Confidence:  75%
   Buy Score:   75  |  Sell Score: 0
   Entry:       254.61
   Stop Loss:   244.37
   Take Profit: 259.52
   Daily ATR:   5.12
   RSI:         66.9

   Conditions:
   ✅ Price above EMA20 (bullish trend)
   ✅ Sweep near support pivot (S1=253.91, S2=252.20)
   ✅ Sweep at Fibonacci retracement (support)
   ✅ Near monthly demand zone
==================================================
```

---

## Configuration

Edit `config/settings.py` to customise:

| Setting | What to change |
|---------|---------------|
| `CRYPTO_SYMBOLS`, `STOCK_SYMBOLS`, `UK_STOCK_SYMBOLS`, `FOREX_SYMBOLS`, `INDEX_SYMBOLS`, `COMMODITY_SYMBOLS` | Add or remove symbols |
| `SWEEP_THRESHOLDS` | ATR % per asset class to qualify as a sweep |
| `SIGNAL_WEIGHTS` | How much each condition contributes to the score |
| `MIN_SIGNAL_SCORE` | Minimum score to fire a BUY or SELL (default: 60) |
| `ATR_STOP_MULTIPLIER` / `ATR_TARGET_MULTIPLIER` | Stop loss and take profit distances |
| `MARKOV_LOOKBACK_DAYS` | History window for regime detection |

---

## Security

- Never commit `config/secrets.py` to GitHub — it's in `.gitignore`
- Use environment variables or your platform's secrets manager
- Rotate your Telegram bot token immediately if it's ever exposed

---

## Roadmap

- [x] Core indicator calculations (RSI, ATR, EMA, Fibonacci, Pivots)
- [x] Liquidity sweep detection
- [x] Dynamic per-asset-class sweep thresholds
- [x] Multi-factor signal scoring with configurable weights
- [x] Markov regime model
- [x] Backtester (walk-forward on historical data)
- [x] Telegram alerts with multi-user subscribe/unsubscribe
- [x] TradingView webhook integration
- [x] Live web dashboard
- [x] 333-symbol coverage (Crypto, US Stocks, UK FTSE 100, Forex, Indices, Commodities)
- [ ] Live paper trading mode
- [ ] Per-signal performance tracking

---

## Author

Built by a 17-year-old learning quantitative finance from scratch.  
Inspired by institutional market structure analysis.

---

## License

MIT — use it, learn from it, build on it.
