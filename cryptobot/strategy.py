from datetime import datetime

from cryptobot.binance import get_data, handle_decision
from cryptobot.telegram import send_message
from cryptobot.enums import Position


def apply_strategy(symbol, asset):
    window = 1
    entryZscore = 0.01
    pos = Position.NONE
    dt = datetime.fromtimestamp(asset.index[-1] / 1000)

    asset['ewm'] = asset['Close'].ewm(span=20,min_periods=0,adjust=False,ignore_na=False).mean()
    asset["MA25"] = asset["Close"].rolling(25).mean()

    longPos =  asset["ewm"].iloc[-1] > asset["MA25"].iloc[-1]
    shortPos = False # LONG ONLY STRATEGY

    if longPos:
        pos = Position.LONG
    # elif shortPos:
    #     pos = Position.SHORT

    send_message(
        f"📢\t{symbol} \n🕛\tTime: {dt} \n↗️\tShould long: {longPos} \n↘️\tShould short: {shortPos}"
    )

    return pos


def task(symbol: str):
    period = "5 days ago"
    asset = get_data(period, symbol + "USDT")
    pos = apply_strategy(symbol, asset)
    handle_decision(pos, symbol)
