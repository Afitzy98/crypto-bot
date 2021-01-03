import unittest
from datetime import datetime
from unittest import mock

import numpy as np
import pandas as pd
from cryptobot import app
from cryptobot.binance import get_data
from cryptobot.enums import Position
from cryptobot.model import HourlyPosition
from cryptobot.strategy import apply_strategy, task

NO_SIDE_RET_VAL = np.zeros((150, 5))
LONG_RET_VAL = np.linspace((1, 1, 1, 1, 1), (150, 150, 150, 150, 150), 150)
HOURLY_POS = HourlyPosition(time=datetime.now(), symbol="TEST", position=Position.NONE)

DF = pd.DataFrame(LONG_RET_VAL, columns=["Open", "High", "Low", "Close", "Volume"])

@mock.patch("requests.post", autospec=True)
class TestStrategy(unittest.TestCase):

    @mock.patch("cryptobot.db.session")
    @mock.patch("cryptobot.model.HourlyPosition")
    @mock.patch(
        "binance.client.Client.get_historical_klines", side_effect=Exception
    )
    def test_task_failing(
        self, mock_get_data, mock_get_pos, mock_db_session, mock_req_post
    ):
        with app.app_context():
            task()
            mock_get_pos.assert_not_called()
            mock_get_data.assert_called()
            mock_req_post.assert_called()


    @mock.patch("cryptobot.db.session")
    @mock.patch("cryptobot.model.HourlyPosition")
    @mock.patch(
        "binance.client.Client.get_historical_klines", return_value=NO_SIDE_RET_VAL
    )
    def test_strategy_no_side(
        self, mock_get_data, mock_get_pos, mock_db_session, mock_req_post
    ):
        mock_get_pos.query.get.return_value = HOURLY_POS
        with app.app_context():
            task()
            mock_get_pos.assert_called()
            mock_get_data.assert_called()
            mock_req_post.assert_not_called()

    def test_strategy_long(self, mock_req_post):
        pos = apply_strategy(DF)
        mock_req_post.assert_not_called()
        self.assertEqual(pos, Position.LONG)

if __name__ == "__main__":
    unittest.main()
