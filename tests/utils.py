import unittest
from unittest import mock

from cryptobot.utils import handle_request
from settings import TG_USER_ID

MESSAGE1 = "running"


REQ1 = {"message": {"from": {"id": TG_USER_ID}, "text": MESSAGE1}}

REQ2 = {"message": {"from": {"id": TG_USER_ID}, "text": "test"}}

REQ3 = {"message": {"from": {"id": "NONE"}, "text": MESSAGE1}}


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


if __name__ == "__main__":
    unittest.main()