import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    from dotenv import load_dotenv
    load_dotenv(env_path)

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
TOKEN_PATH = 'token.json'
CREDENTIALS_PATH = 'credentials.json'

class GmailEmailSender:
    """Class to send HTML emails with attachments via Gmail API"""

    def __init__(self):
        self.sender = os.getenv('SENDER_EMAIL')
        if not self.sender:
            raise ValueError('SENDER_EMAIL must be set in environment variables')
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, 'w') as token_file:
                token_file.write(creds.to_json())
        return build('gmail', 'v1', credentials=creds)

    def send_email(self,
                   to_emails: List[str],
                   subject: str,
                   html_content: str,
                   attachment_path: Optional[str] = None) -> None:
        """
        Send an email with optional attachment.

        :param to_emails: List of recipient email addresses
        :param subject: Email subject line
        :param html_content: HTML content of the email body
        :param attachment_path: Path to a file to attach (e.g., audio file)
        """
        message = MIMEMultipart()
        message['From'] = self.sender
        message['To'] = ', '.join(to_emails)
        message['Subject'] = subject

        # Attach HTML body
        body = MIMEText(html_content, 'html')
        message.attach(body)

        # Attach file if provided
        if attachment_path and os.path.exists(attachment_path):
            filename = os.path.basename(attachment_path)
            with open(attachment_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            message.attach(part)

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        self.service.users().messages().send(userId='me', body={'raw': raw}).execute()
        print(f"Email sent to: {message['To']}")


if __name__ == '__main__':
    # Get the text content from the file
    summary_file_path = "/Users/ebaad69/Desktop/Exa-projects/Exa + Composio + Elevelnlabs/series_a_companies_summary.txt"
    with open(summary_file_path, 'r') as f:
        summary_content = f.read()
    
    # Convert plain text to HTML - first transform the text
    formatted_content = summary_content.replace('\n\n', '<br><br>')
    formatted_content = formatted_content.replace('\n', '<br>')
    
    # Then create the HTML
    html_content = '<html><body><h1>Series A Funding Newsletter</h1>'
    html_content += '<div style="font-family: Arial, sans-serif; line-height: 1.6;">'
    html_content += formatted_content
    html_content += '</div>'
    html_content += '<p>Listen to the audio summary attached to this email.</p>'
    html_content += '<p>Best regards,<br/>AI Newsletter Bot</p></body></html>'
    
    # Test the GmailEmailSender
    sender = GmailEmailSender()
    
    # Prepare email components
    test_recipients = ["ebaadforrandomstuff@gmail.com"]
    test_subject = '🎵 Series A Companies Funding Update'
    test_audio_path = '/Users/ebaad69/Desktop/Exa-projects/exa+elevenlabs/output/series_a_audio_20250704_002338.mp3'
    
    sender.send_email(
        to_emails=test_recipients,
        subject=test_subject,
        html_content=html_content,
        attachment_path=test_audio_path
    )
