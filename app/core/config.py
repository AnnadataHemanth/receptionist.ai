from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# -------------------------
# App Settings
# -------------------------
APP_NAME = os.getenv("APP_NAME", "Jarvis")
ENV = os.getenv("ENV", "development")

# -------------------------
# Twilio Configuration
# -------------------------
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# -------------------------
# AI Configuration
# -------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# -------------------------
# Security
# -------------------------
SECRET_KEY = os.getenv("SECRET_KEY")

# -------------------------
# Optional Safety Checks
# -------------------------
if not TWILIO_ACCOUNT_SID:
    print("⚠️ Warning: TWILIO_ACCOUNT_SID not set")

if not GROQ_API_KEY:
    print("⚠️ Warning: GROQ_API_KEY not set")

if not SECRET_KEY:
    raise ValueError("❌ SECRET_KEY is not set in .env")