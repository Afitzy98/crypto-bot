from binance.client import Client
from binance.enums import *
from binance.websockets import BinanceSocketManager
import json 
import numpy as np
import pandas as pd
from sys import exit
from settings import BINANCE_API_KEY, BINANCE_SECRET_KEY

from cryptobot import app
from .telegram import send_message


client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
socket_manager = BinanceSocketManager(client)

def borrow_coin(symbol: str, freeUSDT: float, freeCoin: float):
  ticker = get_ticker(symbol + "USDT")

  amount = 0
  if freeUSDT > 0:
    amount = freeUSDT * ticker["bidPrice"]
  else:
    amount = freeCoin

  return client.create_margin_loan(asset=symbol, amount=amount)

def get_data(period: str, symbol: str):
  try:
    data = np.array(client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1HOUR, period)).astype(float)

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
  order = None
  try:
    if DEVELOPMENT == True:
      order = client.create_test_order(
        symbol=symbol + "USDT",
        side=SIDE_BUY,
        type=ORDER_TYPE_MARKET,
        quantity=round(quantity, 5))
      
      send_message(f"Test order has just been placed for {round(quantity, 2)} {symbol}!")

    else:
      order = client.create_margin_order(
        symbol=symbol + "USDT",
        side=SIDE_BUY,
        type=ORDER_TYPE_MARKET,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=round(quantity, 5))
    
      send_message(f"Order has just been placed for {round(quantity, 2)} {symbol}!")

  except Exception as e:
      send_message(e)

  return order

def handle_decision(side: str, symbol: str):
  equity = get_info_for_symbol(symbol)

  if side == "long":
    return handle_long(symbol, equity)
  
  if side == "short":
    return handle_short(symbol, equity)

  else:
    return handle_exit_positions(symbol, equity)


def handle_exit_positions(symbol: str, equity: dict):
  borrowedCoin = np.float(equity["coin"]["borrowed"])
  freeCoin = np.float(equity["coin"]["free"])

  if borrowedCoin > 0:
    interest = np.float(equity["coin"]["interest"])
    handle_buy_order(symbol, borrowedCoin + interest, app.config.get('DEVELOPMENT'))
  
  if freeCoin > 0:
    handle_sell_order(symbol, freeCoin, app.config.get('DEVELOPMENT'))


def handle_long(symbol: str, equity: dict):
  freeUSDT = np.float(equity["usdt"]['free'])
  if freeUSDT > 0:
    bidPrice = get_ticker(symbol)["bidPrice"]
    qty = freeUSDT / bidPrice
    return handle_buy_order(symbol, qty, app.config.get('DEVELOPMENT'))

def handle_sell_order(symbol: str, quantity: float, DEVELOPMENT: bool):
  order = None
  try:
    if DEVELOPMENT == True:
      order = client.create_test_order(
        symbol=symbol + "USDT",
        side=SIDE_SELL,
        type=ORDER_TYPE_MARKET,
        quantity=round(quantity, 5))

      send_message(f"Test order has just been placed to sell {round(quantity, 2)} {symbol}!")
      
    else:
      order = client.create_margin_order(
        symbol=symbol + "USDT",
        side=SIDE_SELL,
        type=ORDER_TYPE_MARKET,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=round(quantity, 5))
      
      send_message(f"Order has just been placed to sell {round(quantity, 2)} {symbol}!")

  except Exception as e:
    send_message(e)

  return order

def handle_short(symbol: str, equity: dict):
  borrowedCoin = np.float(equity["coin"]['borrowed'])
  if not borrowedCoin > 0:
    freeUSDT = np.float(equity["usdt"]['free'])
    freeCoin = np.float(equity["coin"]['free'])
    borrow_coin(symbol, freeUSDT, freeCoin)
    info = get_info_for_symbol(symbol)
    freeCoin = np.float(equity["coin"]['free'])
    return handle_sell_order(symbol, freeCoin, app.config.get('DEVELOPMENT'))

def process_message(msg):
  if msg['e'] == 'error':
    socket_manager.close()
    start_binance_order_socket()
  else:
      if msg['e'] == 'executionReport' and msg["S"] == "BUY" and msg["x"] == "TRADE":
        equity = get_info_for_symbol(msg["s"][:3])
        borrowed = np.float(equity["coin"]["borrowed"])
        if borrowed > 0:
          interest = np.float(equity["coin"]["interest"])
          client.repay_margin_loan(asset=msg["s"][:3], amount=borrowed + interest)

def start_binance_order_socket():
  socket_manager.start_user_socket(process_message)  
  socket_manager.start()

