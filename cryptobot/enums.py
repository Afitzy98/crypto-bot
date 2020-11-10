from enum import Enum


class Position(str, Enum):
    NONE = "none"
    LONG = "long"
    SHORT = "short"
