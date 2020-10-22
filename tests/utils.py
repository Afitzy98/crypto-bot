import unittest

from cryptobot.utils import handleRequest
from settings import TG_USER_ID
from unittest import mock

MESSAGE = "TEST"

req1 = { "message" : { "from" : { "id": TG_USER_ID }, "text": MESSAGE } }
req2 = { "message" : { "from" : { "id": "NONE" }, "text": MESSAGE } }

@mock.patch("requests.post", autospec=True)
class TestUtils(unittest.TestCase):


    def test_handle_valid_message_request(self, mock_req_post):
        self.assertEqual(handleRequest(req1), MESSAGE)

    def test_handle_invalid_message_request(self, mock_req_post):
        self.assertEqual(handleRequest(req2), None)


if __name__ == '__main__':
    unittest.main()