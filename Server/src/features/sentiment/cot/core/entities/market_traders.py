from features.sentiment.cot.constants import Thresholds
from shared.entities.reading import Reading


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
        self._long = long
        self._long_change = long_change
        self._short = short
        self._short_change = short_change

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
    