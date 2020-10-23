import unittest

from cryptobot.utils import handleRequest
from settings import TG_USER_ID
from unittest import mock

MESSAGE1 = "start"
MESSAGE2 = "test"

REQ1 = {"message": {"from": {"id": TG_USER_ID}, "text": MESSAGE1}}

REQ2 = {"message": {"from": {"id": TG_USER_ID}, "text": MESSAGE2}}

REQ3 = {"message": {"from": {"id": "NONE"}, "text": MESSAGE1}}


class TestUtils(unittest.TestCase):
    @mock.patch(
        "apscheduler.schedulers.background.BackgroundScheduler.start", autospec=True
    )
    def test_handle_valid_message_request(self, mock_sched_start):
        handleRequest(REQ1)
        mock_sched_start.assert_called_once()

    @mock.patch("requests.post", autospec=True)
    def test_handle_invalid_message_request(self, mock_req_post):
        handleRequest(REQ2)
        mock_req_post.assert_called_once()

    @mock.patch("requests.post", autospec=True)
    def test_handle_invalid_user_id_request(self, mock_req_post):
        handleRequest(REQ3)
        mock_req_post.assert_not_called()


if __name__ == "__main__":
    unittest.main()