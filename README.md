# Data-Manager-Hub — Local

A self-hosted version of the Polymarket analysis bot + dashboard.

> **Read-only by design.** No orders are placed. Alpha comes from market structure
> (spread, over-round, liquidity shocks) not from predicting real-world outcomes.

---

## What's inside

| Component | Path | What it does |
|---|---|---|
| **Bot** | `bot/polymarket-bot/` | Polls Polymarket APIs every 5 min, stores snapshots in Postgres, runs 3 strategy engines |
| **API server** | `artifacts/api-server/` | Express.js REST API over Postgres |
| **Dashboard** | `artifacts/dashboard/` | React/Vite UI — markets, signals, performance, docs |

### Strategy engines

| Engine | Signal condition |
|---|---|
| `spread_harvesting` | Bid-ask spread > 2× taker fee — market maker opportunity |
| `neg_risk_overround` | Sum of YES prices across a neg-risk event > 1.0 — arbitrage |
| `mean_reversion` | Sharp price move on thin liquidity — reversal candidate |

---

## Prerequisites

- Python 3.11+
- Node.js 20+ with pnpm (`npm i -g pnpm`)
- Docker (for the managed Postgres — or supply your own)

---

## Quick start

```bash
# 1. Clone
git clone https://github.com/Gabangxa/Data-Manager-Hub-Local.git
cd Data-Manager-Hub-Local

# 2. Install everything + copy .env
make setup

# 3. Edit .env (DATABASE_URL is pre-filled for the Docker Postgres below)
#    Add DISCORD_WEBHOOK_URL if you want crash/streak alerts.
nano .env

# 4. Start Postgres
make db-start

# 5. In separate terminals:
make bot        # Python pipeline scheduler
make api        # Express API  (http://localhost:8080)
make dashboard  # Vite dev UI  (http://localhost:5173)
```

The bot initialises the database schema on first run — no manual migration needed.

---

## Environment variables

See `.env.example` for the full list with explanations.

| Variable | Required | Default | Notes |
|---|---|---|---|
| `DATABASE_URL` | Yes | — | Postgres connection string |
| `POLL_INTERVAL_SECONDS` | No | `300` | Bot polling frequency |
| `DISCORD_WEBHOOK_URL` | No | — | Discord crash + streak alerts |
| `ENABLE_KEEPALIVE` | No | `false` | Set `true` on Replit only |
| `PORT` | No | `8080` | API server port |

---

## Project structure

```
.
├── bot/polymarket-bot/     # Python bot
│   ├── scheduler.py        # Main loop
│   ├── main.py             # Pipeline orchestrator
│   ├── db.py               # Postgres helpers
│   ├── api.py              # Polymarket API client
│   ├── config.py           # All constants
│   ├── alerts.py           # Discord notifications
│   └── agents/             # Strategy engines + data collection
│       ├── market_scanner.py
│       ├── data_collector.py
│       ├── spread_engine.py
│       ├── neg_risk_engine.py
│       ├── reversion_engine.py
│       └── outcome_tracker.py
├── artifacts/
│   ├── api-server/         # Express.js REST API
│   └── dashboard/          # React dashboard (Vite)
├── docker-compose.yml      # Postgres service
├── Makefile                # Common dev commands
└── .env.example            # Environment variable template
```

---

## Deploying to a server / VPS

The bot is a plain Python process; the API and dashboard are Node processes.
Any system with Docker + Python 3.11 + Node 20 works.

Example with systemd or PM2:
```bash
# Bot
cd bot/polymarket-bot && python scheduler.py

# API
cd artifacts/api-server && pnpm start

# Dashboard (build for production)
cd artifacts/dashboard && pnpm build
# Serve dist/ with nginx or any static host
```

---

## License

MIT
