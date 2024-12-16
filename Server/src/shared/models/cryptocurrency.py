from typing import Final
from shared.models.currency import Currency


class CryptoCurrency(Currency):
    """
    Base class for cryptocurrencies.

    A cryptocurrency is a digital or virtual currency.
    """
    def __init__(self, code: str, name: str, cftc_code: str):
        super().__init__(code, name, cftc_code)


class ReportedCryptoCurrencies:
    """
    Holds pre-defined crypto-currencies.
    """
    btc: Final[CryptoCurrency] = CryptoCurrency(
        code="BTC", 
        name="Bitcoin", 
        cftc_code="133741"
        )
    all: Final[list[CryptoCurrency]] = [btc]