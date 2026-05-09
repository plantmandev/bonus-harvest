#!/usr/bin/env python3
"""Run every casino in social_casinos/ sequentially.

Discovery: any .py file in this directory (except casino_base and notify)
that contains a BaseCasino subclass is treated as a casino and run.
To add a new site, drop a file here — no other changes needed.
"""
import importlib
import inspect
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from casino_base import BaseCasino
from notify import notify

SKIP = {'casino_base', 'notify', 'run_all'}


def discover():
    casinos = []
    for path in sorted(Path(__file__).parent.glob('*.py')):
        if path.stem in SKIP:
            continue
        mod = importlib.import_module(path.stem)
        for _, cls in inspect.getmembers(mod, inspect.isclass):
            if issubclass(cls, BaseCasino) and cls is not BaseCasino:
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
            notify(f'{cls.__name__} completed successfully')
        except Exception:
            results[name] = 'FAILED'
            notify(f'{cls.__name__} failed:\n{traceback.format_exc()}', 'ERROR')

    passed = [n for n, r in results.items() if r == 'OK']
    failed = [n for n, r in results.items() if r == 'FAILED']

    notify(f'Harvest complete — {len(passed)} passed, {len(failed)} failed')
    if failed:
        notify(f'Failed sites: {", ".join(failed)}', 'ERROR')
        sys.exit(1)


if __name__ == '__main__':
    main()
