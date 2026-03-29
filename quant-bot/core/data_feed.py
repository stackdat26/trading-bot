# core/data_feed.py
# =============================================
# Fetches price data from APIs.
#
# Uses yfinance (Yahoo Finance) for stocks,
# forex, and indices — completely FREE.
#
# Uses Binance API for crypto.
#
# All data is returned as a standard DataFrame
# with columns: open, high, low, close, volume
# =============================================

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta


# --- YAHOO FINANCE (stocks, forex, indices) ---

def fetch_yfinance(symbol: str, interval: str = "15m", days_back: int = 7) -> pd.DataFrame:
    """
    Fetches OHLCV data from Yahoo Finance.
    Works for stocks (AAPL), forex (EURUSD=X), indices (^GSPC).

    Args:
        symbol:    Yahoo Finance symbol string
        interval:  Candle size — "15m", "1h", "1d", etc.
        days_back: How many days of history to fetch

    Returns:
        DataFrame with open, high, low, close, volume columns
    """
    end_date   = datetime.now()
    start_date = end_date - timedelta(days=days_back)

    ticker = yf.Ticker(symbol)
    df = ticker.history(
        start    = start_date,
        end      = end_date,
        interval = interval,
    )

    if df.empty:
        print(f"⚠️  No data returned for {symbol}. Check the symbol is correct.")
        return pd.DataFrame()

    # Standardise column names to lowercase
    df.columns = [col.lower() for col in df.columns]
    df = df[["open", "high", "low", "close", "volume"]]

    # Drop any rows with missing data
    df = df.dropna()

    print(f"✅ Fetched {len(df)} candles for {symbol} ({interval})")
    return df


def fetch_daily_yfinance(symbol: str, days_back: int = 90) -> pd.DataFrame:
    """
    Fetches daily candles for a symbol.
    Used for ATR, Pivots, and Monthly Demand calculations.

    Args:
        symbol:    Yahoo Finance symbol
        days_back: How many days back (default 90 = ~3 months)

    Returns:
        DataFrame of daily candles
    """
    return fetch_yfinance(symbol, interval="1d", days_back=days_back)


# --- BINANCE (crypto) ---

def fetch_binance(symbol: str, interval: str = "15m", limit: int = 100) -> pd.DataFrame:
    """
    Fetches OHLCV data from Binance (for crypto).
    No API key required for historical data.

    Args:
        symbol:   Binance symbol (e.g. "BTCUSDT")
        interval: Candle size — "15m", "1h", "1d", etc.
        limit:    Number of candles to fetch (max 1000)

    Returns:
        DataFrame with open, high, low, close, volume columns
    """
    import requests

    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol":   symbol,
        "interval": interval,
        "limit":    limit,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw = response.json()
    except Exception as e:
        print(f"❌ Binance fetch failed for {symbol}: {e}")
        return pd.DataFrame()

    # Binance returns a list of lists — convert to DataFrame
    df = pd.DataFrame(raw, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])

    # Keep only what we need
    df = df[["timestamp", "open", "high", "low", "close", "volume"]]

    # Convert types
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df.set_index("timestamp")
    df = df.astype(float)

    print(f"✅ Fetched {len(df)} candles for {symbol} ({interval}) from Binance")
    return df


def fetch_binance_daily(symbol: str, limit: int = 90) -> pd.DataFrame:
    """
    Fetches daily Binance candles.
    Used for ATR and monthly demand calculations.
    """
    return fetch_binance(symbol, interval="1d", limit=limit)


# --- AUTO-DETECT WHICH API TO USE ---

def get_data(symbol: str, interval: str = "15m") -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Automatically detects if a symbol is crypto or traditional asset,
    then fetches both 15min and daily data.

    Args:
        symbol: Any symbol — Binance format for crypto, Yahoo for others

    Returns:
        Tuple of (df_15min, df_daily)
    """
    # Crypto symbols typically end in USDT, BTC, ETH, BNB
    crypto_endings = ["USDT", "BTC", "ETH", "BNB", "BUSD"]
    is_crypto = any(symbol.upper().endswith(end) for end in crypto_endings)

    if is_crypto:
        df_15m  = fetch_binance(symbol, interval="15m", limit=100)
        df_daily = fetch_binance_daily(symbol, limit=90)
    else:
        df_15m  = fetch_yfinance(symbol, interval="15m", days_back=7)
        df_daily = fetch_daily_yfinance(symbol, days_back=90)

    return df_15m, df_daily
