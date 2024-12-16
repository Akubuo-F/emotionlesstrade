from abc import ABC, abstractmethod

from shared.enums.reading import Reading


class Tradable(ABC):
    """
    Base class for any tradable asset.

    A tradable asset is an asset that can be bought or sold by retail traders.
    """

    @abstractmethod
    def get_reading(self) -> Reading:
        """
        :return Reading: The reading of this tradable asset.
        """
        raise NotImplementedError
    