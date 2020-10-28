import unittest
from unittest import mock

from cryptobot.binance import get_data, handle_decision, handle_exit_positions, handle_sell_order, handle_buy_order, get_info_for_symbol, handle_short, handle_long

from cryptobot import app

BTC_TICKER = {
    'askPrice': 11020,
    'bidPrice': 11000
}
EXPECTED_COLUMNS = ["Open", "High", "Low", "Close"]
LONG_ACCOUNT = {
    'userAssets':[
        {
            "asset": "BTC",
            "free": "0"
        },
        {
            "asset": "USDT",
            "free": "100"
        }
    ]
}
SHORT_ACCOUNT = {
    'userAssets':[
        {
            "asset": "BTC",
            "free": "0",
            "borrowed": "0",
            "free":"0.1"
        },
        {
            "asset": "USDT",
            "free": "100"
        }
    ]
}
EXIT_POS_ACCOUNT = {
    'userAssets':[
        {
            "asset": "BTC",
            "free": "0",
            "borrowed": "0.1",
            "interest": "0.0001",
            "free":"0.1"
        },
        {
            "asset": "USDT",
            "free": "100"
        }
    ]
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

    @mock.patch("binance.client.Client.get_historical_klines", return_value=[[0,0,0,0,0]])
    def test_get_data_working(self, mock_get_klines, mock_req_post):
        res = get_data("period", "SYM")
        mock_get_klines.assert_called_once()
        mock_req_post.assert_not_called()
        self.assertEqual(res["Open"].iloc[0], 0)
        self.assertEqual(res["High"].iloc[0], 0)
        self.assertEqual(res["Low"].iloc[0], 0)
        self.assertEqual(res["Close"].iloc[0], 0)

    @mock.patch("binance.client.Client.get_margin_account", return_value=LONG_ACCOUNT)
    @mock.patch("binance.client.Client.get_orderbook_ticker", return_value=BTC_TICKER)
    @mock.patch("binance.client.Client.create_test_order", return_value={})
    def test_long(self, mock_create_order, mock_get_ticker, mock_get_account, mock_req_post):
        res = handle_decision("long", "BTC")
        mock_get_account.assert_called_once()
        mock_get_ticker.assert_called_once()
        mock_create_order.assert_called_once()
        mock_req_post.assert_called_once()
        self.assertEqual({}, res)

    @mock.patch("binance.client.Client.get_margin_account", return_value=SHORT_ACCOUNT)
    @mock.patch("binance.client.Client.get_orderbook_ticker", return_value=BTC_TICKER)
    @mock.patch("binance.client.Client.create_test_order", return_value={})
    def test_short(self, mock_create_order, mock_get_ticker, mock_get_account, mock_req_post):
        res = handle_decision("short", "BTC")
        mock_get_account.assert_called()
        mock_get_ticker.assert_called_once()
        mock_create_order.assert_called_once()
        mock_req_post.assert_called_once()
        self.assertEqual({}, res)

    @mock.patch("binance.client.Client.get_margin_account", return_value=EXIT_POS_ACCOUNT)
    @mock.patch("binance.client.Client.create_test_order", return_value={})
    def test_exit_positions(self, mock_create_order, mock_get_account, mock_req_post):
        handle_decision("none", "BTC")
        mock_get_account.assert_called()
        mock_create_order.assert_called()
        mock_req_post.assert_called()

    
    @mock.patch("binance.client.Client.create_test_order", return_value={})
    def test_handle_exit_position(self, mock_create_order, mock_req_post):
        handle_exit_positions("BTC", {
            "coin": {"borrowed": "0", "free":"0"}
        })
        mock_create_order.assert_not_called()
        mock_req_post.assert_not_called()

    @mock.patch("binance.client.Client.create_margin_order", side_effect=Exception)
    def test_buy_order_failing(self, mock_create_order, mock_req_post):
        handle_buy_order("BTC", 0.1, False)
        mock_req_post.assert_called_once()
        mock_create_order.assert_called_once()


    @mock.patch("binance.client.Client.create_margin_order", side_effect=Exception)
    def test_sell_order_failing(self, mock_create_order, mock_req_post):
        handle_sell_order("BTC", 0.1, False, "MARGIN_BUY")
        mock_create_order.assert_called_once()
        mock_req_post.assert_called_once()

    @mock.patch("binance.client.Client.create_margin_order", return_value={}) 
    def test_real_sell_order(self, mock_create_order, mock_req_post):
        res = handle_sell_order("BTC", 0.1, False, "MARGIN_BUY")
        mock_req_post.assert_called_once()
        mock_create_order.assert_called_once()
        self.assertEqual({}, res)

    @mock.patch("binance.client.Client.create_margin_order",return_value={})
    def test_real_buy_order(self, mock_create_order, mock_req_post):
        res = handle_buy_order("BTC", 0.1, False)
        mock_req_post.assert_called_once()
        mock_create_order.assert_called_once()
        self.assertEqual({}, res)

    @mock.patch("binance.client.Client.get_margin_account", side_effect=Exception)
    def test_get_info_for_symbol_faliing(self, mock_get_account, mock_req_post):
        get_info_for_symbol("BTC")
        mock_get_account.assert_called_once()
        mock_req_post.assert_called_once()

    @mock.patch("binance.client.Client.get_orderbook_ticker", return_value=BTC_TICKER)
    @mock.patch("binance.client.Client.create_test_order", return_value={})
    def test_handle_short_whith_coin_in_account(self, mock_create_order, mock_ticker, mock_req_post):
        handle_short("BTC", {"coin":{"borrowed":"0", "free":"0.1"}, "usdt":{"free":"0"}})
        mock_req_post.assert_called_once()
        mock_ticker.assert_called_once()
        mock_create_order.assert_called_once()


    def test_handle_short_while_shorting(self, mock_req_post):
        handle_short("BTC", {"coin":{"borrowed":"0.1"}})
        mock_req_post.assert_not_called()

    def test_handle_long_while_longing(self, mock_req_post):
        handle_long("BTC", {"usdt":{"free":"0"}})
        mock_req_post.assert_not_called()

if __name__ == '__main__':
    unittest.main()