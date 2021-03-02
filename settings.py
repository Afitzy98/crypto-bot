# settings.py
from dotenv import load_dotenv

load_dotenv()

import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ".\DevCryptoBot-811d9b05d5d8.json"

APP_SETTINGS = os.getenv("APP_SETTINGS")
APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
DB_URI = os.getenv("DB_URI")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_USER_ID = int(os.getenv("TG_USER_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
