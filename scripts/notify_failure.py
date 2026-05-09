#!/usr/bin/env python3
"""Desktop notification when a harvest script fails."""
import argparse
import os
import subprocess
from pathlib import Path

TAIL_LINES = 20


def tail(path: str, n: int) -> str:
    try:
        lines = Path(path).read_text().splitlines()
        return '\n'.join(lines[-n:])
    except Exception as e:
        return f'(could not read log: {e})'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--casino', required=True)
    p.add_argument('--log',    required=True)
    p.add_argument('--exit-code', type=int, default=1)
    args = p.parse_args()

    summary = f'{args.casino} harvest failed (exit {args.exit_code})'
    log_tail = tail(args.log, TAIL_LINES)

    print(f'\n[ALERT] {summary}')
    print(f'Last {TAIL_LINES} log lines:\n{log_tail}\n')

    env = {**os.environ, 'DISPLAY': ':0'}
    try:
        subprocess.run(
            ['notify-send', '--urgency=critical', '--icon=error',
             'Bonus Harvest Failed', summary],
            env=env, check=False
        )
    except FileNotFoundError:
        print('[notify-send not installed — skipping desktop notification]')


if __name__ == '__main__':
    main()
