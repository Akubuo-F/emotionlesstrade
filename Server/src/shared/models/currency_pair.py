from shared.models.currency import Currency
from shared.models.pair import Pair
from shared.enums.reading import Reading


class CurrencyPair(Pair):
    """
    Base class for currency pairs.

    A currency pair is a pair where both its base asset and quote asset are currencies.
    """
    def __init__(self, base: Currency, quote: Currency, name: str):
        super().__init__(base, quote)
    
    @property
    def base(self) -> Currency:
        return self.base
    
    @property
    def quote(self) -> Currency:
        return self.quote

    def get_reading(self) -> Reading:
        raise NotImplementedError

