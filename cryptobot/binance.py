from binance.client import Client
from binance.enums import *
import json 
import numpy as np
import pandas as pd
from sys import exit
from settings import BINANCE_API_KEY, BINANCE_SECRET_KEY

from cryptobot import app
from .telegram import send_message


client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

def get_data(period: str, symbol: str):
  try:
    data = np.array(client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, period)).astype(float)

    return pd.DataFrame(data[:,1:5],index=data[:,0], columns=["Open", "High", "Low", "Close"])

  except Exception:
      send_message("⚠️ Error getting data from Binance...")

def get_info_for_symbol(symbol: str):
  try:
    info = client.get_margin_account()
    coin = None
    usdt = None

    for asset in info['userAssets']:
      if asset["asset"] == "USDT":
        usdt = asset
      if asset["asset"] == symbol:
        coin = asset

    return {"coin": coin, "usdt": usdt}

  except Exception:
      send_message("⚠️ Error getting data from Binance you should check your account....")  

def get_ticker(symbol: str):
  return client.get_orderbook_ticker(symbol=symbol + "USDT")

def handle_buy_order(symbol: str, quantity: float, DEVELOPMENT: bool):
  try:
    if DEVELOPMENT == True:
      client.create_test_order(
        symbol=symbol + "USDT",
        side=SIDE_BUY,
        type=ORDER_TYPE_MARKET,
        quantity=quantity)
      
      send_message(f"Test order has just been placed for {round(quantity, 2)} {symbol}!")

    else:
      client.create_margin_order(
        symbol=symbol + "USDT",
        side=SIDE_BUY,
        type=ORDER_TYPE_MARKET,
        timeInForce=TIME_IN_FORCE_GTC,
        sideEffectType="AUTO_REPAY",
        quantity=quantity)
    
      send_message(f"Order has just been placed for {round(quantity, 2)} {symbol}!")

  except Exception as e:
      send_message(e)

def handle_decision(longPos: bool, shortPos: bool, symbol: str):
  equity = get_info_for_symbol(symbol)

  if longPos:
    handle_long(symbol, equity)
  
  if shortPos:
    handle_short(symbol, equity)

  else:
    handle_exit_positions(symbol, equity)


def handle_exit_positions(symbol: str, equity: dict):
  borrowedCoin = np.float(equity["coin"]["borrowed"])
  freeCoin = np.float(equity["coin"]["free"])

  if borrowedCoin > 0:
    interest = np.float(equity["coin"]["interest"])
    handle_buy_order(symbol, round(borrowedCoin + interest, 4), app.config.get('DEVELOPMENT'))
  
  if freeCoin > 0:
    handle_sell_order(symbol, round(freeCoin, 4), app.config.get('DEVELOPMENT'), "NO_SIDE_EFFECT")


def handle_long(symbol: str, equity: dict):
  freeUSDT = np.float(equity["usdt"]['free'])
  if freeUSDT > 0:
    ticker = get_ticker(symbol)
    askPrice = float(ticker["askPrice"])
    qty = round(freeUSDT / askPrice, 4)
    handle_buy_order(symbol, qty , app.config.get('DEVELOPMENT'))

def handle_sell_order(symbol: str, quantity: float, DEVELOPMENT: bool, sideEffect: str):
  try:
    if DEVELOPMENT == True:
      client.create_test_order(
        symbol=symbol + "USDT",
        side=SIDE_SELL,
        type=ORDER_TYPE_MARKET,
        quantity=quantity)

      send_message(f"Test order has just been placed to sell {round(quantity, 2)} {symbol}!")
      
    else:
      client.create_margin_order(
        symbol=symbol + "USDT",
        side=SIDE_SELL,
        type=ORDER_TYPE_MARKET,
        timeInForce=TIME_IN_FORCE_GTC,
        sideEffectType=sideEffect,
        quantity=quantity)
      
      send_message(f"Order has just been placed to sell {round(quantity, 2)} {symbol}!")

  except Exception as e:
    send_message(e)


def handle_short(symbol: str, equity: dict):
  borrowedCoin = np.float(equity["coin"]['borrowed'])
  if not borrowedCoin > 0:
    freeUSDT = np.float(equity["usdt"]['free'])
    freeCoin = np.float(equity["coin"]['free'])

    ticker = get_ticker(symbol)

    qty = 0
    if freeUSDT > 0:
      qty = freeUSDT / float(ticker["askPrice"])
    else:
      qty = freeCoin # * 2 ?? account for selling both coin and shorted coin? do you have to make two

    handle_sell_order(symbol, round(qty, 4), app.config.get('DEVELOPMENT'), "MARGIN_BUY")



