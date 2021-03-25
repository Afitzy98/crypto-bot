import os
import unittest
from unittest import mock

import numpy as np
from cryptobot import app
from cryptobot.routes import root, stats, webhook_endpoint

from .constants import EQUITY_HISTORY


@mock.patch.dict(os.environ, {"APP_SETTINGS": "config.TestingConfig"})
class TestRoutes(unittest.TestCase):
    def test_root(self):
        res = root()
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

    @mock.patch("cryptobot.model.EquityRecord")
    def test_get_stats(self, mock_eq_record):
        with app.test_request_context():
            mock_eq_record.query.all.return_value = EQUITY_HISTORY
            stats()


if __name__ == "__main__":
    unittest.main()
