from settings import TG_USER_ID

from .scheduler import start, shutdown
from .telegram import send_message

switcher = {
    "start": lambda: start(),
    "stop": lambda: shutdown()
}

def handle_message(message: str):
    global switcher
    switcher.get(message.lower(), lambda: send_message("Sorry I didn't understand that, you said: {}".format(message)))()
    
def handle_request(req: dict):
    message = req["message"]
    # if the update is a message and the message was from my telegram account proceed
    if message and message["from"]["id"] == TG_USER_ID:
        return handle_message(message["text"])
