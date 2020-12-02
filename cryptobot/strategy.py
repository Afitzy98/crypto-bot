from datetime import datetime
import pandas as pd
import numpy as np
from math import sqrt
from cryptobot.binance import get_data, handle_decision
from cryptobot.telegram import send_message
from cryptobot.enums import Position


def apply_strategy_on_history(asset, symbol):
  try:
    lastPos = 0
    nextPos = 0
    data = asset.copy(deep=True)
    data["Returns"] = (data["Close"] - data["Close"].shift(1)) / data["Close"].shift(1)

    data["MA25"] = data["Close"].rolling(25).mean()

    data['ewm'] = data['Close'].ewm(span=20,min_periods=0,adjust=False,ignore_na=False).mean()

    data["longs"] = (data['ewm'] > data['MA25']) 

    positions = np.zeros(data["Open"].size)

    positions[data["longs"]] = 1

    ret = positions * data["Returns"]
    ret[np.isnan(ret)] = 0
    ## HANLE FEES #
    for i in range(0,len(ret)):

      if i < len(ret) - 1:
        nextPos = positions[i+1]
      
      # SINGLE TRADE FEES
      if not lastPos == positions[i] and not nextPos == positions[i]: # pragma: no cover
        ret.iloc[i] -= 0.002
      # CHAINED TRADE FEES
      elif (not lastPos == positions[i] and nextPos == positions[i]) or (lastPos == positions[i] and not nextPos == positions[i]):
        ret.iloc[i] -= 0.001

      if positions[i] == -1: # pragma: no cover
        ret.iloc[i] -= 0.001

      lastPos = positions[i]

    apr = (1+ret).prod() ** (8760/len(ret)) -1
    
    sharpe = ret.mean() * sqrt(8760) / ret.std()

    cumret = (1+ret).cumprod() - 1

    return {
        "symbol": symbol,
        'apr': apr,
        'sharpe': sharpe,
        'cumret': cumret.iloc[-1],
        "numPositions": np.count_nonzero(positions)
    }

  except Exception as e:
    return {
        "symbol": symbol,
        'apr': 0,
        'sharpe': 0,
        'cumret': 0,
        "numPositions": 0
    }

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
    period = "1 week ago"
    asset = get_data(period, symbol)
    pos = apply_strategy(symbol, asset)
    handle_decision(pos, symbol)
