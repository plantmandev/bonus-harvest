import base64
import os
import re
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv(Path(__file__).parent.parent / '.env')

SCOPES            = ['https://www.googleapis.com/auth/gmail.modify']
TOKEN_PATH        = Path(__file__).parent / 'token.json'
GMAIL_STATUS_PATH = Path(__file__).parent.parent / 'logs' / 'gmail_auth_status.txt'


from casinos.errors import GmailAuthExpiredError  # noqa: re-exported for callers


def _write_status(status: str):
    GMAIL_STATUS_PATH.parent.mkdir(exist_ok=True)
    GMAIL_STATUS_PATH.write_text(f'{status} {datetime.now().strftime("%Y-%m-%d %H:%M")}')


def _build_client_config():
    client_id     = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    if not client_id or not client_secret:
        raise ValueError('Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET in .env')
    return {
        'installed': {
            'client_id':     client_id,
            'client_secret': client_secret,
            'redirect_uris': ['http://localhost'],
            'auth_uri':      'https://accounts.google.com/o/oauth2/auth',
            'token_uri':     'https://oauth2.googleapis.com/token',
        }
    }


def _get_service():
    """Return an authorized Gmail service. Raises GmailAuthExpiredError if re-auth is needed."""
    from google.auth.exceptions import RefreshError
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                TOKEN_PATH.unlink(missing_ok=True)
                _write_status('EXPIRED')
                raise GmailAuthExpiredError(
                    'Gmail OAuth token expired or revoked — run: python3 -m auth.gmail'
                )
        else:
            _write_status('EXPIRED')
            raise GmailAuthExpiredError(
                'Gmail OAuth token missing — run: python3 -m auth.gmail'
            )
        TOKEN_PATH.write_text(creds.to_json())
    _write_status('OK')
    return build('gmail', 'v1', credentials=creds)


def reauthenticate():
    """Run the full interactive OAuth flow and save a fresh token."""
    flow  = InstalledAppFlow.from_client_config(_build_client_config(), SCOPES)
    creds = flow.run_local_server(port=8080, open_browser=False)
    TOKEN_PATH.write_text(creds.to_json())
    _write_status('OK')
    print('Gmail authentication successful — token saved.')
    return build('gmail', 'v1', credentials=creds)


def get_verification_code(sender_query, received_after=None, timeout=90, poll_interval=4, delete_after=True):
    service  = _get_service()
    deadline = time.time() + timeout
    after    = f' after:{int(received_after)}' if received_after else ' newer_than:2m'

    while time.time() < deadline:
        results = service.users().messages().list(
            userId='me', q=f'from:{sender_query}{after}', maxResults=5
        ).execute()
        for message in results.get('messages', []):
            msg      = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            msg_time = int(msg['internalDate']) / 1000
            if received_after and msg_time < received_after:
                continue
            match = re.search(r'\b(\d{6})\b', _decode_body(msg['payload']))
            if match:
                if delete_after:
                    service.users().messages().trash(userId='me', id=message['id']).execute()
                return match.group(1)
        time.sleep(poll_interval)

    raise TimeoutError(f'No verification code from "{sender_query}" within {timeout}s')


def delete_messages(sender_query: str, received_after: float | None = None):
    service = _get_service()
    after   = f' after:{int(received_after)}' if received_after else ' newer_than:1d'
    results = service.users().messages().list(
        userId='me', q=f'from:{sender_query}{after}', maxResults=20
    ).execute()
    for message in results.get('messages', []):
        service.users().messages().trash(userId='me', id=message['id']).execute()


def _decode_body(payload):
    for part in payload.get('parts', []):
        if part['mimeType'] == 'text/plain':
            data = part.get('body', {}).get('data', '')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    data = payload.get('body', {}).get('data', '')
    return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore') if data else ''


if __name__ == '__main__':
    try:
        _get_service()
        print('Gmail token is valid.')
    except GmailAuthExpiredError as e:
        print(f'{e}\nStarting re-authentication...')
        reauthenticate()
