import unittest
from unittest import mock

from cryptobot.telegram import set_webhook, send_message

MESSAGE = "TEST"


class TestTelegram(unittest.TestCase):
    @mock.patch("requests.post", autospec=True, side_effect=Exception)
    def test_set_webhook_failing(self, mock_req_post):
        set_webhook()
        mock_req_post.assert_called_once()

    @mock.patch("requests.post", autospec=True)
    def test_set_webhook_working(self, mock_req_post):
        set_webhook()
        mock_req_post.assert_called_once()

    @mock.patch("requests.post", autospec=True, side_effect=Exception)
    def test_send_message_failing(self, mock_req_post):
        send_message(MESSAGE)
        mock_req_post.assert_called_once()

    @mock.patch("requests.post", autospec=True)
    def test_send_message_working(self, mock_req_post):
        send_message(MESSAGE)
        mock_req_post.assert_called_once()


if __name__ == "__main__":
    unittest.main()