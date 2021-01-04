from threading import Thread

from flask import current_app as app
from settings import TG_USER_ID

from .binance import get_current_ts_dt, handle_exit_positions
from .constants import SYMBOLS
from .enums import JobType
from .model import get_position
from .scheduler import add_trade_job, get_jobs, is_running, is_trading, sched
from .strategy import task
from .telegram import send_message


def start_trading():
    if not is_trading():
        add_trade_job(task)
        Thread(target=task).start()
    else:
        get_jobs()

def stop_trading():
    if is_trading():
        Thread(target=exit_trade_positions).start()
    else:
        get_jobs()

def update_strategy():
    if is_trading():
        sched.remove_all_jobs()
        add_trade_job(task)
        send_message("Strategy logic updated")

    
def exit_trade_positions():
    out = "🛑 Stopped trading with: \n"
    for s in SYMBOLS:
        handle_exit_positions(s, get_position(get_current_ts_dt(), s).position)
        out+= f"\u2022 {s}\n"
    send_message(out)
    sched.remove_all_jobs()

switcher = {
    "list": get_jobs,
    "start": start_trading,
    "running": is_running,
    "stop": stop_trading,
    "update": update_strategy
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
