from binance.client import Client
from binance.enums import *
import json
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from settings import BINANCE_API_KEY, BINANCE_SECRET_KEY

from cryptobot import app
from .constants import AUTO_REPAY, MARGIN_BUY, NO_SIDE_EFFECT
from .enums import Position
from .model import add_position, get_position
from .telegram import send_message


client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)


def get_data(period: str, symbol: str):
    try:
        data = np.array(
            client.get_historical_klines(symbol, Client.KLINE_INTERVAL_5MINUTE, period)
        ).astype(float)

        return pd.DataFrame(
            data[:, 1:5], index=data[:, 0], columns=["Open", "High", "Low", "Close"]
        )

    except Exception as e:
        send_message(e)


def get_order_qty(symbol: str, coins_available: float):
    try:
        ticks = "0"
        for filt in client.get_symbol_info(symbol + "USDT")["filters"]:
            if filt["filterType"] == "LOT_SIZE":
                ticks = filt["stepSize"].find("1") - 2

        return math.floor(coins_available * 10 ** ticks) / float(10 ** ticks)

    except Exception as e:
        send_message(e)


def get_equity():
    try:
        VALID_FIELDS = ["free", "borrowed", "interest", "netAsset"]
        out = "Asset\t Free\t Borrowed\t Interest\t Net \n"
        for asset in client.get_margin_account()["userAssets"]:
            should_print = False
            sym = asset["asset"]
            part = f"{sym}\t "
            for field in VALID_FIELDS:
                val = float(asset[field])
                part += f"{round(val, 2)}\t "
                if val > 0:
                    should_print = True

            if should_print:
                out += part + "\n"

        send_message(out)

    except Exception as e:
        send_message(e)


def get_info_for_symbol(symbol: str):
    try:
        coin = None
        usdt = None
        for asset in client.get_margin_account()["userAssets"]:
            if asset["asset"] == "USDT":
                usdt = asset
            if asset["asset"] == symbol:
                coin = asset

        return {"coin": coin, "usdt": usdt}

    except Exception as e:
        send_message(e)


def get_ticker(symbol: str):
    return client.get_orderbook_ticker(symbol=symbol + "USDT")


def handle_decision(position: Position, symbol: str):
    prevPosition = get_position(get_previous_ts_dt(), symbol).position

    if position == Position.LONG:
        handle_long(symbol, prevPosition)

    elif position == Position.SHORT:
        handle_short(symbol, prevPosition)

    else:
        handle_exit_positions(symbol, prevPosition)

    add_position(get_current_ts_dt(), symbol, position)


def handle_exit_positions(symbol: str, prevPosition: Position):
    if prevPosition == Position.SHORT:
        equity = get_info_for_symbol(symbol)
        borrowedCoin = np.float(equity["coin"]["borrowed"])
        interest = np.float(equity["coin"]["interest"])

        qtyOwed = get_order_qty(symbol, borrowedCoin + interest)

        handle_order(
            symbol,
            SIDE_BUY,
            AUTO_REPAY,
            qtyOwed,
            0,
            app.config.get("DEVELOPMENT"),
        )

    if prevPosition == Position.LONG:
        equity = get_info_for_symbol(symbol)
        freeCoin = np.float(equity["coin"]["free"])
        qty = get_order_qty(symbol, freeCoin)
        handle_order(
            symbol,
            SIDE_SELL,
            NO_SIDE_EFFECT,
            qty,
            0,
            app.config.get("DEVELOPMENT"),
        )


def handle_long(symbol: str, prevPosition: Position):
    if not prevPosition == Position.LONG:
        equity = get_info_for_symbol(symbol)
        freeUSDT = np.float(equity["usdt"]["free"])
        ticker = get_ticker(symbol)
        askPrice = float(ticker["askPrice"])
        qty = get_order_qty(symbol, freeUSDT / askPrice)
        handle_order(
            symbol, SIDE_BUY, AUTO_REPAY, qty, 0, app.config.get("DEVELOPMENT")
        )


def handle_short(symbol: str, prevPosition: Position):
    if prevPosition == Position.LONG:
        equity = get_info_for_symbol(symbol)
        freeCoin = np.float(equity["coin"]["free"])
        qty = get_order_qty(symbol, freeCoin * 2)
        marginBuyBorrowAmount = get_order_qty(symbol, qty / 2)
        handle_order(
            symbol,
            SIDE_SELL,
            MARGIN_BUY,
            qty,
            marginBuyBorrowAmount,
            app.config.get("DEVELOPMENT"),
        )

    elif not prevPosition == Position.SHORT:
        equity = get_info_for_symbol(symbol)
        freeUSDT = np.float(equity["usdt"]["free"])
        ticker = get_ticker(symbol)
        qty = get_order_qty(symbol, freeUSDT / float(ticker["askPrice"]))

        handle_order(
            symbol,
            SIDE_SELL,
            MARGIN_BUY,
            qty,
            qty,
            app.config.get("DEVELOPMENT"),
        )


def handle_order(
    symbol: str,
    side: str,
    sideEffectType: str,
    quantity: float,
    marginBuyBorrowAmount: float,
    DEVELOPMENT: bool,
):
    try:
        kwargs = {
            "symbol": symbol + "USDT",
            "side": side,
            "type": ORDER_TYPE_MARKET,
            "quantity": quantity,
        }

        if marginBuyBorrowAmount > 0 and not DEVELOPMENT:
            kwargs["marginBuyBorrowAmount"] = marginBuyBorrowAmount

        if DEVELOPMENT:
            client.create_test_order(**kwargs)
        else:
            kwargs["sideEffectType"] = sideEffectType
            client.create_margin_order(**kwargs)

        send_message(
            f"Order has just been placed for {quantity} {symbol}! Side: {side}"
        )

    except Exception as e:
        send_message(e)


def get_current_ts_dt():
    return datetime.now().replace(microsecond=0, second=0)


def get_previous_ts_dt():
    return datetime.now().replace(microsecond=0, second=0) - timedelta(minutes=5)
