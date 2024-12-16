from abc import ABC, abstractmethod

class COTReportable(ABC):
    """
    Interface for any asset reported in the Commitments of Traders (COT) report.
    """

    @property
    @abstractmethod
    def cftc_code(self) -> str:
        """
        :return str: The CFTC contract code of this asset as it is reported by the Commodity Features Trading
        Commision (CFTC).
        """
        raise NotImplementedError