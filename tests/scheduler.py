import unittest
from unittest import mock

from cryptobot.scheduler import add_job, get_jobs, remove_job, is_running, shutdown


class MockJob:
    def __init__(self, name, id):
        self.name = name
        self.id = id


JOBS = [MockJob(name="test", id=1), MockJob(name="test2", id=2)]
NO_JOBS = []


@mock.patch("requests.post", autospec=True)
class TestScheduler(unittest.TestCase):
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.add_job", autospec=True
    )
    def test_add_job(self, mock_add_job, mock_req_post):
        add_job(lambda x: x, {"symbol": "s"})
        mock_req_post.assert_called_once()
        mock_add_job.assert_called_once()

    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.remove_job",
        autospec=True,
    )
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.get_jobs",
        return_value=JOBS,
    )
    def test_remove_job(self, mock_get_jobs, mock_remove_job, mock_req_post):
        remove_job("test")
        mock_req_post.assert_called_once()
        mock_get_jobs.assert_called_once()
        mock_remove_job.assert_called_once()

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


if __name__ == "__main__":
    unittest.main()