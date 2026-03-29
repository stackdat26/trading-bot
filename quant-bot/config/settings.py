# config/settings.py
# =============================================
# All your bot's main settings live here.
# Change these to customise how the bot works.
# =============================================


# --- ASSETS TO TRADE ---
# Add or remove any symbols you want the bot to watch

CRYPTO_SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
]

STOCK_SYMBOLS = [
    "AAPL",
    "TSLA",
    "NVDA",
]

FOREX_SYMBOLS = [
    "EURUSD=X",   # Euro vs Dollar (Yahoo Finance format)
    "GBPUSD=X",
]

INDEX_SYMBOLS = [
    "^GSPC",      # S&P 500
    "^IXIC",      # NASDAQ
    "^FTSE",      # FTSE 100
]


# --- TIMEFRAMES ---
SWEEP_TIMEFRAME     = "15m"    # The candle size for sweep detection
TREND_TIMEFRAME     = "1h"     # Used for EMA trend direction
CONTEXT_TIMEFRAME   = "1d"     # Daily candles for ATR, Pivots, Monthly levels


# --- LIQUIDITY SWEEP SETTINGS ---
SWEEP_THRESHOLD_PERCENT = 20   # Candle must be > 20% of daily ATR to count as sweep
ATR_PERIOD              = 14   # Number of days to calculate ATR over


# --- RSI SETTINGS ---
RSI_PERIOD      = 14
RSI_OVERSOLD    = 30           # Below this = potential buy
RSI_OVERBOUGHT  = 70           # Above this = potential sell


# --- EMA SETTINGS ---
EMA_FAST = 20                  # Short EMA (trend detection)
EMA_SLOW = 50                  # Long EMA (major trend)


# --- FIBONACCI LEVELS ---
# These are the retracement levels your bot checks confluence at
FIB_RETRACEMENTS = [0.236, 0.382, 0.500, 0.618, 0.786]
FIB_EXTENSIONS   = [1.272, 1.414, 1.618, 2.000, 2.618]


# --- SIGNAL SCORING WEIGHTS ---
# Higher number = that indicator counts for more in the final score
# You can tune these over time based on what works best

SIGNAL_WEIGHTS = {
    "liquidity_sweep":    30,   # Your main edge
    "rsi":                20,   # Momentum confirmation
    "trend_ema":          15,   # Direction filter
    "pivot_level":        25,   # Institutional level
    "fibonacci":          20,   # Confluence
    "confirmation":       30,   # Next candle confirms the sweep
}

# Minimum score to generate a BUY or SELL signal (out of ~140 max)
MIN_SIGNAL_SCORE = 60

# How much stronger one side needs to be vs the other
MIN_SCORE_DIFFERENCE = 30


# --- RISK MANAGEMENT ---
ATR_STOP_MULTIPLIER   = 2.0    # Stop loss = entry ± (ATR × this)
ATR_TARGET_MULTIPLIER = 3.0    # Take profit = entry ± (ATR × this)


# --- MARKOV MODEL SETTINGS ---
MARKOV_LOOKBACK_DAYS = 30      # How many days of history to build transition matrix from
MARKOV_MIN_PROBABILITY = 0.55  # Only boost signal if Markov agrees above this threshold

# Market states the Markov model tracks
MARKET_STATES = ["BULLISH", "BEARISH", "OVERBOUGHT", "OVERSOLD", "HIGH_VOL", "SIDEWAYS"]


# --- DATA SETTINGS ---
CANDLES_TO_FETCH   = 100       # How many candles to pull for analysis
CACHE_DIR          = "data_cache"
