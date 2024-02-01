# import base64
# import os.path
# import json
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError

# def search_and_extract(service, user_id, search_query):
#     try:
        
#         # Call the Gmail API
#         service = build("gmail", "v1", credentials=creds)

#         # Specify the email subject to search for
#         search_subject = "x"

#         # Search for emails with the specified subject
#         response = service.users().messages().list(userId=user_id, q=search_query).execute()
#         messages = response.get('messages', [])

#         if not messages:
#             print("No emails found with the specified subject.")
#             return None

#         # Retrieve the content of the first matching email
#         message_id = messages[0]['id']
#         message = service.users().messages().get(userId=user_id, id=message_id).execute()

#         # Extract email content
#         email_data = {
#             'subject': message['subject'],
#             'from': message['payload']['headers'][1]['value'],  # Assuming 'From' header is at index 1
#             'body': base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
#         }

#         return email_data