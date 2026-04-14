import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# WhatsApp
WHATSAPP_TOKEN    = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")
VERIFY_TOKEN      = os.getenv("VERIFY_TOKEN", "shetkari_vaani_secret")

# AI
GROQ_API_KEY      = os.getenv("GROQ_API_KEY", "")

# App
DEBUG             = os.getenv("DEBUG", "false").lower() == "true"
PORT              = int(os.getenv("PORT", "8000"))

# Validate on startup — fail loud, not silent
REQUIRED = {
    "WHATSAPP_TOKEN":    WHATSAPP_TOKEN,
    "WHATSAPP_PHONE_ID": WHATSAPP_PHONE_ID,
    "GROQ_API_KEY":      GROQ_API_KEY,
}

for key, val in REQUIRED.items():
    if not val:
        raise EnvironmentError(f"❌ Missing required env variable: {key}")