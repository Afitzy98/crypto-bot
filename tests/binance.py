import unittest
from datetime import datetime
from unittest import mock

import requests
from cryptobot import app
from cryptobot.binance import (get_all_valid_symbols, get_balance_for_symbol,
                               get_data, get_order_qty, handle_decision,
                               handle_exit_positions, handle_long,
                               handle_order)
from cryptobot.enums import JobType, Position
from cryptobot.model import HourlyPosition, add_position, get_position

TICKER = {"askPrice": 10, "bidPrice": 9}
SYMBOL_INFO = {
    "filters": [
        {"filterType": "OTHER"},
        {"filterType": "LOT_SIZE", "stepSize": "0.001", "minQty": "0.01"},
        {"filterType": "MIN_NOTIONAL", "minNotional":"10.0"}
    ]
}
EMPTY_SYMBOL_FILTERS = {"filters": [{"filterType": "OTHER"}]}
EXPECTED_COLUMNS = ["Open", "High", "Low", "Close"]
LONG_ACCOUNT = {
    "userAssets": [{"asset": "BTC", "free": "0"}, {"asset": "USDT", "free": "100"}]
}
SHORT_ACCOUNT = {
    "userAssets": [
        {"asset": "BTC", "free": "0", "borrowed": "0", "free": "0.1", "interest":"0.001"},
        {"asset": "USDT", "free": "100"},
    ]
}
EXIT_POS_ACCOUNT = {
    "userAssets": [
        {
            "asset": "BTC",
            "free": "0",
            "borrowed": "10",
            "interest": "0.1",
            "free": "10",
        },
        {"asset": "USDT", "free": "100"},
    ]
}

PREVIOUS_NONE = HourlyPosition(
    time=datetime.now(), symbol="TEST", position=Position.NONE
)
PREVIOUS_LONG = HourlyPosition(
    time=datetime.now(), symbol="TEST", position=Position.LONG
)

ASSET_BALANCE = {"free":"100"}
INVALID_ASSET_BALANCE = {"free": "0"}

EQUITY_ACCOUNT = {
    "userAssets": [
        {
            "asset": "BTCUSDT",
            "free": "10",
            "borrowed": "0",
            "interest": "0",
            "netAsset": "10",
        },
        {
            "asset": "LTCUSDT",
            "free": "0",
            "borrowed": "0",
            "interest": "0",
            "netAsset": "0",
        },
    ]
}

EXCHANGE_INFO = {"symbols":[
    {"symbol":"BTCUSDT", "status":"TRADING"},
    {"symbol":"LTCUSDT", "status":"TRADING"},    {"symbol":"XRPUSDT", "status":"DOWN"},
    {"symbol":"BTCBUSD", "status":"TRADING"}
]}

class MockJob:
    def __init__(self, name, id):
        self.name = name
        self.id = id

JOBS = [MockJob(name="BTCUSDT,LTCUSDT,XRPUSDT", id=1), MockJob(name=JobType.PORTFOLIO_MANAGER, id=3)]



@mock.patch("requests.post", autospec=True)
class TestData(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    @mock.patch("binance.client.Client.get_asset_balance", side_effect=Exception)
    def test_get_balance(self, mock_get_balance, mock_req_post):
        res = get_balance_for_symbol("BTCUSDT")
        self.assertEqual(None, res)
        mock_req_post.assert_called_once()
        mock_get_balance.assert_called_once()


    @mock.patch("binance.client.Client.get_historical_klines", side_effect=Exception)
    def test_get_data_failing(self, mock_get_klines, mock_req_post):
        get_data("period", "SYM")
        mock_get_klines.assert_called_once()
        mock_req_post.assert_called_once()

    @mock.patch(
        "binance.client.Client.get_historical_klines", return_value=[[0, 0, 0, 0, 0]]
    )
    def test_get_data_working(self, mock_get_klines, mock_req_post):
        res = get_data("period", "SYM")
        mock_get_klines.assert_called_once()
        mock_req_post.assert_not_called()
        self.assertEqual(res["Open"].iloc[0], 0)
        self.assertEqual(res["High"].iloc[0], 0)
        self.assertEqual(res["Low"].iloc[0], 0)
        self.assertEqual(res["Close"].iloc[0], 0)

    @mock.patch("binance.client.Client.get_asset_balance", return_value=ASSET_BALANCE)
    @mock.patch("binance.client.Client.get_orderbook_ticker", return_value=TICKER)
    @mock.patch("binance.client.Client.get_symbol_info", return_value=SYMBOL_INFO)
    @mock.patch("binance.client.Client.create_test_order", autospec=True)
    @mock.patch("cryptobot.db.session")
    @mock.patch("cryptobot.model.HourlyPosition")
    def test_handle_decision_long(
        self,
        mock_get_pos,
        mock_db_session,
        mock_test_order,
        mock_get_symbol_info,
        mock_orderbook_ticker,
        mock_get_account,
        mock_req_post,
    ):
        mock_get_pos.query.get.return_value = PREVIOUS_NONE
        with app.app_context():
            handle_decision(Position.LONG, "BTC")
            mock_test_order.assert_called_once()
            mock_get_symbol_info.assert_called_once()
            mock_orderbook_ticker.assert_called()
            mock_get_account.assert_called()
            mock_req_post.assert_called_once()
            mock_get_pos.assert_called_once()

    @mock.patch(
        "binance.client.Client.get_asset_balance", return_value=ASSET_BALANCE
    )
    @mock.patch("binance.client.Client.get_symbol_info", return_value=SYMBOL_INFO)
    @mock.patch("binance.client.Client.create_test_order", autospec=True)
    @mock.patch("cryptobot.db.session")
    @mock.patch("cryptobot.model.HourlyPosition")
    @mock.patch("binance.client.Client.get_orderbook_ticker", return_value=TICKER)
    def test_handle_decision_no_signal(
        self,
        mock_get_ticker,
        mock_get_pos,
        mock_db_session,
        mock_test_order,
        mock_get_symbol_info,
        mock_get_account,
        mock_req_post,
    ):
        mock_get_pos.query.get.return_value = PREVIOUS_LONG
        with app.app_context():
            handle_decision(Position.NONE, "SYM")
            mock_test_order.assert_called_once()
            mock_get_symbol_info.assert_called_once()
            mock_get_account.assert_called()
            mock_req_post.assert_called_once()
            mock_get_pos.assert_called_once()
            mock_get_ticker.assert_called_once()

    @mock.patch("binance.client.Client.get_symbol_info", return_value=SYMBOL_INFO)
    @mock.patch(
        "binance.client.Client.get_asset_balance", return_value=ASSET_BALANCE
    )
    @mock.patch("binance.client.Client.create_test_order", autospec=True)
    def test_handle_exit_positions(
        self, mock_test_order, mock_get_account, mock_get_symbol, mock_req_post
    ):
        handle_exit_positions(
            "BTCUSDT",
            Position.LONG,
        )
        mock_get_symbol.assert_called()
        mock_get_account.assert_called()
        mock_req_post.assert_called()
        mock_test_order.assert_called()

    @mock.patch("binance.client.Client.get_symbol_info", return_value=SYMBOL_INFO)
    @mock.patch("binance.client.Client.create_test_order", autospec=True)
    def test_handle_exit_positions_doing_nothing(
        self, mock_test_order, mock_get_symbol, mock_req_post
    ):
        handle_exit_positions(
            "SYM",
            {"shortPos": False, "longPos": False},
        )
        mock_get_symbol.assert_not_called()
        mock_req_post.assert_not_called()
        mock_test_order.assert_not_called()

    @mock.patch("binance.client.Client.get_symbol_info", return_value=SYMBOL_INFO)
    @mock.patch("binance.client.Client.create_test_order", autospec=True)
    def test_handle_long_doing_nothing(
        self,  mock_test_order, mock_get_symbol, mock_req_post
    ):
        handle_long(
            "",
            Position.LONG,
        )
        mock_get_symbol.assert_not_called()
        mock_req_post.assert_not_called()
        mock_test_order.assert_not_called()


    @mock.patch("binance.client.Client.get_symbol_info")
    def test_get_order_qty_no_filter(self, mock_get_symbol, mock_req_post):
        mock_get_symbol.return_value = EMPTY_SYMBOL_FILTERS
        res = get_order_qty("", 1, 1)
        mock_get_symbol.assert_called_once()
        mock_req_post.assert_not_called()
        self.assertEqual(0, res)

    @mock.patch("binance.client.Client.get_symbol_info", side_effect=Exception)
    def test_get_order_qty_no_filter(self, mock_get_symbol, mock_req_post):
        res = get_order_qty("", 1, 1)
        mock_get_symbol.assert_called_once()
        mock_req_post.assert_called_once()
        self.assertEqual(None, res)



    @mock.patch("binance.client.Client.create_order", side_effect=Exception)
    def test_handle_order_failing(self, mock_create_order, mock_req_post):
        handle_order("BTCUSDT", "BUY", 1, False)
        mock_create_order.assert_called_once()
        mock_req_post.assert_called_once()

    @mock.patch("binance.client.Client.get_exchange_info", side_effect=Exception)
    def test_get_all_valid_symbols_failing(self, mock_get_exchange_info, mock_req_post):
        res = get_all_valid_symbols()
        self.assertEqual([], res)
        mock_req_post.assert_called_once()
        mock_get_exchange_info.assert_called_once()

    @mock.patch("binance.client.Client.get_exchange_info", return_value=EXCHANGE_INFO)
    def test_get_all_valid_symbols(self, mock_get_exchange_info, mock_req_post):
        res = get_all_valid_symbols()
        self.assertEqual(["BTCUSDT","LTCUSDT"], res)
        mock_req_post.assert_not_called()
        mock_get_exchange_info.assert_called_once()


    @mock.patch("binance.client.Client.get_asset_balance", return_value=INVALID_ASSET_BALANCE)
    @mock.patch("binance.client.Client.get_orderbook_ticker", return_value=TICKER)
    @mock.patch("binance.client.Client.get_symbol_info", return_value=SYMBOL_INFO)
    def test_buy_invalid_qty(self, mock_get_symbol, mock_get_ticker, mock_get_asset_bal, mock_req_post):
        handle_long("SYM", Position.NONE)
        mock_get_symbol.assert_called_once()
        mock_get_asset_bal.assert_called()
        mock_get_ticker.assert_called()
        mock_req_post.assert_called_once()
    
    @mock.patch("binance.client.Client.get_symbol_info", return_value=SYMBOL_INFO)
    @mock.patch(
        "binance.client.Client.get_asset_balance", return_value=INVALID_ASSET_BALANCE
    )
    @mock.patch("binance.client.Client.get_orderbook_ticker", return_value=TICKER)
    def test_sell_invalid_qty(self, mock_get_ticker, mock_get_asset_bal, mock_get_symbol, mock_req_post):
        handle_exit_positions("SYM",  Position.LONG)
        mock_get_ticker.assert_called_once()
        mock_get_asset_bal.assert_called_once()
        mock_get_symbol.assert_called_once()
        mock_req_post.assert_called_once()

if __name__ == "__main__":
    unittest.main()
