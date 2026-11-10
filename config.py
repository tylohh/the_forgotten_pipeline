import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
CREDENTIALS_DIR = BASE_DIR / "credentials"
HISTORY_FILE = BASE_DIR / "history.json"
OUTPUT_DIR.mkdir(exist_ok=True)
CREDENTIALS_DIR.mkdir(exist_ok=True)

PIPELINE_MODE = os.getenv("PIPELINE_MODE", "TEST").upper()
# Automatically clean any accidental quotes or spaces from keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip('"\' ')
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "").strip('"\' ')
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "").strip('"\' ')
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM").strip('"\' ')

ENABLE_YOUTUBE = os.getenv("ENABLE_YOUTUBE", "false").lower() == "true"
ENABLE_WEBHOOK = os.getenv("ENABLE_WEBHOOK", "false").lower() == "true"
PUBLISHING_WEBHOOK_URL = os.getenv("PUBLISHING_WEBHOOK_URL", "")
CLIENT_SECRET_FILE = CREDENTIALS_DIR / "client_secret.json"
TOKEN_FILE = CREDENTIALS_DIR / "token.json"
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
