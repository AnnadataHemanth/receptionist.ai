from twilio.rest import Client
import os

# Put these in your .env later for security
ACCOUNT_SID = "ACf0e8b895c2de20a3eeeaa9e363ae5364"
AUTH_TOKEN = "1466388c926869a3df312ed01eb49983"
TWILIO_NUMBER = "+16672958709"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_sms(to_number, message):
    client.messages.create(
        body=message,
        from_=TWILIO_NUMBER,
        to=to_number
    )
