from shared.models.cryptocurrency import CryptoCurrency
from shared.models.currency import Currency
from shared.models.currency_pair import CurrencyPair


class CryptoCurrencyPair(CurrencyPair):
    """
    Base class for cryptocurrency pairs.

    A cryptocurrency pair is a currency pair where is base asset is a cryptocurrency and its quote asset is a currency.
    """
    def __init__(self, base: CryptoCurrency, quote: Currency, name: str):
        super().__init__(base, quote, name)

    @property
    def base(self) -> CryptoCurrency:
        return self.base