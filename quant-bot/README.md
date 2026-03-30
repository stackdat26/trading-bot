# 📈 QuantBot — Multi-Asset Liquidity Sweep Trading System

> Built by a 17-year-old. Designed like a prop firm.

A quantitative trading signal bot that detects **institutional liquidity sweeps** across stocks, forex, and indices — using RSI, ATR, Fibonacci retracements, pivot points, and Markov chain regime detection. Signals are broadcast live to all Telegram subscribers.

---

## 🟢 Status: LIVE

Bot is actively running and broadcasting signals to subscribers.  
Subscribe: [t.me/Stackdat_bot](https://t.me/Stackdat_bot)

### 📱 Live Signal Example
<img width="300" height="2400" alt="image" src="https://github.com/user-attachments/assets/864031fe-d75e-4b26-a2b1-5cb4a94f4058" />
<img width="300" height="2400" alt="image" src="https://github.com/user-attachments/assets/353d531c-3a64-457d-83e5-260e59329dff" />


---

## 🧠 The Core Idea

Retail traders react to price. Institutions **cause** price to move.

This bot detects the fingerprint institutions leave behind:
- Large candles that exceed **20% of the daily ATR** on a 15-minute timeframe
- These are **liquidity sweeps** — forced stop runs that trap retail
- After confirmation, the bot scores confluence across multiple indicators
- Only signals when enough conditions align → **high-probability trades**

---

## 🔍 What It Detects

| Signal Component | What It Does |
|-----------------|-------------|
| **Liquidity Sweep** | 15min candle range > 20% of daily ATR = institutional move |
| **RSI** | Momentum filter — oversold/overbought conditions |
| **ATR** | Daily volatility anchor — everything is measured relative to this |
| **EMA (20)** | Trend direction filter |
| **Fibonacci Levels** | Retracement confluence (0.382, 0.5, 0.618) + extensions |
| **Pivot Points** | Daily R1, R2, S1, S2 — key institutional levels |
| **Monthly Demand** | Monthly candle close zones — where real money settled |
| **Markov Regime** | Time-inhomogeneous state model — adapts to market conditions |

---

## 📁 Project Structure

```
quant-bot/
├── README.md                  ← You are here
├── requirements.txt           ← Python libraries needed
├── main.py                    ← Run the bot from here
├── .gitignore                 ← Keeps secrets and clutter out of GitHub
│
├── config/
│   ├── settings.py            ← Symbols, timeframes, thresholds, weights
│   └── secrets.example.py    ← Template for API keys (never commit the real one)
│
├── core/
│   ├── data_feed.py           ← Fetches price data (Yahoo Finance + Binance)
│   ├── indicators.py          ← RSI, ATR, EMA, Fibonacci, Pivots
│   ├── sweep_detector.py      ← Core liquidity sweep detection logic
│   ├── signal_engine.py       ← Combines all signals into a scored decision
│   ├── telegram_alerts.py     ← Broadcasts signals to all Telegram subscribers
│   ├── bot_handler.py         ← Handles /start, /stop, /status commands
│   └── subscriber_store.py    ← Saves/loads subscriber list (data/subscribers.json)
│
├── models/
│   └── markov.py              ← Time-inhomogeneous Markov chain regime model
│
├── backtest/
│   └── run_backtest.py        ← Backtests the strategy on historical data
│
└── tests/
    └── test_indicators.py     ← Unit tests for indicator calculations
```

---

## 🚀 Getting Started

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
```bash
cp config/secrets.example.py config/secrets.py
# Then open secrets.py and add your keys
```

You'll need:
- **`TELEGRAM_BOT_TOKEN`** — create a bot via [@BotFather](https://t.me/BotFather) on Telegram
- **`TELEGRAM_CHAT_ID`** — your personal Telegram chat ID (auto-subscribed as owner)

### 4. Add secrets as environment variables

The bot reads secrets from environment variables, not from the file directly.

**On Linux/Mac:**
```bash
export TELEGRAM_BOT_TOKEN="your_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
python main.py
```

**On Windows:**
```cmd
set TELEGRAM_BOT_TOKEN=your_token_here
set TELEGRAM_CHAT_ID=your_chat_id_here
python main.py
```

**On Replit:** Add them in the Secrets tab — they're loaded automatically.

### 5. Run the bot
```bash
python main.py
```

### 6. Test Telegram connection
```bash
python -c "from core.telegram_alerts import send_telegram; send_telegram('✅ QuantBot working!')"
```

### 7. Run the backtester
```bash
python backtest/run_backtest.py
```

---

## 📲 Telegram Multi-User System

Anyone can subscribe to receive signals by messaging your bot:

| Command | What it does |
|---------|-------------|
| `/start` | Subscribe to signals |
| `/stop` | Unsubscribe |
| `/status` | Show how many subscribers there are |

- Share your bot link (`t.me/YourBotName`) with anyone
- Every subscriber receives all BUY/SELL signals in real time
- The owner (`TELEGRAM_CHAT_ID`) is auto-subscribed on startup
- Subscriber list persists across restarts

---

## 📊 Example Signal Output

```
==================================================
🔍 Running analysis at 2024-01-15 14:00:00
==================================================

🟢 SIGNAL DETECTED — NVDA
==================================================
   Action:      BUY
   Confidence:  80%
   Buy Score:   80  |  Sell Score: 15
   Entry:       167.88
   Stop Loss:   158.05
   Take Profit: 171.90
   Daily ATR:   4.92
   RSI:         29.1

   Conditions:
   ✅ RSI oversold (29.1)
   ✅ Price below EMA20 (bearish trend reversal)
   ✅ Sweep near support pivot (S1=166.03, S2=164.54)
   ✅ Sweep at Fibonacci retracement (support)
   ✅ Near monthly demand zone
==================================================

📲 Telegram alert sent to 42 subscriber(s) for NVDA
```

---

## ⚠️ Assets Supported

| Asset Class | Provider | API Key Required? |
|-------------|----------|-------------------|
| **Stocks** | Yahoo Finance | No |
| **Forex** | Yahoo Finance | No |
| **Indices** | Yahoo Finance | No |
| **Crypto** | Binance | No (public endpoint) |

> Note: Binance may be geo-restricted in some hosting environments.

---

## 🔐 Keeping Secrets Safe

- **Never** commit `config/secrets.py` to GitHub — it's in `.gitignore`
- Use environment variables or your platform's secrets manager
- Rotate your Telegram bot token immediately if it's ever exposed

---

## 📌 Roadmap

- [x] Core repo structure
- [x] Indicator calculations (RSI, ATR, EMA, Fibonacci, Pivots)
- [x] Liquidity sweep detection
- [x] Multi-factor signal scoring
- [x] Markov regime model
- [x] Backtester (walk-forward on 55 days of 15m history)
- [x] Telegram alerts
- [x] Multi-user Telegram bot (/start, /stop, /status)
- [x] TradingView webhook integration
- [x] Web dashboard
- [ ] Live paper trading mode
- [ ] Performance tracking per signal

---

## 👤 Author

Built by a 17-year-old learning quantitative finance from scratch.  
Inspired by institutional market structure analysis.

---

## 📄 License

MIT — use it, learn from it, build on it.
