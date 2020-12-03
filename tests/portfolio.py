import unittest
from unittest import mock
import numpy as np

from cryptobot.constants import PORTFOLIO_MANAGER
from cryptobot.portfolio import open_portfolio, close_portfolio, rebalance_portfolio

class MockJob:
    def __init__(self, name, id):
        self.name = name
        self.id = id

JOBS = [MockJob(name="BTCUSDT", id=1), MockJob(name="OTHERUSDT", id=2), MockJob(name=PORTFOLIO_MANAGER, id=3)]
NO_JOBS = []
LONG_RET_VAL = np.linspace((1, 1, 1, 1, 1), (150, 150, 150, 150, 150), 150)
SYMBOLS_INFO = {"symbols":[{"symbol":"BTCUSDT", "status":"TRADING"},{"symbol":"LTCUSDT", "status":"TRADING"},{"symbol":"ETHUSDT", "status":"TRADING"},{"symbol":"XRPUSDT", "status":"TRADING"},{"symbol":"BNBUSDT", "status":"TRADING"}]}

@mock.patch("requests.post")
class TestPortfolio(unittest.TestCase):

    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.remove_job",
        autospec=True,
    )
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.get_jobs",
        return_value=JOBS,
    )
    def test_close_portfolio(self,mock_get_job, mock_remove_job, mock_req_post):

      close_portfolio() 
      mock_req_post.assert_called()
      mock_remove_job.assert_called()
      mock_get_job.assert_called()
    
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.remove_job",
        autospec=True,
    )
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.get_jobs",
        return_value=NO_JOBS,
    )
    def test_close_portfolio_that_isnt_open(self,mock_get_job, mock_remove_job, mock_req_post):
      close_portfolio() 
      mock_req_post.assert_called()
      mock_remove_job.assert_not_called()
      mock_get_job.assert_called()
      mock_req_post.assert_called()
  
    @mock.patch(
      "apscheduler.schedulers.background.BackgroundScheduler.get_jobs",
      return_value=JOBS,
    )
    def test_open_portfolio_when_portfolio_open(self, mock_get_jobs, mock_req_post):
      open_portfolio()
      mock_get_jobs.assert_called()
      mock_req_post.assert_called()

    # @mock.patch(
    #     "apscheduler.schedulers.background.BackgroundScheduler.add_job",
    #     autospec=True,
    # )
    # @mock.patch(
    #     "apscheduler.schedulers.background.BackgroundScheduler.get_jobs",
    #     return_value=NO_JOBS,
    # )
    # @mock.patch(
    #     "binance.client.Client.get_historical_klines", return_value=LONG_RET_VAL
    # )
    # @mock.patch(
    #     "binance.client.Client.get_exchange_info", return_value=SYMBOLS_INFO
    # )
    # def test_open_portfolio(self, mock_get_symbol_info, mock_get_klines, mock_get_jobs,mock_add_job, mock_req_post):
    #   open_portfolio()
    #   mock_get_symbol_info.assert_called()
    #   mock_get_klines.assert_called()
    #   mock_get_jobs.assert_called()
    #   mock_req_post.assert_called()
    #   mock_add_job.assert_called()

    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.add_job",
        autospec=True,
    )
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.remove_job",
        autospec=True,
    )
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.get_jobs",
        return_value=JOBS,
    )
    @mock.patch(
        "binance.client.Client.get_historical_klines", return_value=LONG_RET_VAL
    )
    @mock.patch(
        "binance.client.Client.get_exchange_info", return_value=SYMBOLS_INFO
    )
    def test_rebalance_portfolio(self,mock_get_symbol_info, mock_get_klines, mock_get_jobs,mock_add_job, mock_remove_job, mock_req_post):
      rebalance_portfolio()
      mock_get_symbol_info.assert_called()
      mock_get_klines.assert_called()
      mock_get_jobs.assert_called()
      mock_req_post.assert_called()
      mock_add_job.assert_called()
      mock_remove_job.assert_called()

if __name__ == "__main__":
    unittest.main()