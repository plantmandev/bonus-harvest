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
FAILURES_FILE  = Path(__file__).parent.parent / 'logs' / 'last_failures.json'

CARD_TEMPLATE = Template('''
          <tr>
            <td style="padding:16px 32px 8px;">
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="border:1px solid #eeeeee;border-radius:6px;overflow:hidden;">
                <tr>
                  <td style="background:$color;width:6px;"></td>
                  <td style="padding:14px 16px;">
                    <table width="100%" cellpadding="0" cellspacing="0">
                      <tr>
                        <td>
                          <img src="$logo" width="24" height="24"
                               style="vertical-align:middle;border-radius:4px;margin-right:8px;"
                               alt="$display logo">
                          <span style="font-size:15px;font-weight:bold;color:#1a1a2e;vertical-align:middle;">
                            $display
                          </span>
                          <span style="font-size:11px;color:#999;margin-left:8px;">
                            RTP $rtp_pct%
                          </span>
                        </td>
                        <td align="right">
                          <span style="font-size:18px;font-weight:bold;color:#333;">
                            $balance_display
                          </span>
                        </td>
                      </tr>
                      <tr>
                        <td style="font-size:12px;color:#888;padding-top:4px;">
                          Balance as of $recorded_at
                        </td>
                        <td align="right" style="font-size:12px;color:#1a9e5c;padding-top:4px;">
                          ≈ $$$estimated_payout est. payout
                        </td>
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


def _read_failures() -> list[str]:
    try:
        data = json.loads(FAILURES_FILE.read_text())
        return data.get('failed', [])
    except Exception:
        return []


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


def render_html(user_name: str = 'there', as_of: datetime | None = None,
                failed_casinos: list[str] | None = None) -> str:
    as_of   = as_of or datetime.now()
    entries = weekly_summary(as_of)

    if failed_casinos is None:
        failed_casinos = _read_failures()

    failures_section = ''
    if failed_casinos:
        from .tracker import CASINO_META
        display_names = [CASINO_META.get(k, {}).get('display', k) for k in failed_casinos]
        failures_section = FAILURE_BANNER.substitute(
            max_retries = 3,
            failed_list = ', '.join(display_names),
        )

    cards = '\n'.join(_render_card(e) for e in entries)

    total = sum(
        e['estimated_payout'] for e in entries if e['estimated_payout'] is not None
    )

    raw = TEMPLATE_PATH.read_text()
    return Template(raw).safe_substitute(
        USER_NAME        = user_name,
        DATE             = as_of.strftime('%b %d, %Y'),
        CASINO_CARDS     = cards,
        TOTAL_PAYOUT     = f'{total:.2f}',
        FAILURES_SECTION = failures_section,
    )


def send_report(to: str | None = None, user_name: str = 'there',
                failed_casinos: list[str] | None = None):
    sender       = os.getenv('GMAIL_ADDRESS', 'sirplantman@gmail.com')
    app_password = os.getenv('GMAIL_APP_PASSWORD')
    recipient    = to or os.getenv('REPORT_RECIPIENT', sender)

    if not app_password:
        raise ValueError('GMAIL_APP_PASSWORD not set in .env')

    failed_casinos = failed_casinos if failed_casinos is not None else _read_failures()
    html    = render_html(user_name, failed_casinos=failed_casinos)
    subject = f'🌾 Bonus Harvest — Daily Report ({datetime.now().strftime("%b %d, %Y")})'
    if failed_casinos:
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
