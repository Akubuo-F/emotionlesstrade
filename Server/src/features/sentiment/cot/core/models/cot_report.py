from abc import ABC
from typing import Any

from features.sentiment.cot.core.models.commercial_traders import CommercialTraders
from features.sentiment.cot.core.models.noncommercial_traders import NonCommercialTraders
from shared.models.reported_assets import ReportedAssets


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
        asset_code: str,
        commercials: CommercialTraders,
        noncommercials: NonCommercialTraders,
        open_interest: int,
        open_interest_change: int
        ):
        """
        Initialises the base class for COT report.

        :param reported_date: The date which traders last reported their positions to the CFTC.
        :param asset_code: The code of the asset that this COT report identifies.
        :param commercials: Traders that use the futures market primarily to hedge their core business activites.
        :param noncommercials: Traders that use the futures market for speculative purposes.
        :param open_interest: The total number of outstanding contracts that are held by market participants at the end
        of each day.
        :param open_interest_change: The total change in open interest from the previous week.
        """
        self._reported_date = str(reported_date)
        self._asset_code = str(asset_code)
        self._commercials = commercials
        self._noncommercial = noncommercials
        self._open_interest = int(open_interest)
        self._open_interest_change = int(open_interest_change)

    def to_dict(self, verbose: bool = True, enhanced: bool = True) -> dict[str, Any]:
        """
        Represents the COT report in a JSON serialisable format.

        :param verbose: Shows more details like the open interest, and the long and short positions of traders.
        :param enhanced: More informed output like the net posititioning of non-commercial traders and the COT Index of
        commercial traders.
        :return dict[str, Any]:
        """
        result: dict[str, Any] = {
            "reported_date": self._reported_date,
            "asset_code": self._asset_code,
            "open_interest": self._open_interest,
            "commercials": self._commercials.to_dict(verbose=verbose, enhanced=enhanced),
            "noncommercials": self._noncommercial.to_dict(verbose=verbose, enhanced=enhanced),
        }
        if verbose:
            result.update(open_interest_change=self._open_interest_change)
        return result
    
    def describe(self, verbose: bool, enhanced: bool) -> str:
        """
        Describes the COT report.

        :param verbose: Shows more details like the changes in open interest, and the long and short positions of traders
        :type verbose: bool 
        :param enhanced: More informed output like the net positioning of non-commercial traders and the COT Index of 
        commercial traders.
        :type enhanced: bool 
        """
        asset_name: str = ""
        for asset in ReportedAssets.all:
            if self._asset_code == asset.code:
                asset_name = asset.name
                break
        description: list[str] = [
            f"COT REPORT OF {asset_name} REPORTED ON {self._reported_date}",
            f"{f"COT INDEX: {self._commercials.get_cot_index()}" if enhanced else ""}",
            f"{f"CHANGE IN OPEN INTEREST: {self._open_interest_change}" if enhanced else ""}",
            f"{f"OPEN INTEREST: {self._open_interest}" if verbose else ""}",
            f"{f"SENTIMENT OF TREND FOLLOWERS: {self._noncommercial.get_sentiment().name.upper()}" if enhanced else ""}",
            f"{f"NONCOMMERCIAL NET PERCENTAGE: {self._noncommercial.do_percentage_net()}%, LONG PERCENTAGE = {self._noncommercial.do_long_percentage()}%, SHORT PERCENTAGE = {self._noncommercial.do_short_percentage()}%" if enhanced else ""}",
            f"{f"NONCOMMERCIAL CHANGES: LONG = {self._noncommercial.long_change}, SHORT = {self._noncommercial.short_change}" if enhanced else ""}",
            f"{f"COMMERCIAL POSITIONS: LONG = {self._commercials.long}, SHORT = {self._commercials.short}" if verbose else ""}",
            f"{f"NONCOMMERCIAL POSITIONS: LONG = {self._noncommercial.long}, SHORT = {self._noncommercial.short}" if verbose else ""}"
        ]
        description = [text for text in description if text != ""]
        return "\n".join(description)

    @property
    def reported_date(self) -> str:
        """
        :return str: The date which traders last reported their positions to the CFTC.
        """
        return self._reported_date
    
    @property
    def asset_code(self) -> str:
        """
        :return str: The code of the asset that this COT report identifies.
        """
        return self._asset_code
    
    
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
    
    