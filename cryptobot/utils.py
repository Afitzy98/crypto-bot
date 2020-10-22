from settings import TG_USER_ID
from .telegram import sendMessage

def handleMessage(message: str):
    # reply in chat with same message
    sendMessage(message)

def handleRequest(req: dict):
    message = req["message"]

    if message and message["from"]["id"] == TG_USER_ID and message["text"]:
        handleMessage(message["text"])
