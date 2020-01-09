import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/gmail.compose']

class GAuth:
    def __init__(self, logger):
        creds = self.__get_creds()
        self.calendar = build('calendar', 'v3', credentials=creds, cache_discovery=False)
        self.mail = build('gmail', 'v1', credentials=creds, cache_discovery=False)
        self.logger = logger

    def __get_creds(self):
        creds = None
        token_path = "secrets/token.pickle"
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                          'secrets/client_secret.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        return creds 

# gauth = GAuth()
