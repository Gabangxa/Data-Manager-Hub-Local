# scheduler.py — continuous pipeline runner + HTTP keep-alive for Replit
#
# Starts a Flask server in a background thread (keeps Replit "always on" alive),
# then runs the pipeline on a loop.
#
# Run pattern:
#   Run 1, 13, 25, ...  → full run including market scanner
#   All other runs      → collect + analyse only (faster, cheaper on API)

import logging
import os
import sys
import time
from datetime import datetime, timezone

# Load .env file if present (local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed — env vars must be set externally

# ── Logging (must happen before any other imports that use loggers) ────────────
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(f"logs/run_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("scheduler")

from config import POLL_INTERVAL_SECONDS
import alerts

# Refresh watchlist every N runs  (default: every 12 runs ≈ 1h at 5min interval)
SCAN_INTERVAL_RUNS = 12


def main():
    # Import here so logging is configured first
    from main import run_pipeline

    logger.info("=" * 60)
    logger.info("polymarket-bot starting up")
    logger.info(f"Poll interval : {POLL_INTERVAL_SECONDS}s")
    logger.info(f"Scan interval : every {SCAN_INTERVAL_RUNS} runs")
    logger.info("=" * 60)

    # Optional HTTP keep-alive server (set ENABLE_KEEPALIVE=true on Replit).
    # Not needed when running locally.
    if os.environ.get("ENABLE_KEEPALIVE", "").lower() == "true":
        from server import start_server
        port = int(os.environ.get("BOT_PORT", 5001))
        start_server(host="0.0.0.0", port=port)
        logger.info(f"Keep-alive server started on port {port}")

    run_count = 0

    while True:
        run_count += 1
        skip_scan = (run_count % SCAN_INTERVAL_RUNS != 1)

        logger.info(f"\n{'='*40}")
        logger.info(
            f"Run #{run_count} at {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}"
            + (" [+scan]" if not skip_scan else "")
        )

        try:
            run_pipeline(skip_scan=skip_scan)
        except Exception as e:
            logger.error(f"Pipeline run #{run_count} failed: {e}", exc_info=True)
            alerts.pipeline_crashed(run_count, e)

        logger.info(f"Sleeping {POLL_INTERVAL_SECONDS}s...")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
