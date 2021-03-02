import json
import os
from threading import Thread
from time import time

from flask import current_app as app
from google.cloud import dialogflow

from .binance import handle_exit_positions, update_equity
from .constants import HELP_TEXT, LANGUAGE_CODE, PROJECT_ID, SYMBOLS
from .enums import JobType
from .model import get_current_equity, get_position
from .scheduler import (
    add_analytics_job,
    add_trade_job,
    get_jobs,
    is_running,
    is_running_analytics,
    is_trading,
    sched,
)
from .strategy import task
from .telegram import send_message
from .utils import get_current_ts_dt

SESSION_CLIENT = dialogflow.SessionsClient()


def chatbot_fallback(text):
    with app.app_context():
        session_id = app.config["STAGE"]

        session = SESSION_CLIENT.session_path(PROJECT_ID, str(session_id))

        text_input = dialogflow.TextInput(text=text, language_code=LANGUAGE_CODE)

        query_input = dialogflow.QueryInput(text=text_input)

        response = SESSION_CLIENT.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        send_message(response.query_result.fulfillment_text)


def display_help():
    out = "Here is the list of the commands that I understand:\n\n"

    for h in HELP_TEXT:
        out += f"{h['name']} - {h['value']} \n\n"

    send_message(out)


def exit_trade_positions():
    out = "🛑 Stopped trading with: \n"
    for s in SYMBOLS:
        handle_exit_positions(s, get_position(get_current_ts_dt(), s).position)
        out += f"\u2022 {s}\n"
    send_message(out)
    sched.remove_all_jobs()


def get_equity():
    eq = get_current_equity()
    if eq:
        out = f"Your account is currently worth ${eq.equity} \n\n"

        assets = json.loads(eq.assets)

        for a in assets:
            asset = a["asset"]
            hedge = round(a["hedge"] * 100, 2)
            out += f"{asset}: {hedge}% \n"

        out += f"\nLast updated: {eq.time}"

    else:
        out = "Equity tracking hasn't been set up yet. Start trading to begin tracking your equity."

    send_message(out)


def start_trading():
    if not is_trading():
        add_trade_job(task)
        Thread(target=task).start()
        add_analytics_job(update_equity)

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
        add_analytics_job(update_equity)

    send_message("Strategy logic updated")


switcher = {
    "equity": get_equity,
    "help": display_help,
    "list": get_jobs,
    "start": start_trading,
    "running": is_running,
    "stop": stop_trading,
    "update": update_strategy,
}
