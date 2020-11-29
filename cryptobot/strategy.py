from datetime import datetime

from cryptobot.binance import get_data, handle_decision
from cryptobot.telegram import send_message
from cryptobot.enums import Position


def apply_strategy(symbol, asset):
    window = 60
    entryZscore = 0.01
    lag = 2
    pos = Position.NONE
    dt = datetime.fromtimestamp(asset.index[-1] / 1000)

    currentOpen = asset["Open"].iloc[-1]
    previousOpen = asset["Open"].iloc[-(1+window)]

    ret60 = (currentOpen - previousOpen) / previousOpen

    longPos = currentOpen > ret60
    shortPos = currentOpen < ret60

    if longPos:
        pos = Position.LONG
    elif shortPos:
        pos = Position.SHORT

    send_message(
        f"📢\t{symbol} \n🕛\tTime: {dt} \n↗️\tShould long: {longPos} \n↘️\tShould short: {shortPos}"
    )

    return pos


def task(symbol: str):
    period = "5 days ago"
    asset = get_data(period, symbol + "USDT")
    pos = apply_strategy(symbol, asset)
    handle_decision(pos, symbol)
