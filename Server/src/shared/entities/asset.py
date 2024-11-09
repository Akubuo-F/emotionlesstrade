from abc import ABC


class Asset(ABC):
    """
    Base class for an asset.

    An Asset is any tradable financial instrument.
    """
    def __init__(self):
        ...