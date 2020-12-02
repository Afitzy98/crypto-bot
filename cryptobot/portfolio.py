from .binance import get_all_valid_symbols, get_data, handle_exit_positions, get_current_ts_dt
from .constants import NUM_SYMBOLS
from .model import get_position
from .strategy import apply_strategy_on_history, task
from .scheduler import get_symbols, remove_job, add_trade_job, add_portfolio_job, does_portfolio_exist, get_jobs
from .telegram import send_message

def close_portfolio():
  if does_portfolio_exist():
    remove_job("PortfolioManager")
    for sym in get_symbols():
      handle_exit_positions(sym, get_position(get_current_ts_dt(), sym).position)
      remove_job(sym)
  else:
    get_jobs()
    send_message("Say start to begin trading, or help for a list of commands.")

def open_portfolio():
  if not does_portfolio_exist():
    add_portfolio_job(rebalance_portfolio)
    rebalance_portfolio()
  else:
    get_jobs()
    
sort_by_returns = lambda x: x["cumret"]

def rebalance_portfolio():
  send_message("Rebalancing Portfolio, This may take a few minutes...")
  symbols = get_all_valid_symbols()
  lookback = "1 week ago"

  data = []

  for s in symbols:
    d = get_data(lookback, s)
    data.append(apply_strategy_on_history(d, s))

  next_symbols = [x["symbol"] for x in sorted(data, key=sort_by_returns, reverse=True)[:NUM_SYMBOLS]]
  current_symbols = get_symbols()
  for s in current_symbols:
    if s not in next_symbols:
      handle_exit_positions(s, get_position(get_current_ts_dt(), s).position)
      remove_job(s)
    else:
      next_symbols.remove(s)

  for s in next_symbols:
    add_trade_job(task, {"symbol":s})
  
  send_message("Portfolio Rebalanced")



