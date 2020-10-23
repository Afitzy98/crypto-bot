from settings import TG_USER_ID
from .scheduler import start, shutdown
from .telegram import sendMessage

switcher = {
    "start": lambda: start(),
    "stop": lambda: shutdown()
}

def handleMessage(message: str):
    global switcher
    switcher.get(message.lower(), lambda: sendMessage("Sorry I didn't understand that, you said: {}".format(message)))()
    
def handleRequest(req: dict):
    message = req["message"]
    # if the update is a message and the message was from my telegram account proceed
    if message and message["from"]["id"] == TG_USER_ID:
        return handleMessage(message["text"])
