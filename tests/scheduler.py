import unittest
from unittest import mock

from cryptobot.scheduler import start, shutdown


@mock.patch("requests.post", autospec=True)
class TestScheduler(unittest.TestCase):
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.start", autospec=True
    )
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.add_job", autospec=True
    )
    def test_start_scheduler(self, mock_add_job, mock_start_sched, mock_req_post):
        start()
        mock_req_post.assert_called_once()
        mock_add_job.assert_called_once()
        mock_start_sched.assert_called_once()

    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.shutdown", autospec=True
    )
    def test_shutdown_scheduler(self, mock_req_post, mock_start_sched):
        shutdown()
        mock_req_post.assert_called_once()
        mock_start_sched.assert_called_once()


if __name__ == "__main__":
    unittest.main()