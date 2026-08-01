#!/usr/bin/env bash
# Watchdog: ensures every active casino has an at job queued.
# Safe to run at any time — skips casinos that already have a pending at job.
# Called by cron daily and can be run manually to re-bootstrap after any outage.
#
# Usage:
#   bash scripts/requeue.sh            # check all casinos
#   bash scripts/requeue.sh stake_us   # check one casino

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/requeue_$(date +%Y-%m-%d).log"

mkdir -p "$LOG_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

log "=== requeue watchdog start ==="

# Determine which casinos to check
if [ "${1:-}" != "" ]; then
    KEYS=("$1")
else
    # Discover from next_run files
    mapfile -t KEYS < <(
        for f in "$LOG_DIR"/*_next_run.txt; do
            [ -f "$f" ] && basename "$f" _next_run.txt
        done
    )
fi

if [ "${#KEYS[@]}" -eq 0 ]; then
    log "No next_run files found — nothing to requeue"
    exit 0
fi

# Get list of commands already queued in at
AT_JOBS=$(atq 2>/dev/null | awk '{print $1}' | xargs -r -I{} at -c {} 2>/dev/null | grep "run_casino.sh" || true)

for KEY in "${KEYS[@]}"; do
    NEXT_RUN_FILE="$LOG_DIR/${KEY}_next_run.txt"
    CMD="bash $SCRIPT_DIR/run_casino.sh $KEY"

    # Skip if an at job already references this casino
    if echo "$AT_JOBS" | grep -q "run_casino.sh $KEY"; then
        NEXT_RUN=$(cat "$NEXT_RUN_FILE" 2>/dev/null || echo "unknown")
        log "$KEY: at job already queued (next_run=$NEXT_RUN) — skipping"
        continue
    fi

    if [ ! -f "$NEXT_RUN_FILE" ]; then
        log "$KEY: no next_run file — scheduling in 4h"
        echo "$CMD" | at "now + 4 hours" 2>>"$LOG_FILE" \
            && log "$KEY: queued for now+4h" \
            || log "$KEY: WARNING — could not queue via at"
        continue
    fi

    NEXT_RUN=$(cat "$NEXT_RUN_FILE")
    AT_EPOCH=$(date -d "$NEXT_RUN" +%s 2>/dev/null) || {
        log "$KEY: could not parse '$NEXT_RUN' — scheduling in 4h"
        echo "$CMD" | at "now + 4 hours" 2>>"$LOG_FILE" \
            && log "$KEY: queued for now+4h" \
            || log "$KEY: WARNING — could not queue via at"
        continue
    }

    NOW_EPOCH=$(date +%s)
    if [ "$AT_EPOCH" -le "$NOW_EPOCH" ]; then
        log "$KEY: overdue ($NEXT_RUN) — scheduling in 4h"
        echo "$CMD" | at "now + 4 hours" 2>>"$LOG_FILE" \
            && log "$KEY: queued for now+4h" \
            || log "$KEY: WARNING — could not queue via at"
    else
        AT_TIME=$(date -d "$NEXT_RUN" '+%H:%M %Y-%m-%d')
        echo "$CMD" | at "$AT_TIME" 2>>"$LOG_FILE" \
            && log "$KEY: queued for $NEXT_RUN" \
            || log "$KEY: WARNING — could not queue via at"
    fi
done

log "=== requeue watchdog done ==="
