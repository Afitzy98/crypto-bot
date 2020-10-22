# settings.py
from dotenv import load_dotenv
load_dotenv()

import os

APP_SETTINGS = os.getenv("APP_SETTINGS")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")