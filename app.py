from flask import Flask, request
from settings import APP_SETTINGS, TG_BOT_TOKEN, WEBHOOK_URL
from cryptobot.telegram import Telegram

app = Flask(__name__)
app.config.from_object(APP_SETTINGS)

tg = Telegram(TG_BOT_TOKEN)
tg.setWebhook(WEBHOOK_URL)

@app.route('/webhook', methods=['POST'])
def handleRequest():
    
    print(request.get_json())

if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'), port=80)