from flask import Flask
from settings import APP_SETTINGS

app = Flask(__name__)
app.config.from_object(APP_SETTINGS)

from cryptobot.binance import start_binance_order_socket
from cryptobot.telegram import set_webhook
from cryptobot.utils import handle_request
from cryptobot import routes

set_webhook()

if app.config.get("DEVELOPMENT") == False:
  start_binance_order_socket()

