from datetime import datetime
import numpy as np
import unittest
from unittest import mock

from cryptobot import app

from cryptobot.binance import get_data
from cryptobot.enums import Position
from cryptobot.model import HourlyPosition, get_position, add_position

HOURLY_POS = HourlyPosition(time=datetime.now(), symbol="TEST", position=Position.NONE)


class TestModel(unittest.TestCase):
    @mock.patch("cryptobot.model.HourlyPosition")
    def test_get_pos(self, mock_get_pos):
        mock_get_pos.query.get.return_value = HOURLY_POS
        with app.app_context():
            res = get_position(datetime.now(), "")
            self.assertEqual(res, HOURLY_POS)

    @mock.patch("cryptobot.model.HourlyPosition")
    def test_get_pos_that_doesnt_exist(self, mock_get_pos):
        mock_get_pos.query.get.return_value = None
        with app.app_context():
            res = get_position(datetime.now(), "")
            self.assertEqual(Position.NONE, HOURLY_POS.position)

    @mock.patch("cryptobot.db.session.add", side_effect=Exception)
    @mock.patch("cryptobot.db.session.commit")
    def test_add_pos_failing(self, mock_db_commit, mock_add):
        with app.app_context():
            add_position(datetime.now(), "", Position.NONE)
            mock_add.assert_called_once()
            mock_db_commit.assert_not_called()

    @mock.patch("cryptobot.db.session.add")
    @mock.patch("cryptobot.db.session.commit")
    def test_add_pos(self, mock_db_commit, mock_add):
        with app.app_context():
            add_position(datetime.now(), "", Position.NONE)
            mock_add.assert_called_once()
            mock_db_commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()