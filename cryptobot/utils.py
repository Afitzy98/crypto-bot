from settings import TG_USER_ID
from flask import current_app as app

from .scheduler import get_jobs, add_job, remove_job, is_running
from .strategy import hourly_task
from .telegram import send_message


switcher = {
    "start": add_job,
    "stop": remove_job,
    "list": get_jobs,
    "running": is_running,
}


def handle_message(message: str):
    parts = message.split()

    func = switcher.get(
        parts[0].lower(),
        lambda: send_message(f"Sorry I didn't understand that, you said: {message}"),
    )

    if func.__code__.co_argcount == 0:
        func()
    elif func.__code__.co_argcount == 1:
        func(parts[1])
    else:
        func(hourly_task, kwargs={"symbol": parts[1]})


def handle_request(req: dict):
    message = req["message"]
    # if the update is a message and the message was from my telegram account proceed
    if message and message["from"]["id"] == TG_USER_ID:
        return handle_message(message["text"])