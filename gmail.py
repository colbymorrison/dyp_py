from email.message import EmailMessage
from googleapiclient.errors import HttpError
from gauth import GAuth
import base64
import json


def create_draft(service, self, user_creds):
    with open('secrets/draft-data.json', 'r') as f:
        draft_data = json.load(f)

    msg = EmailMessage()
    msg['Subject'] = f"{user_creds['first']} {user_creds['last']}"
    msg['From'] = draft_data["address"]
    msg['To'] = user_creds['email']
    msg.set_content(draft_data["body"])

    with open(user_creds['file_name'], 'rb') as f:
        pdf_data = f.read()

    msg.add_attachment(pdf_data, filename=user_creds['file_name'], maintype="application", subtype="pdf")

    encoded = base64.urlsafe_b64encode(msg.as_string().encode())
    try:
        self.service.users().drafts().create(userId='me', body={"message":{"raw":encoded.decode()}}).execute()
    except HttpError as err:
        print(err)
        print("ERROR creating draft")


gauth = GAuth()
user_creds = {"first": "colby", "last": "morrison", "email": "colbyamorrison@gmail.com", "id": "abcdefg", "file_name": "test.pdf"}
create_draft(gauth.mail, user_creds)
