import json
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from string import Template

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

from .tracker import weekly_summary

TEMPLATE_PATH  = Path(__file__).parent.parent / 'templates' / 'daily_email.html'
FAILURES_FILE      = Path(__file__).parent.parent / 'logs' / 'last_failures.json'
GMAIL_STATUS_FILE  = Path(__file__).parent.parent / 'logs' / 'gmail_auth_status.txt'

CARD_TEMPLATE = Template('''
          <tr>
            <td style="padding:10px 24px 0;">
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="border:1px solid #e8e8e8;border-radius:6px;overflow:hidden;">
                <tr>
                  <td style="background:$color;width:4px;"></td>
                  <td style="padding:12px 14px;">
                    <table width="100%" cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="font-size:14px;font-weight:bold;color:#1a1a2e;">$display</td>
                        <td align="right" style="font-size:16px;font-weight:bold;color:#333;">$balance_display</td>
                      </tr>
                      <tr>
                        <td style="font-size:11px;color:#aaa;padding-top:2px;">$recorded_at</td>
                        <td align="right" style="font-size:11px;color:#1a9e5c;padding-top:2px;">≈ $$$estimated_payout</td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
''')

FAILURE_BANNER = Template('''
          <tr>
            <td style="padding:16px 32px 8px;">
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="border:1px solid #e74c3c;border-radius:6px;background:#fff5f5;overflow:hidden;">
                <tr>
                  <td style="background:#e74c3c;width:6px;"></td>
                  <td style="padding:14px 16px;">
                    <p style="margin:0;font-size:14px;font-weight:bold;color:#c0392b;">
                      ⚠️ Manual Fix Required
                    </p>
                    <p style="margin:6px 0 0;font-size:13px;color:#555;">
                      The following casinos failed after $max_retries attempts and need attention:
                    </p>
                    <p style="margin:6px 0 0;font-size:13px;font-weight:bold;color:#c0392b;">
                      $failed_list
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
''')


_ERROR_REMEDIES = {
    'GmailAuthExpired':    'Run <code>python3 -m auth.gmail</code> to re-authenticate Gmail.',
    'AccountVerification': 'Log into the casino and complete identity/selfie verification.',
    'Unknown':             'Check the harvest logs for details.',
}

LOG_DIR = Path(__file__).parent.parent / 'logs'


def _read_casino_failures() -> list[dict]:
    """Return list of {casino, display, error_code, remedy} for any failed casino."""
    from .tracker import CASINO_META
    failures = []
    for key, meta in CASINO_META.items():
        if meta.get('disabled'):
            continue
        path = LOG_DIR / f'{key}_status.txt'
        if not path.exists():
            continue
        try:
            parts = path.read_text().strip().split(' ', 1)
            code  = parts[0]
            if not code.startswith('FAILED'):
                continue
            error_type = code.split(':', 1)[1] if ':' in code else 'Unknown'
            failures.append({
                'casino':  key,
                'display': meta.get('display', key),
                'code':    error_type,
                'remedy':  _ERROR_REMEDIES.get(error_type, _ERROR_REMEDIES['Unknown']),
            })
        except Exception:
            pass
    return failures


def _read_failures() -> list[str]:
    try:
        data = json.loads(FAILURES_FILE.read_text())
        return data.get('failed', [])
    except Exception:
        return []


def _gmail_expired() -> bool:
    try:
        return GMAIL_STATUS_FILE.read_text().strip().startswith('EXPIRED')
    except Exception:
        return False


def _format_date(iso: str | None) -> str:
    if not iso:
        return 'no recent data'
    try:
        return datetime.fromisoformat(iso).strftime('%b %d, %Y %H:%M')
    except ValueError:
        return iso


def _render_card(entry: dict) -> str:
    if entry['balance'] is None:
        balance_display  = 'No data'
        estimated_payout = '—'
    else:
        balance_display  = f"{entry['balance']:,.2f} {entry['currency']}"
        estimated_payout = f"{entry['estimated_payout']:.2f}"

    return CARD_TEMPLATE.substitute(
        color            = entry['color'],
        logo             = entry['logo'],
        display          = entry['display'],
        rtp_pct          = entry['rtp_pct'],
        balance_display  = balance_display,
        recorded_at      = _format_date(entry['recorded_at']),
        estimated_payout = estimated_payout,
    )


def render_html(user_name: str = 'there', as_of: datetime | None = None) -> str:
    as_of   = as_of or datetime.now()
    entries = weekly_summary(as_of)

    casino_failures = _read_casino_failures()
    gmail_expired   = _gmail_expired()

    failures_section = ''
    for f in casino_failures:
        failures_section += f'''
          <tr>
            <td style="padding:10px 24px 0;">
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="border:1px solid #e74c3c;border-radius:6px;background:#fff5f5;overflow:hidden;">
                <tr>
                  <td style="background:#e74c3c;width:4px;"></td>
                  <td style="padding:10px 14px;">
                    <span style="font-size:13px;font-weight:bold;color:#c0392b;">
                      ⚠️ {f["display"]} — {f["code"]}
                    </span><br>
                    <span style="font-size:12px;color:#555;">{f["remedy"]}</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
'''
    if gmail_expired:
        failures_section += '''
          <tr>
            <td style="padding:10px 24px 0;">
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="border:1px solid #e74c3c;border-radius:6px;background:#fff5f5;overflow:hidden;">
                <tr>
                  <td style="background:#e74c3c;width:4px;"></td>
                  <td style="padding:10px 14px;">
                    <span style="font-size:13px;font-weight:bold;color:#c0392b;">
                      🔑 Gmail OAuth — GmailAuthExpired
                    </span><br>
                    <span style="font-size:12px;color:#555;">Run: python3 -m auth.gmail</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
'''

    cards = '\n'.join(_render_card(e) for e in entries)

    total = sum(
        e['estimated_payout'] for e in entries if e['estimated_payout'] is not None
    )

    try:
        from .plot import generate_email_chart_b64
        b64 = generate_email_chart_b64()
        if b64:
            chart_section = (
                '<tr><td style="padding:16px 24px 0;">'
                f'<img src="data:image/png;base64,{b64}" '
                'width="100%" style="display:block;border-radius:4px;" alt="Balance chart">'
                '</td></tr>'
            )
        else:
            chart_section = ''
    except Exception:
        chart_section = ''

    raw = TEMPLATE_PATH.read_text()
    return Template(raw).safe_substitute(
        DATE             = as_of.strftime('%b %d, %Y'),
        CASINO_CARDS     = cards,
        TOTAL_PAYOUT     = f'{total:.2f}',
        FAILURES_SECTION = failures_section,
        CHART_SECTION    = chart_section,
    )


def send_report(to: str | None = None, user_name: str = 'there',
                failed_casinos: list[str] | None = None):
    sender       = os.getenv('GMAIL_ADDRESS', 'sirplantman@gmail.com')
    app_password = os.getenv('GMAIL_APP_PASSWORD')
    recipient    = to or os.getenv('REPORT_RECIPIENT', sender)

    if not app_password:
        raise ValueError('GMAIL_APP_PASSWORD not set in .env')

    html    = render_html(user_name)
    subject = f'🌾 Bonus Harvest — Daily Report ({datetime.now().strftime("%b %d, %Y")})'
    if _read_casino_failures() or _gmail_expired():
        subject = f'⚠️ {subject} — Action Required'

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = sender
    msg['To']      = recipient
    msg.attach(MIMEText(html, 'html'))

    with smtplib.SMTP('smtp.gmail.com', 587) as s:
        s.starttls()
        s.login(sender, app_password)
        s.send_message(msg)

    print(f'Daily report sent to {recipient}')


if __name__ == '__main__':
    send_report()
