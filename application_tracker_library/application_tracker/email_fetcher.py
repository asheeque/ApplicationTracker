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
        logging.info("EmailFetcher initialized with given config.")

    def get_service(self,token=None):
        try:
            creds = None
            if token:
                creds = Credentials(token=token)
            else:
                token_path = os.path.expanduser(self.config.get("token_path", TOKEN_PATH))
                if os.path.exists(token_path):
                    creds = Credentials.from_authorized_user_file(token_path)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    logging.info("Credentials refreshed.")

                else:
                    credentials_path = os.path.expanduser(
                        self.config.get("credentials_path", CREDENTIALS_PATH))
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, self.SCOPES )
                    creds = flow.run_local_server(port=0)
                    logging.info("Credentials obtained from user.")
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                    logging.info(f"Credentials saved to {token_path}")

            service = build('gmail', 'v1', credentials=creds)
            logging.info("Gmail service built successfully.")

            return service
        except Exception as e:
            logging.error(f"An error occurred while getting service: {e}")
            # or log the error if you have a logging system in place
            return None

    def get_after_date_from_latest_timestamp(self,default_date):
        try:
            if os.path.exists(LATEST_TIMESTAMP_FILE):
                with open(LATEST_TIMESTAMP_FILE, "r") as f:
                    latest_timestamp = int(f.read().strip())
                    after_date = datetime.utcfromtimestamp(latest_timestamp / 1000)
                    return after_date
            return default_date
        except Exception as e:
            logging.error(f"Error fetching date from timestamp: {e}")
            return default_date

    def save_latest_timestamp(self,messages_data):
        try:
            if not messages_data:
                return
            latest_timestamp = max(int(msg['internalDate']) for msg in messages_data)
            with open(LATEST_TIMESTAMP_FILE, "w") as f:
                f.write(str(latest_timestamp))
                logging.info(f"Latest timestamp {latest_timestamp} saved to {LATEST_TIMESTAMP_FILE}.")
        except Exception as e:
            logging.error(f"Error saving the latest timestamp: {e}")

    def list_messages_with_labels(self,service, user_id='me', query=''):
    
        try:
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
        except Exception as e:
            logging.error(f"Error listing messages with labels: {e}")
            return []

    def fetch_email_data(self,gmail_service, message_id):
        try:
            return gmail_service.users().messages().get(userId='me', id=message_id).execute()
        except Exception as e:
            logging.error(f"Error fetching data for message ID {message_id}: {e}")
            return None
        
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
        print(len(headers))
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
        # print(headers.keys())
        from_address = next((item['value'] for item in headers if item['name'] == 'From'), None)
        to_address = next((item['value'] for item in headers if item['name'] == 'To'), None)

        return from_address, to_address,subject

    def get_full_message_text(self,msg_data):
        payload = msg_data['payload']
        parts = payload.get('parts', [])

        # Handle simple emails without multipart
        if not parts:
            body_data = payload['body'].get('data') 
            if not body_data:
                return ''
            decoded_bytes = base64.urlsafe_b64decode(body_data.encode('ASCII'))
            text = decoded_bytes.decode('utf-8')
            return text

        # Handle multipart emails
        email_content = []
        for part in parts:
            mime_type = part['mimeType']
            if mime_type == 'text/plain' or mime_type == 'text/html':
                body_data = payload['body'].get('data') 
                if not body_data:
                    return ''
                decoded_bytes = base64.urlsafe_b64decode(body_data.encode('ASCII'))
                text = decoded_bytes.decode('utf-8')
                email_content.append(text)

        return "\n".join(email_content)

    def fetch_emails_with_date_range(self, gmail_service, from_date=None, to_date=None):
        # Convert datetime objects to string
        if from_date:
            from_date_str = from_date.strftime('%Y/%m/%d')
        if to_date:
            to_date_str = to_date.strftime('%Y/%m/%d')

        # Construct queries based on provided dates
        queries = []
        if from_date and to_date:
            queries.append(f"label:inbox after:{from_date_str} before:{to_date_str}")
            queries.append(f"label:Applications after:{from_date_str} before:{to_date_str}")
        else:
            # Use the previous logic if dates are not provided
            default_after_date = datetime.strptime("2023-08-17 00:00:00", '%Y-%m-%d %H:%M:%S')
            after_date = self.get_after_date_from_latest_timestamp(default_after_date)
            after_date_str = after_date.strftime('%Y/%m/%d')
            queries.append(f"label:inbox after:{after_date_str}")
            queries.append(f"label:Applications after:{after_date_str}")
        all_messages = []
        for query in queries:
            all_messages.extend(fetcher.list_messages_with_labels(gmail_service, query=query))
        
        unique_messages_by_id = {message['id']: message for message in all_messages}
        return list(unique_messages_by_id.values())
    
    def fetch_and_process_emails(self, gmail_service,messages):
        all_messages_data = [self.fetch_email_data(gmail_service, msg['id']) for msg in messages]
        processed_emails = [self.one_message_data_processing(msg_data) for msg_data in all_messages_data]
        # self.save_latest_timestamp(all_messages_data)
        return processed_emails


def initialize_fetcher(token=None):
    fetcher = EmailFetcher()
    gmail_service = fetcher.get_service(token)
    if not gmail_service:
        logging.error("Failed to obtain Gmail service. Exiting program.")
        return
    return fetcher, gmail_service


    
def save_emails_to_csv(emails):
    with open('output_new.csv', 'w', newline='') as csvfile:
        fieldnames = emails[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for email in emails:
            writer.writerow(email)



# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     fetcher, gmail_service = initialize_fetcher()

#     if fetcher and gmail_service:
#         messages = fetcher.fetch_emails_with_date_range(gmail_service)
#         process_and_save_emails(fetcher, gmail_service, messages)
#         logging.info(f"Processed {len(messages)} emails.")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    fetcher, gmail_service = initialize_fetcher()

    if fetcher and gmail_service:
        messages = fetcher.fetch_emails_with_date_range(gmail_service)
        emails = fetcher.fetch_and_process_emails(gmail_service,messages)

        # If used as a standalone script, save to CSV
        save_emails_to_csv(emails)
        logging.info(f"Processed {len(messages)} emails.")
