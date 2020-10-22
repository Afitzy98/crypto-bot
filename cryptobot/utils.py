from settings import TG_USER_ID
from .scheduler import Scheduler
from .telegram import sendMessage

sched = Scheduler()

switcher = {
    "start": lambda: sched.start(),
    "stop": lambda: sched.shutdown()
}

def handleMessage(message: str):
    return switcher.get(message, lambda: sendMessage("Sorry, I didn't understand that."))()
    
def handleRequest(req: dict):
    message = req["message"]

    if message and message["from"]["id"] == TG_USER_ID:
        return handleMessage(message["text"])
