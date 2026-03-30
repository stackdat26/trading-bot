# 📈 QuantBot — Multi-Asset Liquidity Sweep Trading System

> Built by a 17-year-old. Designed like a prop firm.

A quantitative trading signal bot that detects **institutional liquidity sweeps** across crypto, stocks, forex, and indices — using RSI, ATR, Fibonacci retracements, pivot points, and time-inhomogeneous Markov chain regime detection.

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
│   ├── settings.py            ← Your symbols, timeframes, thresholds
│   └── secrets.example.py    ← Template for API keys (never commit the real one)
│
├── core/
│   ├── data_feed.py           ← Fetches price data (REST + WebSocket)
│   ├── indicators.py          ← RSI, ATR, EMA, Fibonacci, Pivots
│   ├── sweep_detector.py      ← The core liquidity sweep logic
│   └── signal_engine.py       ← Combines all signals into a score
│
├── models/
│   ├── markov.py              ← Time-inhomogeneous Markov chain
│   └── regimes.py             ← Classifies market state (Bullish, Bearish, etc.)
│
├── execution/
│   └── trader.py              ← Order logic + risk management (paper trade first)
│
├── backtest/
│   └── backtester.py          ← Test strategy on historical data
│
├── notebooks/
│   └── analysis.ipynb         ← Jupyter notebook for exploring data
│
├── tests/
│   └── test_indicators.py     ← Verify your maths is right
│
└── logs/
    └── signals.log            ← Every signal the bot fires gets logged here
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

### 3. Set up your config
```bash
cp config/secrets.example.py config/secrets.py
# Then open secrets.py and add your API keys
```

### 4. Run it
```bash
python main.py
```

---

## 📊 Example Signal Output

```
==================================================
🔍 Running strategy at 2024-01-15 14:00:00
==================================================

💥 SWEEP DETECTED on BTCUSDT
   Candle Range: $1,240  |  Daily ATR: $4,100
   Sweep Size: 30.2% of daily ATR ✅

🎯 SIGNAL: BTCUSDT — BUY
   Confidence Score : 74%
   Buy Score        : 115  |  Sell Score: 20
   Entry Price      : $42,850
   Stop Loss        : $41,900  (2× ATR below)
   Take Profit      : $44,500  (1.618 Fib extension)
   Regime           : OVERSOLD → BULLISH (Markov P: 0.68)

   Conditions Met:
   ✅ Liquidity sweep (30% ATR)
   ✅ RSI oversold (27.4)
   ✅ Price at S1 pivot
   ✅ Price at 0.618 Fibonacci
   ⬜ Monthly demand zone (not close enough)
```

---

## ⚠️ Assets Supported

- **Crypto** — via Binance API (BTC, ETH, etc.)
- **Stocks** — via Yahoo Finance (free, no API key needed)
- **Forex** — via OANDA or Alpha Vantage
- **Indices** — SPX, NAS100, DAX via Yahoo Finance

---

## 🔐 API Keys

Never commit real API keys to GitHub. Use `config/secrets.py` (which is in `.gitignore`).

---

## 📌 Roadmap

- [x] Core repo structure
- [x] Indicator calculations (RSI, ATR, EMA, Fibonacci, Pivots)
- [x] Liquidity sweep detection
- [x] Multi-factor signal scoring
- [ ] Markov regime model
- [ ] Backtester
- [ ] TradingView webhook integration
- [ ] Telegram alerts
- [ ] Web dashboard

---

## 👤 Author

Built by a 17-year-old learning quantitative finance from scratch.  
Inspired by institutional market structure analysis.

---

## 📄 License

MIT — use it, learn from it, build on it.
