from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_number = os.getenv('TWILIO_NUMBER')

client = Client(account_sid, auth_token)

def send_sms(to_number, message):
    client.messages.create(
        body=message,
        from_=twilio_number,
        to=to_number
    )
