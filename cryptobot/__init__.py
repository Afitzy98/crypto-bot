from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from settings import APP_SETTINGS, DB_URI


app = Flask(__name__)
app.config.from_object(APP_SETTINGS)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

from cryptobot import routes
from cryptobot.telegram import set_webhook, send_message

send_message("🔄 Scheduler has restarted")
set_webhook()
