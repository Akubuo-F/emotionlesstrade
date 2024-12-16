from enum import Enum


class Reading(Enum):
    """
    Base class for readings

    A reading can be of any of these three: bullish, bearish, or neutral.
    """
    bullish = 1
    bearish = -1
    neutral = 0
