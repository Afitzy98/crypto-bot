from flask import Flask, request, jsonify
from settings import APP_SETTINGS, TG_BOT_TOKEN, WEBHOOK_URL, TG_USER_ID
from cryptobot.telegram import Telegram
from cryptobot.utils import handleMessage

app = Flask(__name__)
app.config.from_object(APP_SETTINGS)

tg = Telegram(TG_BOT_TOKEN)
tg.setWebhook(WEBHOOK_URL)

@app.route('/{}'.format(TG_BOT_TOKEN), methods=['POST'])
def handleRequest():
    
    req = request.get_json()

    if req.message["from"].id == TG_USER_ID and req.message.text:
        handleMessage(req.message.text)

    return 'ok'

if __name__ == '__main__':
    app.run(threaded=True, ssl_context=('cert.pem', 'key.pem'), port=80)