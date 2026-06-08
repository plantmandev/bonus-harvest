#!/usr/bin/env python3
"""Run every casino in casinos/ sequentially.

Discovery: any .py file in casinos/ (except base) that contains a BaseCasino
subclass is picked up automatically. Drop a new file there — no other changes needed.
"""
import importlib
import inspect
import json
import sys
import time
import traceback
from pathlib import Path

from casinos.base import BaseCasino, notify

SKIP        = {'base', '__init__'}
MAX_RETRIES = 3
RETRY_DELAY = 30  # seconds between retry attempts
FAILURES_FILE = Path('logs/last_failures.json')


def discover():
    casinos = []
    for path in sorted(Path('casinos').glob('*.py')):
        if path.stem in SKIP:
            continue
        mod = importlib.import_module(f'casinos.{path.stem}')
        for _, cls in inspect.getmembers(mod, inspect.isclass):
            if issubclass(cls, BaseCasino) and cls is not BaseCasino:
                if getattr(cls, 'DISABLED', False):
                    notify(f'Skipping {cls.__name__} — disabled')
                else:
                    casinos.append((path.stem, cls))
                break
    return casinos


def main():
    casinos = discover()
    if not casinos:
        notify('No casino modules found — nothing to run.', 'WARNING')
        return

    notify(f'Starting harvest for {len(casinos)} site(s): {", ".join(n for n, _ in casinos)}')

    results = {}
    for name, cls in casinos:
        for attempt in range(1, MAX_RETRIES + 1):
            notify(f'Running {cls.__name__}{"" if attempt == 1 else f" (retry {attempt - 1}/{MAX_RETRIES - 1})"}...')
            try:
                cls().run()
                results[name] = 'OK'
                notify(f'{cls.__name__} completed', 'SUCCESS')
                break
            except Exception:
                notify(f'{cls.__name__} attempt {attempt} failed:\n{traceback.format_exc()}', 'ERROR')
                if attempt < MAX_RETRIES:
                    notify(f'Retrying in {RETRY_DELAY}s...')
                    time.sleep(RETRY_DELAY)
                else:
                    results[name] = 'FAILED'
                    notify(f'{cls.__name__} failed after {MAX_RETRIES} attempts — needs manual fix', 'ERROR')

    passed = [n for n, r in results.items() if r == 'OK']
    failed = [n for n, r in results.items() if r == 'FAILED']

    FAILURES_FILE.parent.mkdir(exist_ok=True)
    FAILURES_FILE.write_text(json.dumps({'failed': failed, 'timestamp': __import__('datetime').datetime.now().isoformat()}))

    notify(f'Done — {len(passed)} passed, {len(failed)} failed')
    if failed:
        notify(f'Failed: {", ".join(failed)}', 'ERROR')
        sys.exit(1)


if __name__ == '__main__':
    main()
