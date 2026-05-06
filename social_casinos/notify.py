import sys
from datetime import datetime


def notify(message: str, level: str = 'INFO'):
    tag = f'[{level}]'
    ts  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'{ts} {tag:<9} {message}'
    print(line, flush=True)
    if level == 'ERROR':
        print(line, file=sys.stderr, flush=True)
