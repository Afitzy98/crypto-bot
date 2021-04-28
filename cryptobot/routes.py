import json
from datetime import date, datetime, timedelta

from flask import render_template, request
from settings import TG_BOT_TOKEN

from cryptobot import app

from .model import get_equity_history_within_time
from .webhook import handle_request


@app.route("/", methods=["GET"])
def root():
    return "ok"


@app.route("/{}".format(TG_BOT_TOKEN), methods=["POST"])
def webhook_endpoint():
    try:
        req = request.get_json()
        handle_request(req)
        return "ok"
    except Exception as e:
        return f"ERROR.WHILE_HANDLING_REQUEST"


@app.route("/stats", methods=["GET"])
def stats():
    frm = request.args.get("from")
    to = request.args.get("to")
    if frm is not None:
        frm = datetime.strptime(frm, "%d/%m/%y").date()

    if to is not None:
        to = datetime.strptime(to, "%d/%m/%y").date()
    else:
        to = date.today()

    history = get_equity_history_within_time(frm, to)
    initial_equity = history[0].equity
    initial_hedges = json.loads(history[0].assets)
    pnl = []
    pnl_percent = []
    equity_division = []

    for r in history:
        curr_pnl = r.equity - initial_equity
        pnl.append((r.time, curr_pnl))
        pnl_percent.append((r.time, (curr_pnl / initial_equity) * 100))
        hedges = json.loads(r.assets)
        equity_division.append(
            (tuple([r.time.isoformat()] + [h["hedge"] for h in hedges]))
        )

    return render_template(
        "index.html",
        pnl=pnl,
        pnl_percent=pnl_percent,
        equity_division=equity_division,
    )
