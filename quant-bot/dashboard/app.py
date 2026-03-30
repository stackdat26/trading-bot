# dashboard/app.py
# =============================================
# QuantBot Web Dashboard
#
# Runs on port 5000. Shows live signals,
# stats, and bot status in a clean webpage.
#
# Routes:
#   /           — Main dashboard (HTML)
#   /api/signals — Recent signals (JSON)
#   /api/stats   — Bot stats (JSON)
#   /webhook     — TradingView webhook (POST)
# =============================================

import os
import threading
from flask import Flask, jsonify, render_template_string
from core.signal_store import get_signals, get_stats
from core.webhook_receiver import webhook_bp
from core.subscriber_store import subscriber_count
from config.settings import (
    CRYPTO_SYMBOLS, STOCK_SYMBOLS, FOREX_SYMBOLS, INDEX_SYMBOLS
)

app = Flask(__name__)
app.register_blueprint(webhook_bp)

ALL_SYMBOLS = CRYPTO_SYMBOLS + STOCK_SYMBOLS + FOREX_SYMBOLS + INDEX_SYMBOLS

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>QuantBot Dashboard</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background: #0d0f14;
      color: #e2e8f0;
      font-family: 'Segoe UI', system-ui, sans-serif;
      min-height: 100vh;
      padding: 24px;
    }

    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 28px;
      padding-bottom: 20px;
      border-bottom: 1px solid #1e2330;
    }

    header h1 {
      font-size: 1.5rem;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: #22c55e;
      display: inline-block;
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50%       { opacity: 0.4; }
    }

    .uptime {
      font-size: 0.8rem;
      color: #64748b;
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 16px;
      margin-bottom: 28px;
    }

    .stat-card {
      background: #131720;
      border: 1px solid #1e2330;
      border-radius: 12px;
      padding: 20px;
      text-align: center;
    }

    .stat-card .value {
      font-size: 2rem;
      font-weight: 700;
      color: #fff;
      margin-bottom: 4px;
    }

    .stat-card .label {
      font-size: 0.75rem;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .stat-card.buy  .value { color: #22c55e; }
    .stat-card.sell .value { color: #ef4444; }
    .stat-card.subs .value { color: #3b82f6; }

    .section-title {
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #64748b;
      margin-bottom: 12px;
    }

    .symbols-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 28px;
    }

    .symbol-tag {
      background: #1e2330;
      border-radius: 6px;
      padding: 5px 12px;
      font-size: 0.8rem;
      color: #94a3b8;
    }

    .signals-table-wrap {
      background: #131720;
      border: 1px solid #1e2330;
      border-radius: 12px;
      overflow: hidden;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
    }

    thead tr {
      background: #1a1f2e;
      text-transform: uppercase;
      font-size: 0.7rem;
      letter-spacing: 0.06em;
      color: #64748b;
    }

    th, td {
      padding: 12px 16px;
      text-align: left;
      border-bottom: 1px solid #1e2330;
    }

    tr:last-child td { border-bottom: none; }

    tbody tr:hover { background: #1a1f2e; }

    .badge {
      display: inline-block;
      padding: 3px 10px;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 600;
    }

    .badge.buy  { background: #14532d; color: #4ade80; }
    .badge.sell { background: #450a0a; color: #f87171; }
    .badge.tv   { background: #1e3a5f; color: #60a5fa; font-size: 0.65rem; }

    .conf-bar {
      width: 80px;
      height: 6px;
      background: #1e2330;
      border-radius: 3px;
      overflow: hidden;
      display: inline-block;
      vertical-align: middle;
      margin-left: 8px;
    }

    .conf-fill {
      height: 100%;
      border-radius: 3px;
      background: linear-gradient(90deg, #3b82f6, #22c55e);
    }

    .empty-state {
      text-align: center;
      padding: 60px 20px;
      color: #475569;
    }

    .empty-state p { margin-top: 8px; font-size: 0.85rem; }

    .refresh-note {
      text-align: right;
      font-size: 0.75rem;
      color: #334155;
      margin-top: 16px;
    }

    .telegram-btn {
      display: inline-block;
      background: #0088cc;
      color: #fff;
      padding: 10px 20px;
      border-radius: 8px;
      text-decoration: none;
      font-size: 0.85rem;
      font-weight: 600;
      margin-top: 16px;
    }

    .telegram-btn:hover { background: #0077b5; }

    .webhook-info {
      background: #131720;
      border: 1px solid #1e2330;
      border-radius: 12px;
      padding: 20px;
      margin-top: 24px;
      font-size: 0.82rem;
      color: #64748b;
      line-height: 1.7;
    }

    .webhook-info code {
      background: #1e2330;
      padding: 2px 8px;
      border-radius: 4px;
      color: #60a5fa;
      font-size: 0.8rem;
    }
  </style>
</head>
<body>

<header>
  <h1>
    <span class="dot"></span>
    QuantBot Dashboard
  </h1>
  <div class="uptime">
    Started: <span id="started">—</span> &nbsp;|&nbsp; Uptime: <span id="uptime">—</span>
  </div>
</header>

<!-- Stats -->
<div class="stats-grid">
  <div class="stat-card">
    <div class="value" id="total">—</div>
    <div class="label">Total Signals</div>
  </div>
  <div class="stat-card buy">
    <div class="value" id="buys">—</div>
    <div class="label">Buy Signals</div>
  </div>
  <div class="stat-card sell">
    <div class="value" id="sells">—</div>
    <div class="label">Sell Signals</div>
  </div>
  <div class="stat-card subs">
    <div class="value" id="subs">—</div>
    <div class="label">Subscribers</div>
  </div>
</div>

<!-- Symbols -->
<div class="section-title">Watching {{ symbol_count }} Symbols</div>
<div class="symbols-row">
  {% for s in symbols %}
  <span class="symbol-tag">{{ s }}</span>
  {% endfor %}
</div>

<!-- Signals Table -->
<div class="section-title">Live Signals</div>
<div class="signals-table-wrap">
  <table>
    <thead>
      <tr>
        <th>Time</th>
        <th>Symbol</th>
        <th>Action</th>
        <th>Confidence</th>
        <th>Entry</th>
        <th>Stop Loss</th>
        <th>Take Profit</th>
        <th>RSI</th>
        <th>Source</th>
      </tr>
    </thead>
    <tbody id="signals-body">
      <tr>
        <td colspan="9">
          <div class="empty-state">
            ⏳ Loading signals...
          </div>
        </td>
      </tr>
    </tbody>
  </table>
</div>

<div class="refresh-note">Auto-refreshes every 30 seconds</div>

<!-- Telegram -->
<div style="margin-top: 24px;">
  <div class="section-title">Subscribe to Signals</div>
  <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 8px;">
    Get every BUY/SELL alert sent directly to your Telegram.
  </p>
  <a class="telegram-btn" href="https://t.me/{{ bot_username }}" target="_blank">
    📲 Subscribe on Telegram
  </a>
</div>

<!-- Webhook Info -->
<div class="webhook-info">
  <strong style="color: #e2e8f0;">📡 TradingView Webhook</strong><br>
  Requires TradingView Pro or above. Set your alert webhook URL to:<br>
  <code>{{ webhook_url }}/webhook</code><br><br>
  Alert message format (paste this into TradingView alert message box):<br>
  <code>{"symbol":"{{ticker}}","action":"BUY","price":{{close}},"stop_loss":0,"take_profit":0}</code>
</div>

<script>
  async function loadStats() {
    try {
      const r = await fetch('/api/stats');
      const d = await r.json();
      document.getElementById('total').textContent   = d.total_signals;
      document.getElementById('buys').textContent    = d.buy_signals;
      document.getElementById('sells').textContent   = d.sell_signals;
      document.getElementById('subs').textContent    = d.subscribers;
      document.getElementById('uptime').textContent  = d.uptime;
      document.getElementById('started').textContent = d.started_at;
    } catch(e) {}
  }

  async function loadSignals() {
    try {
      const r = await fetch('/api/signals');
      const signals = await r.json();
      const tbody = document.getElementById('signals-body');

      if (!signals.length) {
        tbody.innerHTML = `<tr><td colspan="9">
          <div class="empty-state">
            ⬜ No signals yet — next scan in &lt;15 min
            <p>The bot scans all symbols every 15 minutes.</p>
          </div></td></tr>`;
        return;
      }

      tbody.innerHTML = signals.map(s => {
        const action = s.action || 'BUY';
        const conf   = s.confidence || 0;
        const src    = s.source === 'TradingView'
          ? '<span class="badge tv">TradingView</span>'
          : '';
        return `<tr>
          <td style="color:#64748b;font-size:0.78rem">${s.timestamp}</td>
          <td style="font-weight:600">${s.symbol}</td>
          <td><span class="badge ${action.toLowerCase()}">${action}</span></td>
          <td>
            ${conf}%
            <span class="conf-bar">
              <span class="conf-fill" style="width:${conf}%"></span>
            </span>
          </td>
          <td>${Number(s.entry).toFixed(4)}</td>
          <td style="color:#f87171">${s.stop_loss ? Number(s.stop_loss).toFixed(4) : '—'}</td>
          <td style="color:#4ade80">${s.take_profit ? Number(s.take_profit).toFixed(4) : '—'}</td>
          <td>${s.rsi ? Number(s.rsi).toFixed(1) : '—'}</td>
          <td>${src || '<span style="color:#334155">Bot</span>'}</td>
        </tr>`;
      }).join('');
    } catch(e) {}
  }

  function refresh() {
    loadStats();
    loadSignals();
  }

  refresh();
  setInterval(refresh, 30000);
</script>

</body>
</html>
"""


@app.route("/")
def index():
    bot_username = os.environ.get("TELEGRAM_BOT_USERNAME", "YourBotName")
    webhook_url  = os.environ.get("REPLIT_DEV_DOMAIN", "https://your-replit-url.replit.dev")
    if not webhook_url.startswith("http"):
        webhook_url = "https://" + webhook_url
    return render_template_string(
        DASHBOARD_HTML,
        symbols=ALL_SYMBOLS,
        symbol_count=len(ALL_SYMBOLS),
        bot_username=bot_username,
        webhook_url=webhook_url,
    )


@app.route("/api/signals")
def api_signals():
    return jsonify(get_signals(50))


@app.route("/api/stats")
def api_stats():
    stats = get_stats()
    stats["subscribers"] = subscriber_count()
    return jsonify(stats)


def start_dashboard():
    """
    Starts the Flask dashboard in a background daemon thread.
    Call this once from main.py.
    """
    def run():
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

    thread = threading.Thread(target=run, daemon=True, name="Dashboard")
    thread.start()
    print("🌐 Dashboard started at http://0.0.0.0:5000")
