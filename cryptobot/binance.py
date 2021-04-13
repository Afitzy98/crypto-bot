import json
import math

import numpy as np
import pandas as pd
from settings import BINANCE_API_KEY, BINANCE_SECRET_KEY

from binance.client import Client
from binance.enums import *
from cryptobot import app

from .constants import AUTO_REPAY, MARGIN_BUY, NO_SIDE_EFFECT, SYMBOLS
from .enums import PositionType
from .model import add_equity_record, add_position, get_position
from .telegram import send_message
from .utils import get_current_ts_dt, get_nearest_hour_dt, get_previous_ts_dt

client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)


def get_data(period: str, symbol: str):
    try:
        data = np.array(
            client.get_historical_klines(symbol, Client.KLINE_INTERVAL_4HOUR, period)
        ).astype(float)

        return pd.DataFrame(
            data[:, 1:5], index=data[:, 0], columns=["Open", "High", "Low", "Close"]
        )

    except Exception as e:
        send_message(e)


def update_equity():
    usdt_in_coins = 0

    assets = []

    for s in SYMBOLS:
        bal = np.float(client.get_asset_balance(asset=s[:-4])["free"])
        ticker = np.float(get_ticker(s)["bidPrice"])
        amount_in_usdt = bal * ticker

        assets.append(
            {
                "asset": s[:-4],
                "usdt_total": amount_in_usdt,
            }
        )

        usdt_in_coins += amount_in_usdt

    free_usdt = np.float(client.get_asset_balance("USDT")["free"])

    assets.append(
        {
            "asset": "USDT",
            "usdt_total": free_usdt,
        }
    )

    usdt_equity = round(free_usdt + usdt_in_coins, 2)

    assets = [
        {"asset": a["asset"], "hedge": round(a["usdt_total"] / usdt_equity, 3)}
        for a in assets
    ]

    time = get_nearest_hour_dt()

    add_equity_record(time, usdt_equity, json.dumps(assets))


def get_order_qty(symbol: str, coins_available: float, price: float):
    try:
        ticks = "0"
        minimum = 0
        for filt in client.get_symbol_info(symbol)["filters"]:
            if filt["filterType"] == "LOT_SIZE":
                ticks = filt["stepSize"].find("1") - 2
            if filt["filterType"] == "MIN_NOTIONAL":
                minimum = float(filt["minNotional"]) / price

        qty = math.floor(coins_available * 10 ** ticks) / float(10 ** ticks)
        isValid = qty > minimum

        return qty, isValid

    except Exception as e:
        send_message(e)


def get_balance_for_symbol(symbol: str):
    try:
        coin = client.get_asset_balance(symbol[:-4])
        return float(coin["free"])

    except Exception as e:
        send_message(e)


def get_ticker(symbol: str):
    return client.get_orderbook_ticker(symbol=symbol)


def handle_decision(position: PositionType, symbol: str):
    prevPosition = get_position(get_previous_ts_dt(), symbol).position
    if position == PositionType.LONG:
        handle_long(symbol, prevPosition)

    else:
        handle_exit_positions(symbol, prevPosition)

    add_position(get_current_ts_dt(), symbol, position)


def handle_exit_positions(symbol: str, prevPosition: PositionType):
    if prevPosition == PositionType.LONG:
        freeCoin = get_balance_for_symbol(symbol)
        qty, isValid = get_order_qty(
            symbol, freeCoin, float(get_ticker(symbol)["bidPrice"])
        )

        if isValid:
            handle_order(
                symbol,
                SIDE_SELL,
                qty,
                app.config.get("DEVELOPMENT"),
            )
        else:
            send_message(
                f"❗ Order for {qty} {symbol} could not be placed as it is less than the minumum order quantity"
            )


def get_all_valid_symbols():
    try:
        data = client.get_exchange_info()["symbols"]
        return [
            s["symbol"]
            for s in data
            if s["symbol"][-4:] == "USDT" and s["status"] == "TRADING"
        ]
    except Exception as e:
        send_message(e)
        return []


def get_useable_usdt_qty(symbol: str):
    usdt_in_coins = 0
    symbols = [s for s in SYMBOLS if s != symbol]
    for s in symbols:
        bal = np.float(client.get_asset_balance(asset=s[:-4])["free"])
        ticker = np.float(get_ticker(s)["bidPrice"])
        usdt_in_coins += bal * ticker

    free_usdt = np.float(client.get_asset_balance("USDT")["free"])

    useable_usdt = (free_usdt + usdt_in_coins) * (1 / len(SYMBOLS))

    return free_usdt if useable_usdt > free_usdt else useable_usdt


def handle_long(symbol: str, prevPosition: PositionType):
    if not prevPosition == PositionType.LONG:
        freeUSDT = get_useable_usdt_qty(symbol)
        askPrice = float(get_ticker(symbol)["askPrice"])
        qty, isValid = get_order_qty(symbol, freeUSDT / askPrice, askPrice)
        if isValid:
            handle_order(symbol, SIDE_BUY, qty, app.config.get("DEVELOPMENT"))
        else:
            send_message(
                f"❗ Order for {qty} {symbol} could not be placed as it is less than the minumum order quantity"
            )


def handle_order(
    symbol: str,
    side: str,
    quantity: float,
    DEVELOPMENT: bool,
):
    try:
        kwargs = {
            "symbol": symbol,
            "side": side,
            "type": ORDER_TYPE_MARKET,
            "quantity": quantity,
        }

        if DEVELOPMENT:
            client.create_test_order(**kwargs)
        else:
            client.create_order(**kwargs)

        send_message(
            f"Order has just been placed to {side.lower()} {quantity} {symbol}!"
        )

    except Exception as e:
        send_message(e)
