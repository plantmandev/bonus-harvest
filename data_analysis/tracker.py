import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / 'balances.db'

# RTP from README gleaning strategy; used to estimate cash after playthrough
CASINO_META = {
    'stake_us': {
        'display':  'Stake.us',
        'rtp':      0.98,
        'currency': 'SC',
        'logo':     'https://stake.us/apple-touch-icon.png',
        'color':    '#1a9e5c',
    },
    'chumba_casino': {
        'display':  'Chumba Casino',
        'rtp':      0.9678,
        'currency': 'SC',
        'logo':     'https://lobby.chumbacasino.com/favicon.ico',
        'color':    '#e8b923',
        'disabled': True,
    },
    'fortune_coins': {
        'display':  'Fortune Coins',
        'rtp':      0.9533,
        'currency': 'FC',
        'logo':     'https://www.fortunecoins.com/favicon.ico',
        'color':    '#c0392b',
    },
    'acebet_cc': {
        'display':  'AceBet.cc',
        'rtp':      0.96,
        'currency': 'SC',
        'logo':     'https://acebet.cc/favicon.ico',
        'color':    '#2980b9',
    },
}


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS balances (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            recorded_at TEXT    NOT NULL,
            casino      TEXT    NOT NULL,
            raw_text    TEXT,
            balance     REAL,
            currency    TEXT
        )
    ''')
    conn.commit()
    return conn


def parse_balance(text: str) -> float | None:
    match = re.search(r'[\d]+\.?\d*', text.replace(',', ''))
    return float(match.group()) if match else None


def record(casino: str, raw_text: str):
    meta     = CASINO_META.get(casino, {})
    currency = meta.get('currency', 'SC')
    balance  = parse_balance(raw_text)
    with _connect() as conn:
        conn.execute(
            'INSERT INTO balances (recorded_at, casino, raw_text, balance, currency) VALUES (?, ?, ?, ?, ?)',
            (datetime.now().isoformat(), casino, raw_text, balance, currency)
        )


def weekly_summary(as_of: datetime | None = None) -> list[dict]:
    as_of = as_of or datetime.now()
    since = (as_of - timedelta(days=7)).isoformat()

    with _connect() as conn:
        rows = conn.execute(
            '''SELECT casino, balance, currency, raw_text, recorded_at
               FROM balances
               WHERE recorded_at >= ? AND balance IS NOT NULL
               ORDER BY casino, recorded_at DESC''',
            (since,)
        ).fetchall()

    seen    = set()
    entries = []
    for casino, balance, currency, raw_text, recorded_at in rows:
        if casino in seen:
            continue
        if casino not in CASINO_META:
            continue  # skip ghost keys like __main__
        if CASINO_META[casino].get('disabled'):
            continue
        seen.add(casino)
        meta = CASINO_META.get(casino, {})
        rtp  = meta.get('rtp', 0.96)
        entries.append({
            'casino':           casino,
            'display':          meta.get('display', casino),
            'logo':             meta.get('logo', ''),
            'color':            meta.get('color', '#333'),
            'balance':          balance or 0.0,
            'currency':         currency or meta.get('currency', 'SC'),
            'raw_text':         raw_text or '',
            'estimated_payout': round((balance or 0.0) * rtp, 2),
            'rtp_pct':          round(rtp * 100, 2),
            'recorded_at':      recorded_at,
        })

    # Include active casinos with no recent data so the report is always complete
    for key, meta in CASINO_META.items():
        if meta.get('disabled'):
            continue
        if key not in seen:
            entries.append({
                'casino':           key,
                'display':          meta['display'],
                'logo':             meta['logo'],
                'color':            meta['color'],
                'balance':          None,
                'currency':         meta['currency'],
                'raw_text':         '—',
                'estimated_payout': None,
                'rtp_pct':          round(meta['rtp'] * 100, 2),
                'recorded_at':      None,
            })

    return entries
