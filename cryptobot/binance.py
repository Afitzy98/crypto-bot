from binance.client import Client
from binance.enums import *
import json
import math
import numpy as np
import pandas as pd
from settings import BINANCE_API_KEY, BINANCE_SECRET_KEY

from cryptobot import app
from .telegram import send_message

client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

state = {"prevPosition": {"shortPos": False, "longPos": False}}


def setState(newState):
    global state
    state = newState


def get_data(period: str, symbol: str):
    try:
        data = np.array(
            client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1HOUR, period)
        ).astype(float)

        return pd.DataFrame(
            data[:, 1:5], index=data[:, 0], columns=["Open", "High", "Low", "Close"]
        )

    except Exception:
        send_message("⚠️ Error getting data from Binance...")


def get_order_qty(symbol: str, coins_available: float):
    ticks = {}
    minQty = 0
    for filt in client.get_symbol_info(symbol + "USDT")["filters"]:
        if filt["filterType"] == "LOT_SIZE":
            ticks[symbol] = filt["stepSize"].find("1") - 2
            minQty = float(filt["minQty"])
            break

    order_quantity = math.floor(coins_available * 10 ** ticks[symbol]) / float(
        10 ** ticks[symbol]
    )

    return [order_quantity, order_quantity > minQty]


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

    except Exception:
        send_message(
            "⚠️ Error getting data from Binance you should check your account...."
        )


def get_ticker(symbol: str):
    return client.get_orderbook_ticker(symbol=symbol + "USDT")


def handle_buy_order(symbol: str, quantity: float, DEVELOPMENT: bool):
    print("Order Quantity: {}".format(quantity))
    try:
        if DEVELOPMENT == True:
            client.create_test_order(
                symbol=symbol + "USDT",
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=quantity,
            )

            send_message(f"Test order has just been placed for {quantity} {symbol}!")

        else:
            client.create_margin_order(
                symbol=symbol + "USDT",
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                sideEffectType="AUTO_REPAY",
                quantity=quantity,
            )

            send_message(f"Order has just been placed for {quantity} {symbol}!")

    except Exception as e:
        send_message(e)


def handle_decision(longPos: bool, shortPos: bool, symbol: str):
    prevPosition = state["prevPosition"]
    equity = get_info_for_symbol(symbol)
    print(
        f"Previous Position - short: {prevPosition['shortPos']} long: {prevPosition['longPos']}"
    )
    if longPos:
        handle_long(symbol, equity, prevPosition)

    if shortPos:
        handle_short(symbol, equity, prevPosition)

    else:
        handle_exit_positions(symbol, equity, prevPosition)

    setState({"prevPosition": {"shortPos": shortPos, "longPos": longPos}})


def handle_exit_positions(symbol: str, equity: dict, prevPosition: dict):

    if prevPosition["shortPos"]:
        borrowedCoin = np.float(equity["coin"]["borrowed"])
        interest = np.float(equity["coin"]["interest"])

        [qty, isValid] = get_order_qty(symbol, borrowedCoin + interest)

        handle_buy_order(symbol, qty, app.config.get("DEVELOPMENT"))

    if prevPosition["longPos"]:
        freeCoin = np.float(equity["coin"]["free"])
        [qty, isValid] = get_order_qty(symbol, freeCoin)
        if isValid:
            handle_sell_order(
                symbol, qty, app.config.get("DEVELOPMENT"), "NO_SIDE_EFFECT"
            )


def handle_long(symbol: str, equity: dict, prevPosition: dict):
    freeUSDT = np.float(equity["usdt"]["free"])
    ticker = get_ticker(symbol)
    askPrice = float(ticker["askPrice"])
    [qty, isValid] = get_order_qty(symbol, freeUSDT / askPrice)

    if not prevPosition["longPos"] and isValid:
        handle_buy_order(symbol, qty, app.config.get("DEVELOPMENT"))


def handle_sell_order(
    symbol: str,
    quantity: float,
    DEVELOPMENT: bool,
    sideEffect: str,
    marginBuyBorrowAmount: float,
):
    try:
        if DEVELOPMENT == True:
            client.create_test_order(
                symbol=symbol + "USDT",
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=quantity,
            )

            send_message(
                f"Test order has just been placed to sell {quantity} {symbol}!"
            )

        else:
            client.create_margin_order(
                symbol=symbol + "USDT",
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                sideEffectType=sideEffect,
                marginBuyBorrowAmount=marginBuyBorrowAmount,
                quantity=quantity,
            )

            send_message(f"Order has just been placed to sell {quantity} {symbol}!")

    except Exception as e:
        send_message(e)


def handle_short(symbol: str, equity: dict, prevPosition: dict):

    if not prevPosition["shortPos"]:

        if prevPosition["longPos"]:
            freeCoin = np.float(equity["coin"]["free"])
            [qty, isValid] = get_order_qty(symbol, freeCoin * 2)
            [marginBuyBorrowAmount, isBorrowValid] = get_order_qty(symbol, qty / 2)

            if isValid and isBorrowValid:
                handle_sell_order(
                    symbol,
                    qty,
                    app.config.get("DEVELOPMENT"),
                    "MARGIN_BUY",
                    marginBuyBorrowAmount,
                )

        else:
            freeUSDT = np.float(equity["usdt"]["free"])
            ticker = get_ticker(symbol)
            [qty, isValid] = get_order_qty(symbol, freeUSDT / float(ticker["askPrice"]))

            if isValid:
                handle_sell_order(
                    symbol, qty, app.config.get("DEVELOPMENT"), "MARGIN_BUY", qty
                )
