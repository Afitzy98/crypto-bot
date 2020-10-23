import pandas as pd
import unittest
from unittest import mock

from cryptobot.data import get_data


EXPECTED_COLUMNS = ["Open", "High", "Low", "Close"]

@mock.patch("requests.post", autospec=True)
class TestData(unittest.TestCase):

    @mock.patch("binance.client.Client.get_historical_klines", side_effect=Exception)
    def test_get_data_failing(self, mock_get_klines, mock_req_post):
        get_data("period", "SYM")
        mock_get_klines.assert_called_once()
        mock_req_post.assert_called_once()

    @mock.patch("binance.client.Client.get_historical_klines", return_value=[[0,0,0,0,0]])
    def test_get_data_working(self, mock_get_klines, mock_req_post):
        res = get_data("period", "SYM")
        mock_get_klines.assert_called_once()
        mock_req_post.assert_not_called()
        self.assertEqual(res["Open"].iloc[0], 0)
        self.assertEqual(res["High"].iloc[0], 0)
        self.assertEqual(res["Low"].iloc[0], 0)
        self.assertEqual(res["Close"].iloc[0], 0)

if __name__ == '__main__':
    unittest.main()