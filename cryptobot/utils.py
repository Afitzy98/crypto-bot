from settings import TG_USER_ID

from .scheduler import start, shutdown
from .telegram import send_message
from .binance import setState

switcher = {"start": lambda: start(), "stop": lambda: shutdown(), "state": setState}


def str_to_bool(string: str):
    return string.lower() in ("yes", "true", "t", "1", "True")


def handle_message(message: str):
    global switcher

    keys = switcher.keys()

    for key in keys:
        if key in message.lower():
            func = switcher.get(
                key,
                lambda: send_message(
                    "Sorry I didn't understand that, you said: {}".format(message)
                ),
            )
            if key == "state":
                state = message.lower().split()

                shortPos = str_to_bool(state[1])
                longPos = str_to_bool(state[2])

                func(
                    {
                        "prevPosition": {
                            "shortPos": shortPos,
                            "longPos": longPos,
                        }
                    }
                )
                send_message(f"Previous Position - short: {shortPos} long: {longPos}")

            else:
                func()


def handle_request(req: dict):
    message = req["message"]
    # if the update is a message and the message was from my telegram account proceed
    if message and message["from"]["id"] == TG_USER_ID:
        return handle_message(message["text"])
