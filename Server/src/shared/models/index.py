from typing import Final
from shared.models.asset import Asset
from shared.enums.reading import Reading
from shared.interfaces.tradable import Tradable


class Index(Asset, Tradable):
    """
    Base class for indecies.

    An index is an asset.
    """
    def __init__(self, code: str, name: str, cftc_code: str):
        super().__init__(code, name, cftc_code)

    def get_reading(self) -> Reading:
        raise NotImplementedError


class ReportedIndecies:
    """
    Holds pre-defined indecies.
    """
    dji: Final[Index] = Index(
        code="DJI", 
        name="Dow Jones Industrial Average", 
        cftc_code="124603"
        )
    ndx: Final[Index] = Index(
        code="NDX", 
        name="Nasdaq", 
        cftc_code="209742"
        )
    rty: Final[Index] = Index(
        code="RTY", 
        name="Russel", 
        cftc_code="239742"
        )
    spx: Final[Index] = Index(
        code="SPX", 
        name="S&P 500", 
        cftc_code="13874A"
        )
    tnx: Final[Index] = Index(
        code="TNX", 
        name="10-Year U.S. Treasury Notes", 
        cftc_code="043602"
        )
    all: Final[list[Index]] = [dji, ndx, rty, spx, tnx]
