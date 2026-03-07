# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))

# OPENAI_API_KEY removed — we now run Whisper locally for free