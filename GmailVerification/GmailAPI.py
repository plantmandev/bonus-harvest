#              # 
# VERIFICATION # 
#              # 

import base64
import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Defines script privileges to 'READ-ONLY' and 'WRITE'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

def GmailAPI():
    # Creates 'creds' variable
    creds = None
    
    # If token.json already exists, credentials are pulled from token.json
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If token.json does not exist OR token.json is invalid, credentials are refreshed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Else, open Gmail authorization page using credentials.json to authorize token.json generation
        else:
            # Use os.path.join to construct the correct path
            credentials_path = os.path.join(os.path.dirname(__file__), "credentials.json")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

if __name__ == "__main__":
    GmailAPI()
