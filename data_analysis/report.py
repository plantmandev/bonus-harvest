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

TEMPLATE_PATH = Path(__file__).parent.parent / 'templates' / 'weekly_email.html'

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


def _format_date(iso: str | None) -> str:
    if not iso:
        return 'no data this week'
    try:
        return datetime.fromisoformat(iso).strftime('%b %d, %Y %H:%M')
    except ValueError:
        return iso


def _render_card(entry: dict) -> str:
    if entry['balance'] is None:
        balance_display  = 'No data'
        estimated_payout = '—'
    else:
        balance_display  = f"{entry['balance']:.2f} {entry['currency']}"
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

    week_start = (as_of - timedelta(days=7)).strftime('%b %d')
    week_end   = as_of.strftime('%b %d, %Y')
    week_range = f'{week_start} – {week_end}'

    cards = '\n'.join(_render_card(e) for e in entries)

    total = sum(
        e['estimated_payout'] for e in entries if e['estimated_payout'] is not None
    )

    raw = TEMPLATE_PATH.read_text()
    return Template(raw).safe_substitute(
        USER_NAME     = user_name,
        WEEK_RANGE    = week_range,
        CASINO_CARDS  = cards,
        TOTAL_PAYOUT  = f'{total:.2f}',
    )


def send_report(to: str | None = None, user_name: str = 'there'):
    sender       = os.getenv('GMAIL_ADDRESS', 'sirplantman@gmail.com')
    app_password = os.getenv('GMAIL_APP_PASSWORD')
    recipient    = to or os.getenv('REPORT_RECIPIENT', sender)

    if not app_password:
        raise ValueError('GMAIL_APP_PASSWORD not set in .env')

    html    = render_html(user_name)
    subject = f'🌾 Bonus Harvest — Weekly Report ({datetime.now().strftime("%b %d, %Y")})'

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = sender
    msg['To']      = recipient
    msg.attach(MIMEText(html, 'html'))

    with smtplib.SMTP('smtp.gmail.com', 587) as s:
        s.starttls()
        s.login(sender, app_password)
        s.send_message(msg)

    print(f'Weekly report sent to {recipient}')


if __name__ == '__main__':
    send_report()
