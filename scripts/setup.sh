#!/usr/bin/env bash
# Run once on the server to configure daily Stake.us harvesting.
# Usage: sudo bash scripts/setup.sh
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_USER="${SUDO_USER:-$(whoami)}"
VENV="$PROJECT_DIR/.venv"

# ── system packages ──────────────────────────────────────────────────────────
echo "[setup] Installing system packages..."
apt-get update -qq
apt-get install -y --no-install-recommends xvfb wget gnupg ca-certificates at python3 python3-venv
systemctl enable --now atd

if ! command -v google-chrome &>/dev/null && ! command -v google-chrome-stable &>/dev/null; then
    echo "[setup] Installing Google Chrome..."
    wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    apt-get install -y /tmp/chrome.deb
    rm /tmp/chrome.deb
else
    echo "[setup] Chrome already installed — skipping"
fi

# ── python venv ───────────────────────────────────────────────────────────────
echo "[setup] Setting up Python venv at $VENV..."
if [ ! -f "$VENV/bin/activate" ]; then
    python3 -m venv "$VENV"
fi
# shellcheck source=/dev/null
source "$VENV/bin/activate"
pip install -q --upgrade pip
pip install -q -r "$PROJECT_DIR/requirements.txt"

# ── .env ──────────────────────────────────────────────────────────────────────
ENV_FILE="$PROJECT_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "[setup] Creating .env template — fill in your credentials"
    cat > "$ENV_FILE" <<'EOF'
STAKE_USERNAME=
STAKE_PASSWORD=
SERVER_MODE=true
# PROXY_SERVER=
EOF
elif ! grep -q "SERVER_MODE" "$ENV_FILE"; then
    echo "SERVER_MODE=true" >> "$ENV_FILE"
fi

# ── cron jobs ─────────────────────────────────────────────────────────────────
# The harvest schedule itself runs via `at`: run_casino.sh re-queues its own
# next run every time it finishes (see scripts/run_casino.sh). Cron only needs
# to send the daily report and re-queue any casino whose `at` job went missing.
echo "[setup] Installing crontab entries for $RUN_USER..."
REPORT_LINE="0 8 * * * bash $PROJECT_DIR/scripts/send_daily_report.sh"
REQUEUE_LINE="0 6 * * * bash $PROJECT_DIR/scripts/requeue.sh >> $PROJECT_DIR/logs/requeue_\$(date +\%Y-\%m-\%d).log 2>&1"

EXISTING_CRON="$(crontab -u "$RUN_USER" -l 2>/dev/null || true)"
NEW_CRON="$EXISTING_CRON"
if ! grep -qF "send_daily_report.sh" <<<"$EXISTING_CRON"; then
    NEW_CRON="$(printf '%s\n%s\n%s' "$NEW_CRON" "# Daily balance report — 8am MT" "$REPORT_LINE")"
fi
if ! grep -qF "requeue.sh" <<<"$EXISTING_CRON"; then
    NEW_CRON="$(printf '%s\n%s\n%s' "$NEW_CRON" "# Watchdog — re-queues any casino at job that went missing" "$REQUEUE_LINE")"
fi
printf '%s\n' "$NEW_CRON" | sed '/^$/d' | crontab -u "$RUN_USER" -

# ── summary ───────────────────────────────────────────────────────────────────
echo ""
echo "================================================================"
echo "  Setup complete"
echo "================================================================"
echo "  Project : $PROJECT_DIR"
echo "  Venv    : $VENV"
echo "  Logs    : $PROJECT_DIR/logs/"
echo ""
echo "  Next steps:"
echo "    1. Fill in credentials:  nano $ENV_FILE"
echo "    2. Copy GmailVerification/token.json from your local machine"
echo "    3. Test a manual run:    bash $PROJECT_DIR/scripts/run_stake.sh"
echo "       (this creates the first *_next_run.txt and queues the next"
echo "        at-job — nothing runs on a schedule until step 3 happens once)"
echo "    4. Watch queued jobs:    atq"
echo "    5. Check crontab:        crontab -u $RUN_USER -l"
echo "================================================================"
