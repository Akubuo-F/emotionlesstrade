from typing import Any, Final

from shared.models.asset import Asset
from shared.models.commodity import Commodity, ReportedCommodities
from shared.models.cryptocurrency import CryptoCurrency, ReportedCryptoCurrencies
from shared.models.currency import Currency, ReportedCurrencies
from shared.models.index import Index, ReportedIndecies


class ReportedAssets:
    """
    Holds pre-defined assets.
    """
    all: Final[list[Asset | Any]] = ReportedCurrencies.all \
        + ReportedCryptoCurrencies.all \
        + ReportedIndecies.all \
        + ReportedCommodities.all