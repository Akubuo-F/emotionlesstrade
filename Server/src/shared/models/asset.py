from abc import ABC
from shared.interfaces.cftc_reportable import COTReportable


class Asset(COTReportable, ABC):
    """
    Base class for an asset.

    An asset is a financial instrument.
    """
    def __init__(self, code: str, name: str, ctfc_code: str):
        """
        :param code: The code of the asset, e.g. BTC for Bitcoin, USD for U.S. Dollar.
        :type code: str 
        :param name: The name of the asset.
        :type name: str 
        :param ctfc_code: The CTFC contract code of this asset as it is reported by the Commodity Features 
        Trading Commision (CFTC).
        :type ctfc_code: int 
        """
        self._code = code.upper()
        self._name = " ".join(
            map(
                lambda sub_name: sub_name.capitalize() if "." not in sub_name else sub_name.upper(),
                name.split()
                )
            )
        self._ctfc_code = ctfc_code

    @property
    def code(self) -> str:
        """
        :return str: The code of the asset, e.g. BTC for Bitcoin, USD for U.S. Dollar.
        """
        return self._code
    
    @property
    def name(self) -> str:
        """
        :return str: The name of the asset.
        """
        return self._name

    @property
    def cftc_code(self) -> str:
        return self._ctfc_code
