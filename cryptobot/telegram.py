import requests
import json

class Telegram:
    def __init__(self, botToken: str):
        self.botToken = botToken
        self.reqUrl = "https://api.telegram.org/bot"

    def setWebhook(self, webhookUrl: str):
        reqUrl = self.reqUrl + self.botToken + "/setWebhook"
        setUrl = webhookUrl + "/webhook"
        try:
            requests.post(f"{reqUrl}?url={setUrl}")
        except:
            print("ERROR.FAILED_TO_SET_WEBHOOK")


