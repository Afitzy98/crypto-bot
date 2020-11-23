import numpy as np
import unittest
from unittest import mock

from cryptobot.routes import keep_alive, webhook_endpoint
from cryptobot import app


class TestRoutes(unittest.TestCase):
    def test_keep_alive(self):
        res = keep_alive()
        self.assertEqual(res, "ok")

    def test_handle_request_failing(self):
        with app.test_request_context():
            res = webhook_endpoint()
            self.assertEqual(res, "ERROR.WHILE_HANDLING_REQUEST")

    def test_handle_request_passing(self):
        with app.test_request_context(json={"message": ""}):
            res = webhook_endpoint()
            self.assertEqual(res, "ok")


if __name__ == "__main__":
    unittest.main()