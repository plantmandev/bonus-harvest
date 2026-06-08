#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/daily_report_$(date +%Y-%m-%d).log"

mkdir -p "$LOG_DIR"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

log "Sending daily report..."
source "$PROJECT_DIR/bonus-harvest/bin/activate"
cd "$PROJECT_DIR"

if python3 -m data_analysis.report >> "$LOG_FILE" 2>&1; then
    log "Daily report sent successfully"
else
    log "Daily report failed — exit code $?"
fi
