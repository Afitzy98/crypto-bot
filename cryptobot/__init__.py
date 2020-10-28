from flask import Flask
from settings import APP_SETTINGS

app = Flask(__name__)
app.config.from_object(APP_SETTINGS)

from cryptobot.telegram import set_webhook
from cryptobot.utils import handle_request
from cryptobot import routes

set_webhook()

