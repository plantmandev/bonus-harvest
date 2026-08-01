#!/usr/bin/env python3
"""Live terminal dashboard for bonus-harvest.

Usage:
    python3 dashboard.py
    ./dashboard.py          (after chmod +x dashboard.py)
"""

import sqlite3
import subprocess
import time
from datetime import datetime
from pathlib import Path

from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

PROJECT_DIR = Path(__file__).parent
LOG_DIR     = PROJECT_DIR / 'logs'
DB_PATH     = PROJECT_DIR / 'data_analysis' / 'balances.db'

REFRESH_SECONDS = 30

CASINOS = [
    {'key': 'stake_us',      'display': 'Stake.us',      'color': 'green'},
    {'key': 'fortune_wins',  'display': 'Fortune Wins',  'color': 'yellow'},
    {'key': 'acebet_cc',     'display': 'AceBet.cc',     'color': 'cyan'},
    {'key': 'chumba_casino', 'display': 'Chumba Casino', 'color': 'white', 'disabled': True},
]


# ── data helpers ──────────────────────────────────────────────────────────────

def _read_db(casino_key: str):
    """Return (balance_float, currency_str, recorded_at_iso) or (None, None, None)."""
    try:
        conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
        row  = conn.execute(
            'SELECT balance, currency, recorded_at FROM balances '
            'WHERE casino = ? AND balance IS NOT NULL ORDER BY recorded_at DESC LIMIT 1',
            (casino_key,),
        ).fetchone()
        conn.close()
        return row if row else (None, None, None)
    except Exception:
        return None, None, None


def _next_run_info(casino_key: str):
    """Return (next_run_datetime | None, time_until_markup)."""
    path = LOG_DIR / f'{casino_key}_next_run.txt'
    if not path.exists():
        return None, '[dim]—[/dim]'
    try:
        next_run = datetime.fromisoformat(path.read_text().strip())
        secs     = (next_run - datetime.now()).total_seconds()
        if secs < -3600:
            markup = '[bold red]OVERDUE[/bold red]'
        elif secs < 0:
            markup = '[yellow]NOW[/yellow]'
        else:
            h, rem = divmod(int(secs), 3600)
            m      = rem // 60
            markup = f'{h}h {m:02d}m'
        return next_run, markup
    except Exception:
        return None, '[dim]—[/dim]'


_ERROR_LABELS = {
    'GmailAuthExpired':    '[red]Gmail OAuth expired[/red]',
    'AccountVerification': '[yellow]Account verification needed[/yellow]',
    'Unknown':             '[red]FAILED[/red]',
}


def _last_harvest_status(casino_key: str):
    """Return (timestamp_str, status_markup) from the status file written by BaseCasino.run()."""
    status_file = LOG_DIR / f'{casino_key}_status.txt'
    if not status_file.exists():
        return '—', '[dim]—[/dim]'
    try:
        parts  = status_file.read_text().strip().split(' ', 1)
        code   = parts[0]   # 'OK', 'FAILED:GmailAuthExpired', etc.
        ts     = parts[1] if len(parts) > 1 else '—'
        if code == 'OK':
            return ts, '[green]OK[/green]'
        if code.startswith('FAILED:'):
            error_type = code.split(':', 1)[1]
            markup = _ERROR_LABELS.get(error_type, f'[red]FAILED ({error_type})[/red]')
            return ts, markup
        return ts, '[red]FAILED[/red]'
    except Exception:
        return '—', '[dim]—[/dim]'


def _gmail_status() -> tuple[str, str]:
    """Return (timestamp_str, status_markup)."""
    path = LOG_DIR / 'gmail_auth_status.txt'
    if not path.exists():
        return '—', '[yellow]UNKNOWN[/yellow]'
    try:
        parts  = path.read_text().strip().split(' ', 1)
        status = parts[0]
        ts     = parts[1] if len(parts) > 1 else '—'
        if status == 'OK':
            return ts, '[green]OK[/green]'
        return ts, '[bold red]EXPIRED — run: python3 -m auth.gmail[/bold red]'
    except Exception:
        return '—', '[yellow]?[/yellow]'


def _at_queue():
    """Return list of (job_id, time_str, user) tuples from atq."""
    try:
        result = subprocess.run(['atq'], capture_output=True, text=True, timeout=5)
        lines  = [l for l in result.stdout.strip().splitlines() if l]
        return lines if lines else []
    except Exception:
        return []


# ── layout builder ────────────────────────────────────────────────────────────

def build_layout() -> Layout:
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Casino status table
    tbl = Table(
        title=f'[bold]Bonus Harvest[/bold]  ·  {now}  ·  refresh {REFRESH_SECONDS}s',
        expand=True,
        show_lines=True,
        header_style='bold cyan',
        border_style='blue',
    )
    tbl.add_column('Casino',       style='bold', min_width=14)
    tbl.add_column('Balance',      min_width=18)
    tbl.add_column('Recorded',     min_width=16)
    tbl.add_column('Next Run',     min_width=11, justify='center')
    tbl.add_column('In',           min_width=10, justify='right')
    tbl.add_column('Last Harvest', min_width=11, justify='center')
    tbl.add_column('Status',       min_width=8,  justify='center')

    for c in CASINOS:
        key      = c['key']
        color    = c.get('color', 'white')
        disabled = c.get('disabled', False)
        label    = Text(c['display'], style=f'bold {color}')

        if disabled:
            tbl.add_row(label, '[dim]disabled[/dim]', '—', '—', '—', '—', '[dim]OFF[/dim]')
            continue

        balance, currency, recorded_at = _read_db(key)
        if balance is not None:
            bal_str = f'{balance:,.2f} {currency}'
        else:
            bal_str = '[dim]—[/dim]'
        rec_str = recorded_at[:16].replace('T', ' ') if recorded_at else '[dim]—[/dim]'

        next_dt, until_markup = _next_run_info(key)
        next_str = next_dt.strftime('%m-%d %H:%M') if next_dt else '[dim]—[/dim]'

        last_ts, status_markup = _last_harvest_status(key)

        tbl.add_row(
            label,
            bal_str,
            rec_str,
            next_str,
            Text.from_markup(until_markup),
            last_ts,
            Text.from_markup(status_markup),
        )

    # Gmail auth row
    gmail_ts, gmail_markup = _gmail_status()
    tbl.add_section()
    tbl.add_row(
        Text('Gmail OAuth', style='bold magenta'),
        '[dim]—[/dim]', '[dim]—[/dim]', '[dim]—[/dim]', '[dim]—[/dim]',
        gmail_ts,
        Text.from_markup(gmail_markup),
    )

    # at queue
    at_lines = _at_queue()
    if at_lines:
        at_text = '\n'.join(at_lines)
    else:
        at_text = '[dim](no jobs scheduled)[/dim]'

    layout = Layout()
    layout.split_column(
        Layout(tbl, name='main', ratio=4),
        Layout(
            Panel(at_text, title='[dim]at queue[/dim]', border_style='dim', padding=(0, 1)),
            name='queue',
            ratio=1,
        ),
    )
    return layout


def main():
    console = Console()
    with Live(
        build_layout(),
        console=console,
        screen=True,
        refresh_per_second=4,
    ) as live:
        try:
            while True:
                time.sleep(REFRESH_SECONDS)
                live.update(build_layout())
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
