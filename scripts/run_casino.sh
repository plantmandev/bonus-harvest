#!/usr/bin/env bash
set -euo pipefail

CASINO_KEY="${1:?Usage: run_casino.sh <casino_key>}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/${CASINO_KEY}_$(date +%Y-%m-%d_%H%M).log"
NEXT_RUN_FILE="$LOG_DIR/${CASINO_KEY}_next_run.txt"

mkdir -p "$LOG_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

log "Starting $CASINO_KEY harvest"

DISPLAY_NUM=99
export DISPLAY=:$DISPLAY_NUM
if ! pgrep -f "Xvfb :$DISPLAY_NUM" > /dev/null; then
    Xvfb ":$DISPLAY_NUM" -screen 0 1280x720x24 -ac &
    XVFB_PID=$!
    trap "kill $XVFB_PID 2>/dev/null || true" EXIT
    sleep 1
fi

source "$PROJECT_DIR/.venv/bin/activate"

cd "$PROJECT_DIR"
if python3 -m "casinos.$CASINO_KEY" >> "$LOG_FILE" 2>&1; then
    log "Harvest completed successfully"
else
    EXIT_CODE=$?
    log "Harvest failed — exit code $EXIT_CODE"
    python3 "$SCRIPT_DIR/notify_failure.py" --casino "$CASINO_KEY" --log "$LOG_FILE" --exit-code "$EXIT_CODE" || true
    exit "$EXIT_CODE"
fi

# ── schedule next precise run via at ─────────────────────────────────────────
if [ -f "$NEXT_RUN_FILE" ]; then
    NEXT_RUN=$(cat "$NEXT_RUN_FILE")
    AT_EPOCH=$(date -d "$NEXT_RUN" +%s 2>/dev/null) || {
        log "Could not parse next run time '$NEXT_RUN' — skipping auto-schedule"
        exit 0
    }
    CMD="bash $SCRIPT_DIR/run_casino.sh $CASINO_KEY"
    if [ "$AT_EPOCH" -le "$(date +%s)" ]; then
        echo "$CMD" | at "now + 1 minute" 2>>"$LOG_FILE" \
            && log "Next run scheduled immediately (stale timestamp)" \
            || log "WARNING: could not schedule via at"
    else
        AT_TIME=$(date -d "$NEXT_RUN" '+%H:%M %Y-%m-%d')
        echo "$CMD" | at "$AT_TIME" 2>>"$LOG_FILE" \
            && log "Next run scheduled for $NEXT_RUN" \
            || log "WARNING: could not schedule via at"
    fi
else
    log "No next run file — re-run run_all.sh to bootstrap"
fi
