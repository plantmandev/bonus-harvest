#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/chumba_$(date +%Y-%m-%d_%H%M).log"
NEXT_RUN_FILE="$LOG_DIR/chumba_next_run.txt"

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

# ── schedule next run ─────────────────────────────────────────────────────────
if [ -f "$NEXT_RUN_FILE" ]; then
    NEXT_RUN=$(cat "$NEXT_RUN_FILE")
    rm "$NEXT_RUN_FILE"

    # Convert ISO timestamp to `at` format: HH:MM YYYY-MM-DD
    AT_TIME=$(date -d "$NEXT_RUN" '+%H:%M %Y-%m-%d' 2>/dev/null) || {
        log "Could not parse next run time '$NEXT_RUN' — skipping auto-schedule"
        exit 0
    }

    echo "bash $SCRIPT_DIR/run_chumba.sh" | at "$AT_TIME" 2>>"$LOG_FILE"
    log "Next run scheduled for $NEXT_RUN"
else
    log "No next run file found — skipping auto-schedule"
fi
