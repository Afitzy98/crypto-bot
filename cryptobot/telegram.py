import json

import requests
from settings import TG_BOT_TOKEN, TG_USER_ID, WEBHOOK_URL

BASE_URL = "https://api.telegram.org/bot"


def set_webhook():
    reqUrl = BASE_URL + TG_BOT_TOKEN + "/setWebhook"
    setUrl = WEBHOOK_URL + f"/{TG_BOT_TOKEN}"

    try:
        requests.post(f"{reqUrl}?url={setUrl}")
    except:
        print("ERROR.FAILED_TO_SET_WEBHOOK")


def send_message(message: str):
    reqUrl = BASE_URL + TG_BOT_TOKEN + "/sendMessage"
    params = f"?chat_id={TG_USER_ID}&text={message}"
    try:
        requests.post(reqUrl + params)
    except Exception as e:
        print("ERROR.FAILED_TO_SEND_MESSAGE")
