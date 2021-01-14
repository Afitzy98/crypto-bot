import unittest
from unittest import mock

import numpy as np
from cryptobot import app
from cryptobot.routes import keep_alive, webhook_endpoint


class TestRoutes(unittest.TestCase):
    def test_keep_alive(self):
        res = keep_alive()
        self.assertEqual(res, "ok")

    def test_handle_request_failing(self):
        with app.test_request_context():
            res = webhook_endpoint()
            self.assertEqual(res, "ERROR.WHILE_HANDLING_REQUEST")

    @mock.patch("cryptobot.webhook.handle_request")
    def test_handle_request_passing(self, mock_handle_request):
        with app.test_request_context(json={"message": ""}):
            res = webhook_endpoint()
            self.assertEqual(res, "ok")


if __name__ == "__main__":
    unittest.main()
