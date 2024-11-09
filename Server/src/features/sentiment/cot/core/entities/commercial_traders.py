from features.sentiment.cot.core.entities.market_traders import MarketTraders


class CommercialTraders(MarketTraders):
    """
    Base class for commercial traders.

    Commercial traders are traders that use the futures market to hedge their core buisness logic.
    """
    def get_cot_index(self, historical_net: list[int]) -> float:
        """
        The Commitments of Traders (COT) Index is a percentage that ranges from 0 to 100%. it indicates the level of
        bullishness or bearishness of commercial traders in a particular market.

        :param historical_net: The net positions of commercial traders over the last n weeks (typically 156 weeks for 
        three years).
        """
        min_net = min(historical_net)
        max_net = max(historical_net)
        cot_index = (self.do_net() - min_net) / (max_net - min_net)
        return round(cot_index * 100, 1)