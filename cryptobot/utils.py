from settings import TG_USER_ID
from flask import current_app as app

from .binance import get_equity
from .portfolio import close_portfolio, open_portfolio
from .scheduler import get_jobs, is_running
from .strategy import task
from .telegram import send_message


switcher = {
    "equity": get_equity,
    "list": get_jobs,
    "start": open_portfolio,
    "running": is_running,
    "stop": close_portfolio,
}


def handle_message(message: str):
    switcher.get(
        message.lower(),
        lambda: send_message(f"Sorry I didn't understand that, you said: {message}"),
    )()


def handle_request(req: dict):
    message = req["message"]
    # if the update is a message and the message was from my telegram account proceed
    if message and message["from"]["id"] == TG_USER_ID:
        return handle_message(message["text"])