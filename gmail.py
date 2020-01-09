from email.message import EmailMessage
from googleapiclient.errors import HttpError
from gauth import GAuth
import base64
import json

class GMail:
    def __init__(self, service, logger):
        self.service=service
        self.logger=logger

    def create_draft(self, user_creds):
        self.logger.debug(f"Creating draft for user {user_creds['email']} with files {user_creds['files']}")
        with open('secrets/draft-data.json', 'r') as f:
            draft_data = json.load(f)

        msg = EmailMessage()
        msg['Subject'] = f"{user_creds['first']} {user_creds['last']}"
        msg['From'] = draft_data["address"]
        msg['To'] = user_creds['email']
        msg.set_content(draft_data["body"])

        for file_name in user_creds['files']:
            with open(file_name, 'rb') as f:
                pdf_data = f.read()

            msg.add_attachment(pdf_data, filename=file_name.replace('pdfs/',''), maintype="application", subtype="pdf")

        encoded = base64.urlsafe_b64encode(msg.as_string().encode())
        try:
            self.service.users().drafts().create(userId='me', body={"message":{"raw":encoded.decode()}}).execute()
        except HttpError as err:
            self.logger.error(f"Draft creation error to {user_creds['email']}:\n{err}")

        self.logger.info(f"Draft created to {user_creds['email']}")
