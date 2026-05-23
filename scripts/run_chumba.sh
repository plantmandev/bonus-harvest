#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/chumba_$(date +%Y-%m-%d).log"

mkdir -p "$LOG_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

log "Starting Chumba Casino harvest"

DISPLAY_NUM=99
export DISPLAY=:$DISPLAY_NUM
if ! pgrep -f "Xvfb :$DISPLAY_NUM" > /dev/null; then
    Xvfb ":$DISPLAY_NUM" -screen 0 1280x720x24 -ac &
    XVFB_PID=$!
    trap "kill $XVFB_PID 2>/dev/null || true" EXIT
    sleep 1
fi

source "$PROJECT_DIR/bonus-harvest/bin/activate"

cd "$PROJECT_DIR"
if python3 -m casinos.chumba_casino >> "$LOG_FILE" 2>&1; then
    log "Harvest completed successfully"
else
    EXIT_CODE=$?
    log "Harvest failed — exit code $EXIT_CODE"
    python3 "$SCRIPT_DIR/notify_failure.py" --casino "Chumba Casino" --log "$LOG_FILE" --exit-code "$EXIT_CODE" || true
    exit "$EXIT_CODE"
fi
