import unittest
from datetime import datetime
from unittest import mock

from cryptobot import app
from cryptobot.bot import (exit_trade_positions, start_trading, stop_trading,
                           update_strategy)
from cryptobot.enums import Position
from cryptobot.model import HourlyPosition
from settings import TG_USER_ID

from .constants import JOBS, NO_JOBS

PREVIOUS_NONE = HourlyPosition(
    time=datetime.now(), symbol="TEST", position=Position.NONE
)

@mock.patch("requests.post", autospec=True)
class TestUtils(unittest.TestCase):
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.get_jobs",
        return_value=NO_JOBS,
    )
    @mock.patch("threading.Thread.start", autospec=True)
    def test_start_trading(self, mock_thread, mock_get_jobs, mock_req_post):
        start_trading()
        mock_get_jobs.assert_called_once()
        mock_thread.assert_called_once()
        mock_req_post.assert_not_called()


    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.get_jobs",
        return_value=JOBS,
    )
    @mock.patch("threading.Thread.start", autospec=True)
    def test_start_trading_while_trading(self, mock_thread, mock_get_jobs, mock_req_post):
        start_trading()
        mock_get_jobs.assert_called()
        mock_thread.assert_not_called()
        mock_req_post.assert_called_once()


    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.get_jobs",
        return_value=JOBS,
    )
    @mock.patch("threading.Thread.start", autospec=True)
    def test_stop_trading(self, mock_thread, mock_get_jobs, mock_req_post):
        stop_trading()
        mock_get_jobs.assert_called_once()
        mock_thread.assert_called_once()
        mock_req_post.assert_not_called()

    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.get_jobs",
        return_value=NO_JOBS,
    )
    @mock.patch("threading.Thread.start", autospec=True)
    def test_stop_trading_while_not_trading(self, mock_thread, mock_get_jobs, mock_req_post):
        stop_trading()
        mock_get_jobs.assert_called()
        mock_thread.assert_not_called()
        mock_req_post.assert_called_once()

    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.remove_all_jobs"
    )
    @mock.patch("cryptobot.model.HourlyPosition")
    def test_exit_positions(self, mock_get_pos, mock_remove_jobs, mock_req_post):
        mock_get_pos.query.get.return_value = PREVIOUS_NONE
        with app.app_context():
            exit_trade_positions()
            mock_req_post.assert_called_once()
            mock_remove_jobs.assert_called_once()

    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.remove_all_jobs"
    )
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.add_job"
    )
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.get_jobs",
        return_value=JOBS,
    )
    def test_update_strategy(self, mock_get_jobs, mock_add_job, mock_remove_jobs, mock_req_post):
        update_strategy()
        mock_get_jobs.assert_called_once()
        mock_add_job.assert_called_once()
        mock_remove_jobs.assert_called_once()
        mock_req_post.assert_called_once()

    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.get_jobs",
        return_value=NO_JOBS,
    )
    def test_update_strategy_while_not_trading(self, mock_get_jobs, mock_req_post):
        update_strategy()
        mock_get_jobs.assert_called_once()
        mock_req_post.assert_called_once()

if __name__ == "__main__":
    unittest.main()
