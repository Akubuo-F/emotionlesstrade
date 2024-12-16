from typing import Final
from shared.models.asset import Asset
from shared.interfaces.cftc_reportable import COTReportable


class Currency(Asset, COTReportable):
    """
    Base class for currencies.

    A currency is an asset.
    """
    def __init__(self, code: str, name: str, cftc_code: str):
        super().__init__(code, name, cftc_code)


class ReportedCurrencies:
    """
    Holds pre-defined currencies.
    """
    aud: Final[Currency] = Currency(
        code="AUD", 
        name="Australian Dollar", 
        cftc_code="232741"
        )
    cad: Final[Currency] = Currency(
        code="CAD", 
        name="Canadian Dollar", 
        cftc_code="090741"
        )
    chf: Final[Currency] = Currency(
        code="CHF", 
        name="Swiss Franc", 
        cftc_code="092741"
        )
    eur: Final[Currency] = Currency(
        code="EUR", 
        name="Euro", 
        cftc_code="099741"
        )
    gbp: Final[Currency] = Currency(
        code="GBP", 
        name="British Pound", 
        cftc_code="096742"
        )
    mxn: Final[Currency] = Currency(
        code="MXN", 
        name="Mexican Peso", 
        cftc_code="095741"
        )
    nzd: Final[Currency] = Currency(
        code="NZD", 
        name="New Zealand Dollar", 
        cftc_code="112741"
        )
    jpy: Final[Currency] = Currency(
        code="JPY", 
        name="Japanese Yen", 
        cftc_code="097741"
        )
    usd: Final[Currency] = Currency(
        code="USD", 
        name="U.S. Dollar", 
        cftc_code="098662"
        )
    all: Final[list[Currency]] = [aud, cad, chf, eur, gbp, mxn, nzd, jpy, usd]
    