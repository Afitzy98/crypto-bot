from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from settings import APP_SETTINGS, DB_URI

from settings import TG_BOT_TOKEN

from cryptobot import create_app
from cryptobot.utils import handle_request
from cryptobot.telegram import set_webhook, send_message
from cryptobot.scheduler import scheduler

if __name__ == "__main__":
    app = create_app()
    app.app_context().push()
    scheduler.start()
    send_message("🔄 Scheduler has restarted")
    set_webhook()
    app.run(threaded=True, use_reloader=False)
