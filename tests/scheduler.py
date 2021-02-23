import os
import unittest
from datetime import datetime
from unittest import mock

from cryptobot.scheduler import (
    add_trade_job,
    get_jobs,
    is_running,
    is_running_analytics,
    shutdown,
)

from .constants import JOBS, NO_JOBS


@mock.patch.dict(os.environ, {"APP_SETTINGS": "config.TestingConfig"})
@mock.patch("requests.post", autospec=True)
class TestScheduler(unittest.TestCase):
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.add_job", autospec=True
    )
    def test_add_trade_job(self, mock_add_job, mock_req_post):
        add_trade_job(lambda x: x)
        mock_add_job.assert_called_once()

    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.get_jobs",
        return_value=NO_JOBS,
    )
    def test_get_jobs_empty(self, mock_get_jobs, mock_req_post):
        get_jobs()
        mock_get_jobs.assert_called_once()
        mock_req_post.assert_called_once()

    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.get_jobs",
        return_value=JOBS,
    )
    def test_get_jobs(self, mock_get_jobs, mock_req_post):
        get_jobs()
        mock_get_jobs.assert_called_once()
        mock_req_post.assert_called_once()

    def test_is_running(self, mock_req_post):
        is_running()
        mock_req_post.assert_called_once()

    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.shutdown",
    )
    def test_shutdown(self, mock_shutdown, mock_req_post):
        shutdown()
        mock_shutdown.assert_called_once()

    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.shutdown",
        side_effect=Exception,
    )
    def test_shutdown_failing(self, mock_shutdown, mock_req_post):
        shutdown()
        mock_shutdown.assert_called_once()

    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.get_jobs",
        return_value=JOBS,
    )
    def test_is_running_analytics(self, mock_get_jobs, mock_req_post):
        res = is_running_analytics()
        mock_get_jobs.assert_called_once()
        self.assertEqual(True, res)


if __name__ == "__main__":
    unittest.main()
