#!/usr/bin/env python3
"""Generate the balance-over-time chart and open it in a browser.

Usage:
    python3 view_chart.py
"""

import sys
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')

from data_analysis.plot import generate_chart

path = generate_chart()
print(f'Chart written to: {path}')
webbrowser.open(path.as_uri())
