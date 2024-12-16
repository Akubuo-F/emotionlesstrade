import math
from typing import Any
from features.sentiment.cot.core.models.market_traders import MarketTraders


class CommercialTraders(MarketTraders):
    """
    Base class for commercial traders.

    Commercial traders are traders that use the futures market to hedge their core buisness logic.
    """
    def __init__(
            self, 
            long: int, 
            long_change: int, short: int, short_change: int, 
            historical_net: list[int] | None,
            cot_index: int | None = None
        ):
        """
        :param long: Total number of contracts that have been bought by this category of traders and are still active
        in the market.
        :param long_change: Change in the long contracts from the previous week.
        :param short: Total number of contracts that have been sold by this category of traders and are still 
        active in the market.
        :param short_change: Change in the short contracts from the previous week.
        :param historical_net: The net positions of commercial traders over the last n weeks (typically 156 weeks for 
        three years).
        """
        super().__init__(long, long_change, short, short_change)
        self._historical_net = historical_net
        self._cot_index = cot_index
    
    @property
    def historical_net(self) -> list[int] | None:
        return self._historical_net

    @historical_net.setter
    def historical_net(self, historical_net: list[int]) -> None:
        """
        Set the historical net positions for this commercial traders.

        :param historical_net: The historical net positions of commercial traders.
        :type historical_net: list[int]
        :raises ValueError: If the length of historical net is lesser than 156.
        :raises ValueError: If the current net does not equal historical_net[0]. It assumes that current net wasn't
        included. If you are sure it included then first sort the historical net in decreasing order to avoid the error.
        """
        if len(historical_net) < 156: 
            raise ValueError("length of historical net can't be lesser than 156.")
        if self.do_net() != historical_net[0]:
            raise ValueError(f"""
                    Current net must also be include in historical net, if included, sort the historical net in 
                    descending order.
                """
            )
        self._historical_net = historical_net[: 156]

    def get_cot_index(self) -> int:
        """
        The Commitments of Traders (COT) Index is a percentage that ranges from 0 to 100%. it indicates the level of
        bullishness or bearishness of commercial traders in a particular market.
        """
        if self._historical_net is None:
            if self._cot_index:
                return self._cot_index
            return 0
        min_net = min(self._historical_net)
        max_net = max(self._historical_net)
        cot_index: float = (self.do_net() - min_net) / (max_net - min_net)
        cot_index = round(cot_index * 100, 1)
        return math.ceil(cot_index) if cot_index - int(cot_index) >= .5 else math.floor(cot_index)

    
    def to_dict(self, verbose: bool, enhanced: bool) -> dict[str, float]:
        result: dict[str, float] = super().to_dict(verbose, enhanced)
        if enhanced: result.update(cot_index=self.get_cot_index())
        return result