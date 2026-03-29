# config/secrets.example.py
# =============================================
# COPY THIS FILE → rename it secrets.py
# Then fill in your real API keys.
# secrets.py is in .gitignore so it stays private.
# NEVER commit secrets.py to GitHub.
# =============================================

# Binance (for crypto — get from binance.com/en/my/settings/api-management)
BINANCE_API_KEY    = "YOUR_BINANCE_API_KEY_HERE"
BINANCE_API_SECRET = "YOUR_BINANCE_SECRET_HERE"

# Alpha Vantage (optional — for stocks/forex with more data)
# Free key at: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_KEY = "YOUR_ALPHA_VANTAGE_KEY_HERE"

# Telegram (optional — for alerts to your phone)
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID   = "YOUR_TELEGRAM_CHAT_ID"
