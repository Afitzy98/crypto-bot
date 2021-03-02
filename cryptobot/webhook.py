from settings import TG_USER_ID

from .bot import chatbot_fallback, switcher
from .telegram import send_message


def handle_request(req: dict):
    message = req["message"]
    # if the update is a message and the message was from my telegram account proceed
    if message and message["from"]["id"] == TG_USER_ID:
        switcher.get(
            message["text"].lower(),
            lambda: chatbot_fallback(
                message["text"]
            ),  # if not command pass input to chatbot to interperet
        )()
