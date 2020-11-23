from flask import request

from settings import TG_BOT_TOKEN

from cryptobot import app
from .utils import handle_request


@app.route("/", methods=["GET"])
def keep_alive():
    return "ok"


@app.route("/{}".format(TG_BOT_TOKEN), methods=["POST"])
def webhook_endpoint():
    try:
        req = request.get_json()
        handle_request(req)
        return "ok"
    except Exception as e:
        return str(e)
