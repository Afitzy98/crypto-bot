from settings import TG_USER_ID
from .scheduler import Scheduler
from .telegram import sendMessage


def handleMessage(message: str, sched: Scheduler):
    # using a dict as a switch statement for functions
    switcher = {
        "start": lambda: sched.start(),
        "stop": lambda: sched.shutdown()
    }
    return switcher.get(message.lower(), lambda: sendMessage("Sorry, I didn't understand that."))()
    
def handleRequest(req: dict):
    message = req["message"]

    # if the update is a message and the message was from my telegram account proceed
    if message and message["from"]["id"] == TG_USER_ID:
        return handleMessage(message["text"])
