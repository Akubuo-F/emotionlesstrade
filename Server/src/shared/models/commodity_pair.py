from shared.models.commodity import Commodity
from shared.models.currency import Currency
from shared.models.pair import Pair
from shared.enums.reading import Reading


class CommodityPair(Pair):
    """
    Base class for commodity pairs.

    A commodity pair is a pair where its base asset is a commodity and its quote asset is a currency.
    """
    def __init__(self, base: Commodity, quote: Currency, name: str):
        super().__init__(base, quote)
    
    @property
    def base(self) -> Commodity:
        return self.base
    
    @property
    def quote(self) -> Currency:
        return self.quote

    def get_reading(self) -> Reading:
        raise NotImplementedError

    