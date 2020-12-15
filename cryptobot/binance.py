import json
import math
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from settings import BINANCE_API_KEY, BINANCE_SECRET_KEY

from binance.client import Client
from binance.enums import *
from cryptobot import app

from .constants import AUTO_REPAY, MARGIN_BUY, NO_SIDE_EFFECT, NUM_SYMBOLS
from .enums import Position
from .model import add_position, get_position
from .scheduler import get_symbols
from .telegram import send_message

client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)


def get_data(period: str, symbol: str):
    try:
        data = np.array(
            client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, period)
        ).astype(float)

        return pd.DataFrame(
            data[:, 1:5], index=data[:, 0], columns=["Open", "High", "Low", "Close"]
        )

    except Exception as e:
        send_message(e)


def get_order_qty(symbol: str, coins_available: float):
    try:
        ticks = "0"
        for filt in client.get_symbol_info(symbol)["filters"]:
            if filt["filterType"] == "LOT_SIZE":
                ticks = filt["stepSize"].find("1") - 2

        return math.floor(coins_available * 10 ** ticks) / float(10 ** ticks)

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


def handle_decision(position: Position, symbol: str):
    prevPosition = get_position(get_previous_ts_dt(), symbol).position
    if position == Position.LONG:
        handle_long(symbol, prevPosition)

    else:
        handle_exit_positions(symbol, prevPosition)

    add_position(get_current_ts_dt(), symbol, position)


def handle_exit_positions(symbol: str, prevPosition: Position):
    if prevPosition == Position.LONG:
        freeCoin = get_balance_for_symbol(symbol)
        qty = get_order_qty(symbol, freeCoin)
        handle_order(
            symbol,
            SIDE_SELL,
            qty,
            app.config.get("DEVELOPMENT"),
        )

def get_all_valid_symbols():
    try:
        data = client.get_exchange_info()["symbols"]
        return [s["symbol"] for s in data if s["symbol"][-4:] == "USDT" and s["status"] == "TRADING"]
    except Exception as e:
        send_message(e)
        return []


def get_useable_usdt_qty(symbol: str):
    usdt_in_coins = 0
    symbols = [s for s in get_symbols() if s != symbol]
    for s in symbols:
        bal = np.float(client.get_asset_balance(asset=s[:-4])["free"])
        ticker = np.float(get_ticker(s)["bidPrice"])
        usdt_in_coins += bal * ticker
    
    free_usdt = np.float(client.get_asset_balance("USDT")["free"])
   

    useable_usdt = (free_usdt + usdt_in_coins) * (1/NUM_SYMBOLS)

    return free_usdt if useable_usdt > free_usdt else useable_usdt


def handle_long(symbol: str, prevPosition: Position):
    if not prevPosition == Position.LONG:
        freeUSDT = get_useable_usdt_qty(symbol)
        askPrice = float(get_ticker(symbol)["askPrice"])
        qty = get_order_qty(symbol, freeUSDT / askPrice)
        handle_order(
            symbol, SIDE_BUY, qty, app.config.get("DEVELOPMENT")
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


def get_current_ts_dt():
    return datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)


def get_previous_ts_dt():
    return datetime.now().replace(microsecond=0, second=0, minute=0, hour=0) - timedelta(days=1)
