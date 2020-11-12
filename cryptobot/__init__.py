from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from settings import APP_SETTINGS, DB_URI

db = SQLAlchemy()


def create_app():
    """Construct the core application."""
    app = Flask(__name__)
    app.config.from_object(APP_SETTINGS)
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        from . import routes  # Import routes
        from .scheduler import scheduler
        from .telegram import set_webhook, send_message

        scheduler.start()
        send_message("🔄 Scheduler has restarted")
        set_webhook()
        return app
