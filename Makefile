.PHONY: setup db-start db-stop bot api dashboard install

# ── First-time setup ──────────────────────────────────────────────────────────
setup:
	@echo "→ Copying .env.example to .env (skip if already exists)"
	@cp -n .env.example .env || true
	@echo "→ Installing Node dependencies"
	pnpm install
	@echo "→ Installing Python dependencies"
	pip install -r bot/polymarket-bot/requirements.txt
	@echo ""
	@echo "Done. Edit .env, then run: make db-start && make bot"

# ── Database ──────────────────────────────────────────────────────────────────
db-start:
	docker compose up -d postgres
	@echo "Postgres running on localhost:5432"

db-stop:
	docker compose stop postgres

# ── Bot (pipeline scheduler) ──────────────────────────────────────────────────
bot:
	cd bot/polymarket-bot && python scheduler.py

# ── API server ────────────────────────────────────────────────────────────────
api:
	cd artifacts/api-server && pnpm dev

# ── Dashboard (Vite dev server) ───────────────────────────────────────────────
dashboard:
	cd artifacts/dashboard && pnpm dev

# ── Install / update dependencies ────────────────────────────────────────────
install:
	pnpm install
	pip install -r bot/polymarket-bot/requirements.txt
