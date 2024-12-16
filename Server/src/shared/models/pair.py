from abc import ABC

from shared.models.asset import Asset
from shared.enums.reading import Reading
from shared.interfaces.tradable import Tradable


class Pair(Tradable, ABC):
    """
    Base class for asset pairs.

    An pair represents the value of one asset (base asset) relative to another (quote asset).
    """
    def __init__(self, base: Asset, quote: Asset):
        """
        :param base: The base asset.
        :type base: Asset 
        :param quote: The quote asset.
        :type quote: Asset 
        :param name: The name of this pair.
        :type name: str 
        """
        self._code = f"{base.code}/{quote.code}"
        self._name = f"{base.name}/{quote.name}"
        self._base = base
        self._quote = quote

    @property
    def base(self) -> Asset:
        """
        :return Asset: The base asset.
        """
        return self._base
    
    @property
    def quote(self) -> Asset:
        """
        :return Asset: The quote asset.
        """
        return self._quote

    def get_reading(self) -> Reading:
        raise NotImplementedError
