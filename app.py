from flask import Flask, request, jsonify
from settings import APP_SETTINGS, TG_BOT_TOKEN

from cryptobot.telegram import set_webhook
from cryptobot.utils import handle_request

app = Flask(__name__)
app.config.from_object(APP_SETTINGS)

set_webhook()

@app.route("/", methods=["GET"])
def keep_alive():
    return "ok"

@app.route('/{}'.format(TG_BOT_TOKEN), methods=['POST'])
def webhook_endpoint():
    try:
        req = request.get_json()
        handle_request(req)
        return "ok"
    except:
        return "ERROR.WHILE_HANDLING_REQUEST"

if __name__ == '__main__':
    app.run(threaded=True, port=80)