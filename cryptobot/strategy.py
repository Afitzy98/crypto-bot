from datetime import datetime
from math import sqrt

import numpy as np
import pandas as pd

from .binance import get_data, handle_decision
from .constants import SYMBOLS
from .enums import PositionType
from .telegram import send_message


def apply_strategy(data):
    pos = PositionType.NONE

    data["MA5"] = data["Open"].rolling(5).mean()
    data["MA10"] = data["Open"].rolling(10).mean()
    data["MA20"] = data["Open"].rolling(20).mean()

    longs = (data["MA5"] > data["MA20"]) & (data["MA10"] > data["MA20"])

    if longs.values[-1] == True:
        pos = PositionType.LONG

    return pos


def task():
    period = "1 month ago"
    for s in SYMBOLS:
        try:
            d = get_data(period, s)
            pos = apply_strategy(d)
            handle_decision(pos, s)
        except Exception as e:
            send_message(e)
