from abc import ABC

from features.sentiment.cot.core.entities.commercial_traders import CommercialTraders
from features.sentiment.cot.core.entities.noncommercial_traders import NonCommercialTraders


class COTReport(ABC):
    """
    Base class that represents the COT Report.

    The COT (Commitments of Traders) report is a weekly publication released by regulatory agencies, such as the 
    Commodity Futures Trading Commission (CFTC) in the United States. It provides valuable insights into the positions
    held by different market participants in futures markets, including currency futures. the report categorises traders
    into three main groups: commercial traders (hedgers), non-commercial traders (large speculators), and non-reportable 
    traders (small speculators)
    """

    def __init__(
        self,
        reported_date: str,
        commercials: CommercialTraders,
        noncommercials: NonCommercialTraders,
        open_interest: int,
        open_interest_change: int
        ):
        """
        Initialises the base class for COT report.

        :param reported_date: The date which traders last reported their positions to the CFTC.
        :param commercials: Traders that use the futures market primarily to hedge their core business activites.
        :param noncommercials: Traders that use the futures market for speculative purposes.
        :param open_interest: The total number of outstanding contracts that are held by market participants at the end
        of each day.
        :param open_interest_change: The total change in open interest from the previous week.
        """
        self._reported_date = reported_date
        self._commercials = commercials
        self._noncommercial = noncommercials
        self._open_interest = open_interest
        self._open_interest_change = open_interest_change

    @property
    def reported_date(self) -> str:
        """
        :return str: The date which traders last reported their positions to the CFTC.
        """
        return self._reported_date
    
    @property
    def commercials(self) -> CommercialTraders:
        """
        :return CommercialTraders: Traders that use the futures market primarily to hedge their core business activites.
        """
        return self._commercials
    
    @property
    def noncommercials(self) -> NonCommercialTraders:
        """
        :return NonCommercialTraders: Traders that use the futures market for speculative purposes.
        """
        return self._noncommercial
    
    @property
    def open_interest(self) -> int:
        """
        :return int: The total number of outstanding contracts that are held by market participants at the end
        of each day.
        """
        return self._open_interest
    
    @property
    def open_interest_change(self) -> int:
        """
        :return int: The total change in open interest from the previous week.
        """
        return self._open_interest_change
    
    