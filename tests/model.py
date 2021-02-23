import os
import unittest
from datetime import datetime
from unittest import mock

import numpy as np
from cryptobot import app
from cryptobot.binance import get_data
from cryptobot.enums import PositionType
from cryptobot.model import (Position, add_equity_record, add_position,
                             get_equity_history, get_position)

from .constants import EQUITY_RECORD

HOURLY_POS = Position(time=datetime.now(), symbol="TEST", position=PositionType.NONE)


@mock.patch.dict(os.environ, {"APP_SETTINGS": "config.TestingConfig"})
@mock.patch("requests.post", autospec=True)
class TestModel(unittest.TestCase):
    @mock.patch("cryptobot.model.Position")
    def test_get_pos(self, mock_get_pos, mock_req_post):
        mock_get_pos.query.get.return_value = HOURLY_POS
        with app.app_context():
            res = get_position(datetime.now(), "")
            self.assertEqual(res, HOURLY_POS)

    @mock.patch("cryptobot.model.Position")
    def test_get_pos_that_doesnt_exist(self, mock_get_pos, mock_req_post):
        mock_get_pos.query.get.return_value = None
        with app.app_context():
            res = get_position(datetime.now(), "")
            self.assertEqual(PositionType.NONE, HOURLY_POS.position)

    @mock.patch("cryptobot.model.Position")
    @mock.patch("cryptobot.db.session.add", side_effect=Exception)
    @mock.patch("cryptobot.db.session.commit")
    @mock.patch("cryptobot.db.session.delete")
    def test_add_pos_failing(
        self, mock_db_delete, mock_db_commit, mock_add, mock_get_pos, mock_req_post
    ):
        mock_get_pos.query.get.return_value = None
        with app.app_context():
            add_position(datetime.now(), "", PositionType.NONE)
            mock_add.assert_called_once()
            mock_db_commit.assert_not_called()
            mock_db_delete.assert_not_called()

    @mock.patch("cryptobot.model.Position")
    @mock.patch("cryptobot.db.session.add")
    @mock.patch("cryptobot.db.session.commit")
    @mock.patch("cryptobot.db.session.delete")
    def test_add_pos(
        self, mock_db_delete, mock_db_commit, mock_add, mock_get_pos, mock_req_post
    ):
        mock_get_pos.query.get.return_value = HOURLY_POS
        with app.app_context():
            add_position(datetime.now(), "", PositionType.NONE)
            mock_add.assert_called_once()
            mock_db_commit.assert_called_once()
            mock_db_delete.assert_called_once()

    @mock.patch("cryptobot.model.EquityRecord")
    def test_get_equity_history(self, mock_eq_record, mock_req_post):
        get_equity_history()
        mock_eq_record.query.all.assert_called_once()

    @mock.patch("cryptobot.model.EquityRecord")
    @mock.patch("cryptobot.db.session.add")
    @mock.patch("cryptobot.db.session.commit")
    @mock.patch("cryptobot.db.session.delete")
    def test_get_equity_record(
        self, mock_db_delete, mock_db_commit, mock_db_add, mock_eq_record, mock_req_post
    ):
        mock_eq_record.query.get.return_value = EQUITY_RECORD
        add_equity_record(datetime.now(), 0.0, "")
        mock_db_add.assert_called_once()
        mock_db_commit.assert_called_once()
        mock_db_delete.assert_called_once()

    @mock.patch("cryptobot.model.EquityRecord", side_effect=Exception)
    @mock.patch("cryptobot.db.session.add")
    @mock.patch("cryptobot.db.session.commit")
    @mock.patch("cryptobot.db.session.delete")
    def test_get_equity_record_failing(
        self, mock_db_delete, mock_db_commit, mock_db_add, mock_eq_record, mock_req_post
    ):

        mock_eq_record.query.get.return_value = None

        add_equity_record(datetime.now(), 0.0, "")

        mock_db_add.assert_not_called()
        mock_db_commit.assert_not_called()
        mock_db_delete.assert_not_called()
        mock_req_post.assert_called_once()

    @mock.patch("cryptobot.db.session.add")
    @mock.patch("cryptobot.db.session.commit")
    @mock.patch("cryptobot.model.HourlyPosition")
    def test_add_pos_already_entered(
        self, mock_get_pos, mock_db_commit, mock_add, mock_req_post
    ):
        mock_get_pos.query.get.return_value = HOURLY_POS
        with app.app_context():
            add_position(datetime.now(), "", Position.NONE)
            mock_add.assert_not_called()
            mock_db_commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
