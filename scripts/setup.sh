#!/usr/bin/env bash
# Run once on the server to configure daily Stake.us harvesting.
# Usage: sudo bash scripts/setup.sh
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_USER="${SUDO_USER:-$(whoami)}"
SERVICE_DIR="/etc/systemd/system"
VENV="$PROJECT_DIR/.venv"

# ── system packages ──────────────────────────────────────────────────────────
echo "[setup] Installing system packages..."
apt-get update -qq
apt-get install -y --no-install-recommends xvfb wget gnupg ca-certificates python3 python3-venv

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

# ── systemd service + timer ───────────────────────────────────────────────────
echo "[setup] Installing systemd units..."
sed "s|YOUR_USER|$RUN_USER|g; s|/path/to/bonus-harvest|$PROJECT_DIR|g" \
    "$PROJECT_DIR/scripts/stake-harvest.service" > "$SERVICE_DIR/stake-harvest.service"

cp "$PROJECT_DIR/scripts/stake-harvest.timer" "$SERVICE_DIR/stake-harvest.timer"

systemctl daemon-reload
systemctl enable --now stake-harvest.timer

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
echo "    4. Watch the timer:      systemctl list-timers stake-harvest.timer"
echo "================================================================"
