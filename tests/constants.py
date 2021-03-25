import json

from cryptobot.enums import JobType
from cryptobot.model import EquityRecord
from cryptobot.utils import get_previous_ts_dt


class MockJob:
    def __init__(self, name, id):
        self.name = name
        self.id = id


JOBS = [
    MockJob(name=JobType.TRADE_MANAGER, id=1),
    MockJob(name=JobType.ANALYTICS_MANAGER, id=2),
]
NO_JOBS = []


assets = json.dumps([{"asset": "BTC", "hedge": 0.1}, {"asset": "ETH", "hedge": 0.1}, {"asset": "DOT", "hedge": 0.1}, {"asset": "ADA", "hedge": 0.1}, {"asset": "XRP", "hedge": 0.1}, {"asset": "USDT", "hedge": 0.5}])

ts = get_previous_ts_dt()

EQUITY_RECORD = EquityRecord(equity=100.0, assets=assets, time=ts)

EQUITY_HISTORY = [EQUITY_RECORD for i in range(20)]
