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


assets = json.dumps([{"asset": "a", "hedge": 0.5}, {"asset": "b", "hedge": 0.5}])

ts = get_previous_ts_dt()

EQUITY_RECORD = EquityRecord(equity=100.0, assets=assets, time=ts)
