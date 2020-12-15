from enum import Enum


class Position(str, Enum):
    NONE = "none"
    LONG = "long"
    SHORT = "short"

class JobType(str, Enum):
    TRADE_MANAGER = "TradeManager",
    PORTFOLIO_MANAGER = "PortfolioManager"