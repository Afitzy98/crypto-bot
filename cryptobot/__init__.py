from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from settings import APP_SETTINGS, DB_URI

app = Flask(__name__)
app.config.from_object(APP_SETTINGS)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

db.create_all()
db.session.commit()

from . import routes  # Import routes
from .scheduler import sched
from .telegram import send_message, set_webhook

sched.start()
send_message("🔄 Scheduler has restarted")
set_webhook()
