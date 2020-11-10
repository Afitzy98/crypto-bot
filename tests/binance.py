import unittest
from unittest import mock

from cryptobot.binance import (
    get_data,
    get_info_for_symbol,
    get_order_qty,
    handle_decision,
    handle_exit_positions,
    handle_long,
    handle_order,
    handle_short,
)

from cryptobot import app

TICKER = {"askPrice": 10, "bidPrice": 9}
SYMBOL_INFO = {
    "filters": [
        {"filterType": "OTHER"},
        {"filterType": "LOT_SIZE", "stepSize": "0.001", "minQty": "0.01"},
    ]
}
EMPTY_SYMBOL_FILTERS = {"filters": []}
EXPECTED_COLUMNS = ["Open", "High", "Low", "Close"]
LONG_ACCOUNT = {
    "userAssets": [{"asset": "SYM", "free": "0"}, {"asset": "USDT", "free": "100"}]
}
SHORT_ACCOUNT = {
    "userAssets": [
        {"asset": "SYM", "free": "0", "borrowed": "0", "free": "0.1"},
        {"asset": "USDT", "free": "100"},
    ]
}
EXIT_POS_ACCOUNT = {
    "userAssets": [
        {
            "asset": "SYM",
            "free": "0",
            "borrowed": "10",
            "interest": "0.1",
            "free": "10",
        },
        {"asset": "USDT", "free": "100"},
    ]
}
NO_PREV_POS = {
    "shortPos": False,
    "longPos": False,
}


@mock.patch("requests.post", autospec=True)
class TestData(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

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

    @mock.patch("binance.client.Client.get_margin_account", return_value=LONG_ACCOUNT)
    @mock.patch("binance.client.Client.get_orderbook_ticker", return_value=TICKER)
    @mock.patch("binance.client.Client.get_symbol_info", return_value=SYMBOL_INFO)
    @mock.patch("binance.client.Client.create_test_order", autospec=True)
    def test_handle_decision_long(
        self,
        mock_test_order,
        mock_get_symbol_info,
        mock_orderbook_ticker,
        mock_get_account,
        mock_req_post,
    ):
        with app.app_context():
            handle_decision(True, False, "SYM")
            mock_test_order.assert_called_once()
            mock_get_symbol_info.assert_called_once()
            mock_orderbook_ticker.assert_called_once()
            mock_get_account.assert_called_once()
            mock_req_post.assert_called_once()

    @mock.patch("binance.client.Client.get_margin_account", return_value=SHORT_ACCOUNT)
    @mock.patch("binance.client.Client.get_orderbook_ticker", return_value=TICKER)
    @mock.patch("binance.client.Client.get_symbol_info", return_value=SYMBOL_INFO)
    @mock.patch("binance.client.Client.create_test_order", autospec=True)
    def test_handle_decision_short(
        self,
        mock_test_order,
        mock_get_symbol_info,
        mock_orderbook_ticker,
        mock_get_account,
        mock_req_post,
    ):
        with app.app_context():
            handle_decision(False, True, "SYM")
            mock_test_order.assert_called_once()
            mock_get_symbol_info.assert_called()
            mock_get_account.assert_called_once()
            mock_orderbook_ticker.assert_called_once()
            mock_req_post.assert_called_once()

    @mock.patch(
        "binance.client.Client.get_margin_account", return_value=EXIT_POS_ACCOUNT
    )
    @mock.patch("binance.client.Client.get_symbol_info", return_value=SYMBOL_INFO)
    @mock.patch("binance.client.Client.create_test_order", autospec=True)
    def test_handle_decision_no_signal(
        self,
        mock_test_order,
        mock_get_symbol_info,
        mock_get_account,
        mock_req_post,
    ):
        with app.app_context():
            handle_decision(False, False, "SYM")
            mock_test_order.assert_called_once()
            mock_get_symbol_info.assert_called_once()
            mock_get_account.assert_called_once()
            mock_req_post.assert_called_once()

    @mock.patch("binance.client.Client.create_test_order", side_effect=Exception)
    def test_handle_order_failing(self, mock_test_order, mock_req_post):
        handle_order("", "", "", 1, 1, True)
        mock_req_post.assert_called_once()
        mock_test_order.assert_called_once()

    @mock.patch("binance.client.Client.create_margin_order", autospec=True)
    def test_real_order(self, mock_real_order, mock_req_post):
        handle_order("", "", "", 1, 1, False)
        mock_req_post.assert_called_once()
        mock_real_order.assert_called_once()

    @mock.patch("binance.client.Client.get_symbol_info", return_value=SYMBOL_INFO)
    @mock.patch(
        "binance.client.Client.get_margin_account", return_value=EXIT_POS_ACCOUNT
    )
    @mock.patch("binance.client.Client.create_test_order", autospec=True)
    def test_handle_exit_positions(
        self, mock_test_order, mock_get_account, mock_get_symbol, mock_req_post
    ):
        handle_exit_positions(
            "SYM",
            {"shortPos": True, "longPos": True},
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
    @mock.patch(
        "binance.client.Client.get_margin_account", return_value=EXIT_POS_ACCOUNT
    )
    def test_handle_long_doing_nothing(
        self, mock_get_account, mock_test_order, mock_get_symbol, mock_req_post
    ):
        handle_long(
            "",
            {"shortPos": False, "longPos": True},
        )
        mock_get_account.assert_not_called()
        mock_get_symbol.assert_not_called()
        mock_req_post.assert_not_called()
        mock_test_order.assert_not_called()

    @mock.patch("binance.client.Client.get_symbol_info", return_value=SYMBOL_INFO)
    @mock.patch("binance.client.Client.create_test_order", autospec=True)
    @mock.patch(
        "binance.client.Client.get_margin_account", return_value=EXIT_POS_ACCOUNT
    )
    def test_handle_short_from_long(
        self, mock_get_account, mock_test_order, mock_get_symbol, mock_req_post
    ):
        handle_short(
            "SYM",
            {"shortPos": False, "longPos": True},
        )
        mock_get_account.assert_called_once()
        mock_get_symbol.assert_called()
        mock_req_post.assert_called_once()
        mock_test_order.assert_called_once()

    @mock.patch("binance.client.Client.get_symbol_info", return_value=SYMBOL_INFO)
    @mock.patch("binance.client.Client.create_test_order", autospec=True)
    def test_handle_short_doing_nothing(
        self, mock_test_order, mock_get_symbol, mock_req_post
    ):
        handle_short(
            "",
            {"shortPos": True, "longPos": False},
        )
        mock_get_symbol.assert_not_called()
        mock_req_post.assert_not_called()
        mock_test_order.assert_not_called()

    @mock.patch("binance.client.Client.get_margin_account", side_effect=Exception)
    def test_get_symbol_info_failing(self, mock_get_margin_account, mock_req_post):
        get_info_for_symbol("")
        mock_get_margin_account.assert_called_once()
        mock_req_post.assert_called_once()

    @mock.patch(
        "binance.client.Client.get_symbol_info", return_value=EMPTY_SYMBOL_FILTERS
    )
    def test_get_order_qty_no_filter(self, mock_get_symbol, mock_req_post):
        get_order_qty("", 1)
        mock_get_symbol.assert_called_once()
        mock_req_post.assert_not_called()


if __name__ == "__main__":
    unittest.main()