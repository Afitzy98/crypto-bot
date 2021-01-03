import unittest
from datetime import datetime
from unittest import mock

from cryptobot import app
from cryptobot.enums import Position
from cryptobot.model import HourlyPosition
from cryptobot.utils import (exit_trade_positions, handle_request,
                             start_trading, stop_trading)
from settings import TG_USER_ID

from .constants import JOBS, NO_JOBS

MESSAGE1 = "running"


REQ1 = {"message": {"from": {"id": TG_USER_ID}, "text": MESSAGE1}}

REQ2 = {"message": {"from": {"id": TG_USER_ID}, "text": "test"}}

REQ3 = {"message": {"from": {"id": "NONE"}, "text": MESSAGE1}}

PREVIOUS_NONE = HourlyPosition(
    time=datetime.now(), symbol="TEST", position=Position.NONE
)

@mock.patch("requests.post", autospec=True)
class TestUtils(unittest.TestCase):

    def test_handle_valid_message_request(self, mock_req_post):
        handle_request(REQ1)
        mock_req_post.assert_called_once()


    def test_handle_invalid_message_request(self, mock_req_post):
        handle_request(REQ2)
        mock_req_post.assert_called_once()

    def test_handle_invalid_user_id_request(self, mock_req_post):
        handle_request(REQ3)
        mock_req_post.assert_not_called()

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
        "apscheduler.schedulers.background.BackgroundScheduler.remove_all_jobs",
        return_value=JOBS,
    )
    @mock.patch("cryptobot.model.HourlyPosition")
    def test_exit_positions(self, mock_get_pos, mock_remove_jobs, mock_req_post):
        mock_get_pos.query.get.return_value = PREVIOUS_NONE
        with app.app_context():
            exit_trade_positions()
            mock_req_post.assert_called_once()
            mock_remove_jobs.assert_called_once()


if __name__ == "__main__":
    unittest.main()
