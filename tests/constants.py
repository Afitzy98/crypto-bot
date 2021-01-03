from cryptobot.enums import JobType


class MockJob:
    def __init__(self, name, id):
        self.name = name
        self.id = id


JOBS = [MockJob(name=JobType.TRADE_MANAGER, id=1)]
NO_JOBS = []
