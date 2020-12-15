import threading

from .binance import (get_all_valid_symbols, get_current_ts_dt, get_data,
                      handle_exit_positions)
from .constants import NUM_SYMBOLS
from .scheduler import (add_portfolio_job, does_portfolio_exist, get_jobs,
                        stop_trading, update_symbols)
from .strategy import apply_strategy_on_history, task
from .telegram import send_message


def close_portfolio():
  if does_portfolio_exist():
    stop_trading_thread = threading.Thread(target=stop_trading, kwargs={"handle_exit":handle_exit_positions, "timestamp":get_current_ts_dt()})
    stop_trading_thread.start()

  else:
    get_jobs()
    send_message("Say start to begin trading, or help for a list of commands.")
    
sort_by_returns = lambda x: x["ret"]

def rebalance_portfolio():
  send_message("Rebalancing Portfolio, This may take a few minutes...")
  symbols = get_all_valid_symbols()
  lookback = "1 month ago"

  data = []

  for s in symbols:
    d = get_data(lookback, s)
    data.append(apply_strategy_on_history(d, s))

  next_symbols = [x["symbol"] for x in sorted(data, key=sort_by_returns, reverse=True)[:NUM_SYMBOLS]]
  update_symbols(next_symbols, task, handle_exit_positions, get_current_ts_dt())
  
  send_message("Portfolio Rebalanced")


rebalance_thread = threading.Thread(target=rebalance_portfolio)

def open_portfolio():
  if not does_portfolio_exist():
    add_portfolio_job(rebalance_portfolio)
    rebalance_thread.start()
  else:
    get_jobs()
