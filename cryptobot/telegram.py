import json
import requests
from settings import TG_BOT_TOKEN, WEBHOOK_URL, TG_USER_ID

BASE_URL = "https://api.telegram.org/bot"


def setWebhook():
    reqUrl = BASE_URL + TG_BOT_TOKEN + "/setWebhook"
    setUrl = WEBHOOK_URL + f"/{TG_BOT_TOKEN}"

    try:
        requests.post(f"{reqUrl}?url={setUrl}")
    except:
        print("ERROR.FAILED_TO_SET_WEBHOOK")


def sendMessage(message: str):
    reqUrl = BASE_URL + TG_BOT_TOKEN + "/sendMessage"
    params = f"?chat_id={TG_USER_ID}&text={message}"
    try:
        requests.post(reqUrl + params)
    except:
        print("ERROR.FAILED_TO_SEND_MESSAGE")
