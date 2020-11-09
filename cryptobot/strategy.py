from datetime import datetime

from cryptobot.binance import get_data, handle_decision
from cryptobot.telegram import send_message


def apply_strategy(symbol, asset):
    window = 96
    entryZscore = 0.01
    lag = 2

    dt = datetime.fromtimestamp(asset.index[-1] / 1000)

    asset["Returns"] = (asset["Close"] - asset["Close"].shift(1)) / asset[
        "Close"
    ].shift(1)
    asset["Std Ret"] = asset["Returns"].rolling(window).std().shift(1)

    currentOpen = asset["Open"].iloc[-1]

    longPos = currentOpen >= asset["High"].iloc[-(1 + lag)] * (
        1 + entryZscore * asset["Std Ret"].iloc[-1]
    )
    shortPos = currentOpen <= asset["Low"].iloc[-(1 + lag)] * (
        1 - entryZscore * asset["Std Ret"].iloc[-1]
    )

    send_message(
        f"\🆕\t{symbol} \n🕛\tTime: {dt} \n↗️\tShould long: {longPos} \n↘️\tShould short: {shortPos}"
    )

    return [longPos, shortPos]


def hourly_task(symbol: str):
    period = "5 days ago"
    asset = get_data(period, symbol + "USDT")
    [longPos, shortPos] = apply_strategy(symbol, asset)
    handle_decision(longPos, shortPos, symbol)
