from binance.client import Client
import json 
import numpy as np
import pandas as pd

from .telegram import send_message

client = Client()

def get_data(period, symbol):
  global client
  try:
    data = np.array(client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1HOUR, period)).astype(float)

    return pd.DataFrame(data[:,1:5],index=data[:,0], columns=["Open", "High", "Low", "Close"])

  except Exception:
      send_message("⚠️ Error getting data from Binance...")