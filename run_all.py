#!/usr/bin/env python3
"""Run every casino in casinos/ sequentially.

Discovery: any .py file in casinos/ (except base) that contains a BaseCasino
subclass is picked up automatically. Drop a new file there — no other changes needed.
"""
import importlib
import inspect
import sys
import traceback
from pathlib import Path

from casinos.base import BaseCasino, notify

SKIP = {'base', '__init__'}


def discover():
    casinos = []
    for path in sorted(Path('casinos').glob('*.py')):
        if path.stem in SKIP:
            continue
        mod = importlib.import_module(f'casinos.{path.stem}')
        for _, cls in inspect.getmembers(mod, inspect.isclass):
            if issubclass(cls, BaseCasino) and cls is not BaseCasino:
                if getattr(cls, 'DYNAMIC_SCHEDULE', False):
                    notify(f'Skipping {cls.__name__} — self-scheduling')
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
        notify(f'Running {cls.__name__}...')
        try:
            cls().run()
            results[name] = 'OK'
            notify(f'{cls.__name__} completed', 'SUCCESS')
        except Exception:
            results[name] = 'FAILED'
            notify(f'{cls.__name__} failed:\n{traceback.format_exc()}', 'ERROR')

    passed = [n for n, r in results.items() if r == 'OK']
    failed = [n for n, r in results.items() if r == 'FAILED']
    notify(f'Done — {len(passed)} passed, {len(failed)} failed')
    if failed:
        notify(f'Failed: {", ".join(failed)}', 'ERROR')
        sys.exit(1)


if __name__ == '__main__':
    main()
