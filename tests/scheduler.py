import unittest
from datetime import datetime
from unittest import mock

from cryptobot.enums import JobType
from cryptobot.scheduler import (add_portfolio_job, add_trade_job,
                                 does_portfolio_exist, get_jobs, is_running,
                                 shutdown, stop_trading, update_symbols)


class MockJob:
    def __init__(self, name, id):
        self.name = name
        self.id = id


JOBS = [MockJob(name="A,B,C", id=1), MockJob(name=JobType.PORTFOLIO_MANAGER, id=3)]
NO_JOBS = []


@mock.patch("requests.post", autospec=True)
class TestScheduler(unittest.TestCase):
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.add_job", autospec=True
    )
    def test_add_trade_job(self, mock_add_job, mock_req_post):
        add_trade_job(lambda x: x, {"symbols": ["s"]})
        mock_add_job.assert_called_once()

    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.add_job", autospec=True
    )
    def test_add_portfolio_job(self, mock_add_job, mock_req_post):
        add_portfolio_job(lambda x: x)
        mock_req_post.assert_not_called()
        mock_add_job.assert_called_once()

    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.get_jobs",
        return_value=JOBS,
    )
    def test_does_portfolio_exist(self, mock_get_jobs, mock_req_post):
        res = does_portfolio_exist()
        self.assertEqual(res, True)
        mock_get_jobs.assert_called_once()




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
        "apscheduler.schedulers.background.BackgroundScheduler.get_jobs",
        return_value=NO_JOBS,
    )   
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.add_job",
    )     
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.remove_job",
        autospec=True
    )    
    def test_update_symbols(self,mock_remove_job,mock_add_job, mock_get_jobs, mock_req_post):
        update_symbols(["B", "C", "D"],  lambda symbols: symbols, lambda symbol, prevPosition: symbol,datetime.now())
        mock_remove_job.assert_not_called()
        mock_get_jobs.assert_called_once()

        
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.get_jobs",
        return_value=JOBS,
    )  
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.remove_all_jobs",
        autospec=True
    ) 
    def test_stop_trading(self, mock_remove_jobs,mock_get_jobs, mock_req_post):
        stop_trading(lambda symbol, prevPosition: symbol, datetime.now())
        mock_get_jobs.assert_called_once()
        mock_req_post.assert_called_once()
        mock_remove_jobs.assert_called_once()

    
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.get_jobs",
        return_value=NO_JOBS,
    )   
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.remove_all_jobs",
        autospec=True
    )   
    def test_stop_trading_no_jobs(self, mock_remove_jobs, mock_get_jobs, mock_req_post):
        stop_trading(lambda symbol, prevPosition: symbol, datetime.now())
        mock_get_jobs.assert_called_once()
        mock_remove_jobs.assert_called_once()
        mock_req_post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
