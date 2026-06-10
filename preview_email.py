#!/usr/bin/env python3
"""Render the daily report HTML and open it in the browser — no email sent.

Usage:
    python3 preview_email.py
"""

import sys
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')

from data_analysis.report import render_html

html = render_html(user_name='there')
out  = Path(__file__).parent / 'logs' / 'preview_email.html'
out.parent.mkdir(exist_ok=True)
out.write_text(html)

print(f'Preview written to: {out}')
webbrowser.open(out.as_uri())
