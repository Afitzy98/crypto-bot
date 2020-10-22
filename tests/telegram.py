import unittest

from cryptobot.telegram import setWebhook, sendMessage
from settings import TG_USER_ID
from unittest import mock

MESSAGE = "TEST"

class TestTelegram(unittest.TestCase):

    @mock.patch("requests.post", autospec=True, side_effect=Exception)
    def test_set_webhook_failing(self, mock_req_post):
        setWebhook()
        mock_req_post.assert_called_once()

    @mock.patch("requests.post", autospec=True)
    def test_set_webhook_working(self, mock_req_post):
        sendMessage(MESSAGE)
        mock_req_post.assert_called_once()

    @mock.patch("requests.post", autospec=True, side_effect=Exception)
    def test_send_message_failing(self, mock_req_post):
        sendMessage(MESSAGE)
        mock_req_post.assert_called_once()

    @mock.patch("requests.post", autospec=True)
    def test_send_message_working(self, mock_req_post):
        setWebhook()
        mock_req_post.assert_called_once()


if __name__ == '__main__':
    unittest.main()