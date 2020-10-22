from cryptobot.telegram import setWebhook
from cryptobot.utils import handleRequest
from flask import Flask, request, jsonify
from settings import APP_SETTINGS, TG_BOT_TOKEN


app = Flask(__name__)
app.config.from_object(APP_SETTINGS)

setWebhook()

@app.route('/{}'.format(TG_BOT_TOKEN), methods=['POST'])
def webhookEndpoint():
    try:
        req = request.get_json()
        handleRequest(req)
        return "ok"
    except:
        return "ERROR.WHILE_HANDLING_REQUEST"

if __name__ == '__main__':
    app.run(threaded=True, ssl_context=('cert.pem', 'key.pem'), port=80)