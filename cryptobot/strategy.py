from datetime import datetime
import pandas as pd
import numpy as np
from math import sqrt
from cryptobot.binance import get_data, handle_decision
from cryptobot.telegram import send_message
from cryptobot.enums import Position


def apply_strategy_on_history(asset, symbol):
  lookback = 14
  asset["Returns"] = (asset["Close"] - asset["Close"].shift(lookback)) / asset["Close"].shift(lookback)
  return {
      "symbol": symbol,
      "ret": asset["Returns"].iloc[-1]
  }



def task(symbols: list):
    for s in symbols:
      handle_decision(Position.LONG, s)
