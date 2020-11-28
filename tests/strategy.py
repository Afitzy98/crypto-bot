from datetime import datetime
import numpy as np
import unittest
from unittest import mock

from cryptobot import app

from cryptobot.binance import get_data
from cryptobot.enums import Position
from cryptobot.model import HourlyPosition
from cryptobot.strategy import task, apply_strategy

NO_SIDE_RET_VAL = np.zeros((150, 5))
LONG_RET_VAL = np.linspace((1, 1, 1, 1, 1), (150, 150, 150, 150, 150), 150)
SHORT_RET_VAL = np.linspace((150, 150, 150, 150, 150), (1, 1, 1, 1, 1), 150)
HOURLY_POS = HourlyPosition(time=datetime.now(), symbol="TEST", position=Position.NONE)


@mock.patch("requests.post", autospec=True)
class TestStrategy(unittest.TestCase):
    @mock.patch(
        "binance.client.Client.get_historical_klines", return_value=NO_SIDE_RET_VAL
    )
    @mock.patch("cryptobot.db.session")
    @mock.patch("cryptobot.model.HourlyPosition")
    def test_strategy_no_side(
        self, mock_get_pos, mock_db_session, mock_get_klines, mock_req_post
    ):
        mock_get_pos.query.get.return_value = HOURLY_POS
        with app.app_context():
            task("")
            mock_get_klines.assert_called_once()
            mock_req_post.assert_called_once()
            mock_get_pos.assert_called_once()

    @mock.patch(
        "binance.client.Client.get_historical_klines", return_value=LONG_RET_VAL
    )
    def test_strategy_long(self, mock_get_klines, mock_req_post):
        asset = get_data("", "")
        pos = apply_strategy("SYM", asset)
        mock_get_klines.assert_called_once()
        mock_req_post.assert_called_once()
        self.assertEqual(Position.LONG, pos)

    @mock.patch(
        "binance.client.Client.get_historical_klines", return_value=SHORT_RET_VAL
    )
    def test_strategy_short(self, mock_get_klines, mock_req_post):
        asset = get_data("", "")
        pos = apply_strategy("SYM", asset)
        mock_get_klines.assert_called_once()
        mock_req_post.assert_called_once()
        self.assertEqual(Position.SHORT, pos)


if __name__ == "__main__":
    unittest.main()