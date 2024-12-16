import math
from typing import Any


class MarketTraders:
    """
    Base class thar represents a group of market traders.

    Market traders are a group of traders traders who hold positions in a futures market.
    """

    def __init__(self, long: int, long_change: int, short: int, short_change: int):
        """
        :param long: Total number of contracts that have been bought by this category of traders and are still active
        in the market.
        :param long_change: Change in the long contracts from the previous week.
        :param short: Total number of contracts that have been sold by this category of traders and are still 
        active in the market.
        :param short_change: Change in the short contracts from the previous week.
        """
        self._long = int(long)
        self._long_change = int(long_change)
        self._short = int(short)
        self._short_change = int(short_change)

    def to_dict(self, verbose: bool, enhanced: bool) -> dict[str, float]:
        """
        Represents the trader group in a JSON serialisable format.

        :return dict[str, Any]:
        """
        result: dict[str, float] = {}
        if verbose: 
            result.update(
                long=self._long,
                long_change=self._long_change,
                short=self._short,
                short_change=self._short_change
            )
        if enhanced:
            result.update(
                net=self.do_net(),
                percentage_net=self.do_percentage_net()
                )
        return result

    def do_net(self) -> int:
        """
        :return int: Returns the net positon of this category of traders.
        """
        return self.long - self.short
    
    def do_percentage_net(self) -> float:
        """
        :return float: Returns the net position in percentage of this categorry of traders.
        """
        net_ratio = self.do_net() / (self._long + self._short)
        return round(net_ratio * 100, 1)

    @property
    def long(self) -> int:
        """
        :return int: Total number of contracts that have been bought by this category of traders and are still active
        in the market.
        """
        return self._long
    
    @property
    def long_change(self) -> int:
        """
        :return int: Change in the long contracts from the previous week.
        """
        return self._long_change
    
    @property
    def short(self) -> int:
        """
        :return int: Total number of contracts that have been sold by this category of traders and are still active
        in the market.
        """
        return self._short
    
    @property
    def short_change(self) -> int:
        """
        :return int: Change in the short contracts from the previous week.
        """
        return self._short_change
    
    def do_long_percentage(self) -> float:
        """
        :returns int: The long contracts percentage of this trader group.
        """
        total: int = self._long + self._short
        ratio: float = self._long/total
        percentage: float = ratio * 100
        return round(percentage, 1)
        #return math.ceil(percentage) if percentage - int(percentage) >= 0.5 else math.floor(percentage)
    
    def do_short_percentage(self) -> float:
        """
        :returns int: The short contracts percentage of this trader group.
        """
        total: int = self._long + self._short
        ratio: float = self._short/total
        percentage: float = ratio * 100
        return round(percentage, 2)
        #return math.ceil(percentage) if percentage - int(percentage) >= 0.5 else math.floor(percentage)
    