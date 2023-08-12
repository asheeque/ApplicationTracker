import base64
from datetime import datetime
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json
from bs4 import BeautifulSoup
import csv
from application_tracker.config import config
import logging
import sys

TOKEN_PATH = "token.json"
CREDENTIALS_PATH = "credentials.json"
LATEST_TIMESTAMP_FILE = "latest_timestamp.txt"

class EmailFetcher:
    def __init__(self, config=config):
        """
        Initialize the EmailFetcher with optional configuration.
        """
        self.config = config or {}
        self.SCOPES = self.config.get("SCOPES", ['https://www.googleapis.com/auth/gmail.readonly'])

    def get_service(self):
        try:
            creds = None
            token_path = os.path.expanduser(
                self.config.get("token_path", TOKEN_PATH))
            # print(token_path)
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    credentials_path = os.path.expanduser(
                        self.config.get("credentials_path", CREDENTIALS_PATH))
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, self.SCOPES )
                    creds = flow.run_local_server(port=0)
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())

            service = build('gmail', 'v1', credentials=creds)
            return service
        except Exception as e:
            logging.error(f"An error occurred while getting service: {e}")
            # or log the error if you have a logging system in place
            return None

    def get_after_date_from_latest_timestamp(self,default_date):
        if os.path.exists(LATEST_TIMESTAMP_FILE):
            with open(LATEST_TIMESTAMP_FILE, "r") as f:
                latest_timestamp = int(f.read().strip())
                
                # Convert the timestamp from milliseconds to seconds and create a datetime object
                after_date = datetime.utcfromtimestamp(latest_timestamp / 1000)
                return after_date
        return default_date

    def save_latest_timestamp(self,messages_data):
        if not messages_data:
            return
        # Find the latest timestamp from the messages
        latest_timestamp = max(int(msg['internalDate']) for msg in messages_data)

        # Save to a file
        with open(LATEST_TIMESTAMP_FILE, "w") as f:
            f.write(str(latest_timestamp))

    def list_messages_with_labels(self,service, user_id='me', query=''):
    

        response = service.users().messages().list(userId=user_id, q=query).execute()
        # print(response)
        messages = []
        if 'messages' in response:
            
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages
    
    def datetime_handler(self,x):
        if isinstance(x, datetime):
            return x.strftime('%Y-%m-%d %H:%M:%S')
        raise TypeError("Unknown type")
    
    def one_message_data_processing(self,data):

        timestamp = int(data['internalDate']) / 1000
        received_date = datetime.utcfromtimestamp(timestamp)
        from_address, to_address,subject = self.extract_from_and_to_addresses(data)

        full_message = self.get_full_message_text(data)
        body = self.extract_body_content(full_message)
        
        email_dict = {
            "from":from_address,
            "to":to_address,
            "received_date":self.datetime_handler(received_date),
            "subject":subject,
            "snippet":data["snippet"],
            "body":body
        }

        return email_dict

    def extract_body_content(self,html_string):
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_string, 'html.parser')
        
        # Find all div tags
        divs = soup.find_all('div')
        
        if not divs:
            return soup.get_text()
        
        # Find the div with the most text content
        largest_div = max(divs, key=lambda div: len(div.get_text()))
        body = largest_div.get_text()
        sanitized_body = body.replace("\u00a0", " ").replace("\u200c", "")

        # Strip to remove any extra spaces at the beginning or end
        sanitized_body = sanitized_body.strip()
        return sanitized_body


    def extract_from_and_to_addresses(self,msg_data):
        headers = msg_data['payload']['headers']
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
        from_address = next((item['value'] for item in headers if item['name'] == 'From'), None)
        to_address = next((item['value'] for item in headers if item['name'] == 'To'), None)

        return from_address, to_address,subject

    def get_full_message_text(self,msg_data):
        payload = msg_data['payload']
        parts = payload.get('parts', [])

        # Handle simple emails without multipart
        if not parts:
            body_data = payload['body']['data']
            decoded_bytes = base64.urlsafe_b64decode(body_data.encode('ASCII'))
            text = decoded_bytes.decode('utf-8')
            return text

        # Handle multipart emails
        email_content = []
        for part in parts:
            mime_type = part['mimeType']
            if mime_type == 'text/plain' or mime_type == 'text/html':
                body_data = part['body']['data']
                decoded_bytes = base64.urlsafe_b64decode(body_data.encode('ASCII'))
                text = decoded_bytes.decode('utf-8')
                email_content.append(text)

        return "\n".join(email_content)


if __name__ == "__main__":
    fetcher = EmailFetcher()
    gmail_service = fetcher.get_service()
    if gmail_service is None:
        print("Failed to obtain Gmail service. Exiting program.")
        sys.exit(1)
    default_after_date = datetime.strptime("2023-08-09 15:48:03", '%Y-%m-%d %H:%M:%S')
    after_date = fetcher.get_after_date_from_latest_timestamp(default_after_date)
    after_date_str = after_date.strftime('%Y/%m/%d')
    
    query_inbox = f"label:inbox after:{after_date_str}"
    messages_inbox = fetcher.list_messages_with_labels(gmail_service, query=query_inbox)

    query_applications = f"label:Applications after:{after_date_str}"
    messages_applications = fetcher.list_messages_with_labels(gmail_service, query=query_applications)
    
    all_messages = messages_inbox + messages_applications
    unique_messages_by_id = {message['id']: message for message in all_messages}
    messages = list(unique_messages_by_id.values())
    # print(messages_inbox[0])

    all_messages_data = []
    for idx,msg in enumerate(messages):
        if(idx % 50 == 0):
            print(idx," API CALL")
        msg_data = gmail_service.users().messages().get(userId='me', id=msg['id']).execute()
        all_messages_data.append(msg_data)
    
    all_messages = []
    for idx,msg in enumerate(all_messages_data):
        # if(idx % 50 == 0):
        processed_data = fetcher.one_message_data_processing(msg)
        all_messages.append(processed_data)

    fetcher.save_latest_timestamp(all_messages_data)


    with open('output_test.csv', 'w', newline='') as csvfile:
        fieldnames = all_messages[0].keys() # Assuming all dictionaries have the same keys
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for data in all_messages:
            writer.writerow(data)
    print(len(messages),messages[0])