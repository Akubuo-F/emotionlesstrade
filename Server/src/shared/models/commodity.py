from typing import Final
from shared.models.asset import Asset


class Commodity(Asset):
    """
    Base class for commodities.

    A commodity is an asset.
    """
    def __init__(self, code: str, name: str, ctfc_code: str):
        super().__init__(code, name, ctfc_code)


class ReportedCommodities:
    wti: Final[Commodity] = Commodity(
        code="WTI",
        name="U.S. Oil",
        ctfc_code="067651"
    )
    xag: Final[Commodity] = Commodity(
        code="XAG",
        name="Silver",
        ctfc_code="084691"
    )
    xau: Final[Commodity] = Commodity(
        code="XAU",
        name="Gold",
        ctfc_code="088691"
    )
    xcu: Final[Commodity] = Commodity(
        code="XCU",
        name="Copper",
        ctfc_code="085692"
    )
    xpd: Final[Commodity] = Commodity(
        code="XPD",
        name="Palladium",
        ctfc_code="075651"
    )
    xpt: Final[Commodity] = Commodity(
        code="XPT",
        name="Platinum",
        ctfc_code="076651"
    )
    all: Final[list[Commodity]] = [wti, xag, xau, xcu, xpd, xpt]