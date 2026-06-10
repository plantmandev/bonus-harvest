#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/harvest_$(date +%Y-%m-%d).log"

mkdir -p "$LOG_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

log "Starting harvest for all sites"

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

# Capture exit code without letting it kill the script — report must always send
HARVEST_EXIT=0
python3 run_all.py >> "$LOG_FILE" 2>&1 || HARVEST_EXIT=$?

if [ "$HARVEST_EXIT" -eq 0 ]; then
    log "All sites completed successfully"
else
    log "Harvest had failures — exit code $HARVEST_EXIT"
    python3 "$SCRIPT_DIR/notify_failure.py" --casino "Bonus Harvest" --log "$LOG_FILE" --exit-code "$HARVEST_EXIT" || true
fi

# Always send the daily report regardless of harvest outcome
log "Sending daily balance report..."
python3 -m data_analysis.report >> "$LOG_FILE" 2>&1 && log "Report sent" || log "Report failed — check log"

# Schedule each casino's next precise run via at
_schedule_casino() {
    local KEY="$1" FILE="$2"
    local NEXT_RUN AT_TIME AT_EPOCH NOW_EPOCH CMD
    NEXT_RUN=$(cat "$FILE")
    AT_EPOCH=$(date -d "$NEXT_RUN" +%s 2>/dev/null) || {
        log "Could not parse next run for $KEY: '$NEXT_RUN' — skipping"
        return
    }
    NOW_EPOCH=$(date +%s)
    CMD="bash $SCRIPT_DIR/run_casino.sh $KEY"
    if [ "$AT_EPOCH" -le "$NOW_EPOCH" ]; then
        # Stale timestamp — run soon instead of blocking on a past time
        echo "$CMD" | at "now + 1 minute" 2>>"$LOG_FILE" \
            && log "Next $KEY run scheduled immediately (stale timestamp)" \
            || log "WARNING: could not schedule $KEY via at"
    else
        AT_TIME=$(date -d "$NEXT_RUN" '+%H:%M %Y-%m-%d')
        echo "$CMD" | at "$AT_TIME" 2>>"$LOG_FILE" \
            && log "Next $KEY run scheduled for $NEXT_RUN" \
            || log "WARNING: could not schedule $KEY via at"
    fi
}

for NEXT_RUN_FILE in "$LOG_DIR"/*_next_run.txt; do
    [ -f "$NEXT_RUN_FILE" ] || continue
    _schedule_casino "$(basename "$NEXT_RUN_FILE" _next_run.txt)" "$NEXT_RUN_FILE"
done

exit "$HARVEST_EXIT"
