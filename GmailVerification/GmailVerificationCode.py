import re
import time
import base64
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from GmailAPI import get_gmail_service


def get_verification_code(sender_query, received_after=None, timeout=90, poll_interval=4):
    """Poll Gmail for a verification email and extract the first 6-digit code found.

    received_after: Unix timestamp — only emails received at or after this time are considered.
    """
    service = get_gmail_service()
    deadline = time.time() + timeout
    after_clause = f' after:{int(received_after)}' if received_after else ' newer_than:2m'

    while time.time() < deadline:
        results = service.users().messages().list(
            userId='me',
            q=f'from:{sender_query}{after_clause}',
            maxResults=5
        ).execute()

        messages = results.get('messages', [])
        for message in messages:
            msg = service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()

            # Skip emails received before login was submitted
            msg_time = int(msg['internalDate']) / 1000
            if received_after and msg_time < received_after:
                continue

            body = _decode_body(msg['payload'])
            match = re.search(r'\b(\d{6})\b', body)
            if match:
                return match.group(1)

        time.sleep(poll_interval)

    raise TimeoutError(f'No verification code from "{sender_query}" received within {timeout}s')


def _decode_body(payload):
    parts = payload.get('parts', [])
    if parts:
        for part in parts:
            if part['mimeType'] == 'text/plain':
                data = part.get('body', {}).get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    data = payload.get('body', {}).get('data', '')
    if data:
        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    return ''
