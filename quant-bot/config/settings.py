# config/settings.py
# =============================================
# All your bot's main settings live here.
# Change these to customise how the bot works.
# =============================================


# --- ASSETS TO TRADE ---
# Add or remove any symbols you want the bot to watch

CRYPTO_SYMBOLS = [
    # Major
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "AVAXUSDT", "DOGEUSDT", "DOTUSDT", "MATICUSDT",
    "LINKUSDT", "UNIUSDT", "ATOMUSDT", "LTCUSDT", "ETCUSDT",
    "XLMUSDT", "ALGOUSDT", "VETUSDT", "FILUSDT", "TRXUSDT",
    # Mid-cap / trending
    "NEARUSDT", "FTMUSDT", "SANDUSDT", "MANAUSDT", "AXSUSDT",
    "GALAUSDT", "APEUSDT", "GMTUSDT", "OPUSDT", "ARBUSDT",
    "INJUSDT", "SUIUSDT", "SEIUSDT", "TIAUSDT", "JUPUSDT",
    "WIFUSDT", "BONKUSDT", "PENDLEUSDT", "STRKUSDT", "PYTHUSDT",
]

STOCK_SYMBOLS = [
    # US S&P 500 — Tech & Mega-cap
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA",
    "BRK-B", "JPM", "JNJ", "V", "PG", "UNH", "HD", "MA",
    "DIS", "BAC", "XOM", "PFE", "KO", "WMT", "AMD", "NFLX",
    "PYPL", "INTC", "CSCO", "ADBE", "CRM", "ORCL", "IBM",
    # Financials
    "GS", "MS", "C", "WFC", "AXP", "SPGI", "BLK", "CB",
    # Industrials & Defence
    "MMM", "CAT", "DE", "BA", "LMT", "RTX", "NOC", "GD",
    "HON", "UPS", "FDX", "DAL", "UAL", "AAL",
    # Consumer
    "SBUX", "MCD", "YUM", "CMG", "NKE", "LULU", "TGT",
    "COST", "CVS", "WBA",
    # Healthcare
    "TMO", "ABT", "MDT", "SYK", "ISRG", "REGN", "BIIB",
    "AMGN", "GILD", "MRK", "LLY", "BMY",
    # Utilities
    "NEE", "DUK", "SO", "AEP", "EXC", "SRE", "PCG", "ED",
    "FE", "ETR",
    # REITs
    "AMT", "PLD", "CCI", "EQIX", "PSA", "SPG", "O", "VICI", "AVB",
    # Energy & Materials
    "EOG", "PXD", "COP", "MPC", "VLO", "PSX", "OXY", "HAL",
    "SLB", "NEM", "FCX", "AA", "X", "CLF", "MP", "ALB",
    "LTHM", "SQM",
]

UK_STOCK_SYMBOLS = [
    # FTSE 100 — Yahoo Finance format (append .L)
    "HSBA.L", "BP.L", "SHEL.L", "AZN.L", "ULVR.L", "RIO.L",
    "GSK.L", "BATS.L", "LSEG.L", "NG.L", "VOD.L", "LLOY.L",
    "BARC.L", "NWG.L", "BT-A.L", "MKS.L", "JD.L", "ABF.L",
    "IMB.L", "PRU.L", "STAN.L", "AAL.L", "ADM.L", "AGK.L",
    "ANTO.L", "AUTO.L", "AV.L", "AVV.L", "BA.L", "BAB.L",
    "BGEO.L", "BKG.L", "BLND.L", "BME.L", "BNZL.L", "BRBY.L",
    "CCH.L", "CCL.L", "CNA.L", "CPG.L", "CRDA.L", "CRH.L",
    "DCC.L", "DGE.L", "DLN.L", "DPLM.L", "EDV.L", "ENT.L",
    "EXPN.L", "EZJ.L", "FERG.L", "FLTR.L", "FRES.L", "GFS.L",
    "GLEN.L", "HIK.L", "HL.L", "HLMA.L", "HLN.L", "HWDN.L",
    "IAG.L", "IHG.L", "III.L", "INF.L", "ITRK.L", "ITV.L",
    "KGF.L", "LAND.L", "LGEN.L", "MNDI.L", "MNG.L", "MRO.L",
    "MTO.L", "NXT.L", "OCDO.L", "PHNX.L", "PSON.L", "REL.L",
    "RKT.L", "RMV.L", "RR.L", "SBRY.L", "SDR.L", "SGE.L",
    "SGRO.L", "SKG.L", "SMDS.L", "SMIN.L", "SMT.L", "SN.L",
    "SPX.L", "SSE.L", "SVT.L", "TSCO.L", "TW.L", "UU.L",
    "WPP.L", "WTB.L",
]

FOREX_SYMBOLS = [
    # Majors
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X",
    "NZDUSD=X", "USDCHF=X",
    # Euro crosses
    "EURGBP=X", "EURJPY=X", "EURAUD=X", "EURCAD=X", "EURNZD=X",
    "EURCHF=X",
    # GBP crosses
    "GBPJPY=X", "GBPAUD=X", "GBPCAD=X", "GBPCHF=X", "GBPNZD=X",
    # AUD/NZD/CAD crosses
    "AUDJPY=X", "AUDCAD=X", "AUDCHF=X", "AUDNZD=X",
    "CADJPY=X", "CADCHF=X",
    "NZDJPY=X", "NZDCAD=X", "NZDCHF=X",
    "CHFJPY=X",
    # Emerging markets
    "USDMXN=X", "USDZAR=X", "USDTRY=X", "USDSEK=X", "USDNOK=X",
    "USDDKK=X", "USDSGD=X", "USDHKD=X", "USDCNH=X", "USDINR=X",
    "USDKRW=X", "USDBRL=X",
]

INDEX_SYMBOLS = [
    # Americas
    "^GSPC",       # S&P 500
    "^IXIC",       # NASDAQ
    "^DJI",        # Dow Jones
    "^VIX",        # Volatility Index
    "^BVSP",       # Brazil Bovespa
    "^MXX",        # Mexico IPC
    # Europe
    "^FTSE",       # UK FTSE 100
    "^GDAXI",      # Germany DAX
    "^FCHI",       # France CAC 40
    "^STOXX50E",   # Euro Stoxx 50
    "^AEX",        # Netherlands AEX
    "^IBEX",       # Spain IBEX 35
    "^SSMI",       # Switzerland SMI
    # Asia-Pacific
    "^N225",       # Japan Nikkei 225
    "^HSI",        # Hong Kong Hang Seng
    "^AXJO",       # Australia ASX 200
    "^NSEI",       # India Nifty 50
    "^BSESN",      # India BSE Sensex
    "^KS11",       # South Korea KOSPI
    "^TWII",       # Taiwan TAIEX
    "^STI",        # Singapore STI
    "^KLSE",       # Malaysia KLCI
    "^JKSE",       # Indonesia IDX
    "^TA125.TA",   # Israel TA-125
]

COMMODITY_SYMBOLS = [
    # Precious metals
    "GC=F",   # Gold
    "SI=F",   # Silver
    "PL=F",   # Platinum
    "PA=F",   # Palladium
    # Energy
    "CL=F",   # Crude Oil (WTI)
    "BZ=F",   # Brent Crude
    "NG=F",   # Natural Gas
    "RB=F",   # RBOB Gasoline
    "HO=F",   # Heating Oil
    # Base metals
    "HG=F",   # Copper
    # Agricultural
    "ZC=F",   # Corn
    "ZW=F",   # Wheat
    "ZS=F",   # Soybeans
    "KC=F",   # Coffee
    "CT=F",   # Cotton
    "SB=F",   # Sugar
    "CC=F",   # Cocoa
    # Livestock
    "LE=F",   # Live Cattle
    "GF=F",   # Feeder Cattle
    "HE=F",   # Lean Hogs
]


# --- TIMEFRAMES ---
SWEEP_TIMEFRAME     = "15m"    # The candle size for sweep detection
TREND_TIMEFRAME     = "1h"     # Used for EMA trend direction
CONTEXT_TIMEFRAME   = "1d"     # Daily candles for ATR, Pivots, Monthly levels


# --- LIQUIDITY SWEEP SETTINGS ---
# Dynamic threshold per asset class:
#   Candle range must exceed this % of daily ATR to qualify as a sweep.
SWEEP_THRESHOLDS = {
    "crypto":      20,   # Crypto is highly volatile — needs a larger move
    "stock":       15,   # US & UK equities
    "forex":       10,   # FX pairs move in tighter ranges
    "index":       12,   # Indices sit between stocks and forex
    "commodity":   15,   # Commodities behave similarly to stocks
}
ATR_PERIOD = 14   # Number of days to calculate ATR over


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
