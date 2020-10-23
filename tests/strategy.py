import numpy as np
import unittest
from unittest import mock

from cryptobot.strategy import apply_strategy

NO_SIDE_RET_VAL = np.zeros((150, 5))
LONG_RET_VAL = np.linspace((1,1,1,1,1),(150, 150, 150, 150, 150), 150)
SHORT_RET_VAL = np.linspace((150, 150, 150, 150, 150), (1,1,1,1,1), 150)

@mock.patch("requests.post", autospec=True)
class TestStrategy(unittest.TestCase):

    @mock.patch("binance.client.Client.get_historical_klines", return_value=NO_SIDE_RET_VAL)
    def test_strategy_no_side(self, mock_get_klines, mock_req_post):
        side = apply_strategy("SYM")
        mock_get_klines.assert_called_once()
        mock_req_post.assert_called_once()
        self.assertEqual(side, "none")

    @mock.patch("binance.client.Client.get_historical_klines", return_value=LONG_RET_VAL)
    def test_strategy_long(self, mock_get_klines, mock_req_post):
        side = apply_strategy("SYM")
        mock_get_klines.assert_called_once()
        mock_req_post.assert_called_once()
        self.assertEqual(side, "long")

    @mock.patch("binance.client.Client.get_historical_klines", return_value=SHORT_RET_VAL)
    def test_strategy_short(self, mock_get_klines, mock_req_post):
        side = apply_strategy("SYM")
        mock_get_klines.assert_called_once()
        mock_req_post.assert_called_once()
        self.assertEqual(side, "short")


if __name__ == '__main__':
    unittest.main()