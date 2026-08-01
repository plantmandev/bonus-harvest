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

# Run harvest — capture exit code without letting set -e kill the script
HARVEST_EXIT=0
python3 -m "casinos.$CASINO_KEY" >> "$LOG_FILE" 2>&1 || HARVEST_EXIT=$?

if [ "$HARVEST_EXIT" -eq 0 ]; then
    log "Harvest completed successfully"
else
    log "Harvest failed — exit code $HARVEST_EXIT"
    python3 "$SCRIPT_DIR/notify_failure.py" --casino "$CASINO_KEY" --log "$LOG_FILE" --exit-code "$HARVEST_EXIT" || true
fi

# ── Schedule the next run regardless of harvest outcome ───────────────────────
CMD="bash $SCRIPT_DIR/run_casino.sh $CASINO_KEY"

# Guard against duplicate at-jobs if one for this casino is already pending
# (e.g. a manual re-run, or atd catching up on a backlog after downtime).
# atq lists the currently-executing job too (status '='), which is this very
# script — exclude it or every run would find "itself" and never reschedule.
if atq | awk '$7 == "a" {print $1}' | xargs -r -I{} at -c {} 2>/dev/null | grep -q "run_casino.sh $CASINO_KEY"; then
    log "An at job for $CASINO_KEY is already queued — skipping scheduling"
    exit "$HARVEST_EXIT"
fi

if [ -f "$NEXT_RUN_FILE" ]; then
    NEXT_RUN=$(cat "$NEXT_RUN_FILE")
    AT_EPOCH=$(date -d "$NEXT_RUN" +%s 2>/dev/null) || {
        log "Could not parse next run time '$NEXT_RUN' — falling back to 24h"
        echo "$CMD" | at "now + 24 hours" 2>>"$LOG_FILE" \
            && log "Fallback: next run scheduled 24h from now" \
            || log "WARNING: could not schedule via at"
        exit "$HARVEST_EXIT"
    }
    if [ "$AT_EPOCH" -le "$(date +%s)" ]; then
        echo "$CMD" | at "now + 4 hours" 2>>"$LOG_FILE" \
            && log "Next run scheduled in 4h (overdue timestamp)" \
            || log "WARNING: could not schedule via at"
    else
        AT_TIME=$(date -d "$NEXT_RUN" '+%H:%M %Y-%m-%d')
        echo "$CMD" | at "$AT_TIME" 2>>"$LOG_FILE" \
            && log "Next run scheduled for $NEXT_RUN" \
            || log "WARNING: could not schedule via at"
    fi
else
    log "No next_run file found — scheduling fallback in 24h"
    echo "$CMD" | at "now + 24 hours" 2>>"$LOG_FILE" \
        && log "Fallback: next run scheduled 24h from now" \
        || log "WARNING: could not schedule via at"
fi

exit "$HARVEST_EXIT"
