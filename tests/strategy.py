import unittest
from datetime import datetime
from unittest import mock

import numpy as np
import pandas as pd
from cryptobot import app
from cryptobot.binance import get_data
from cryptobot.enums import Position
from cryptobot.model import HourlyPosition
from cryptobot.strategy import apply_strategy_on_history  # , apply_strategy
from cryptobot.strategy import task

NO_SIDE_RET_VAL = np.zeros((150, 5))
LONG_RET_VAL = np.linspace((1, 1, 1, 1, 1), (150, 150, 150, 150, 150), 150)
HOURLY_POS = HourlyPosition(time=datetime.now(), symbol="TEST", position=Position.LONG)

DF = pd.DataFrame(LONG_RET_VAL, columns=["Open", "High", "Low", "Close", "Volume"])

@mock.patch("requests.post", autospec=True)
class TestStrategy(unittest.TestCase):

    @mock.patch("cryptobot.db.session")
    @mock.patch("cryptobot.model.HourlyPosition")
    def test_strategy_no_side(
        self, mock_get_pos, mock_db_session, mock_req_post
    ):
        mock_get_pos.query.get.return_value = HOURLY_POS
        with app.app_context():
            task(["a", "b"])
            mock_req_post.assert_not_called()



    def test_apply_strategy_on_history(self, mock_req_post):
        res = apply_strategy_on_history(DF, "SYM")
        self.assertEqual(res, {
            "ret": 0.10294117647058823,
            'symbol': 'SYM'
        })

if __name__ == "__main__":
    unittest.main()
