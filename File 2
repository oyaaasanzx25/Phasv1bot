import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TOKEN:
    raise ValueError("ERROR: TELEGRAM_BOT_TOKEN belum diatur di file .env!")
if not GEMINI_API_KEY:
    raise ValueError("ERROR: GEMINI_API_KEY belum diatur di file .env!")
