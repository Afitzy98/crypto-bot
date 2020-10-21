class Telegram:
    def __init__(self, botToken: str):
        self.botToken = botToken
        self.reqUrl = "https://api.telegram.org/bot"

    def setWebhook()