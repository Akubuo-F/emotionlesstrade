from features.sentiment.cot.constants import Thresholds
from features.sentiment.cot.core.entities.market_traders import MarketTraders
from shared.entities.reading import Reading


class NonCommercialTraders(MarketTraders):
    """
    Base class for non-commercial traders.

    NonCommercial traders are traders that use the futures market for speculative purposes.
    """
    def get_sentiment(self) -> Reading:
        """
        :return Reading: Returns the sentiment reading of non-commercial traders.
        """
        percentage_net = self.do_percentage_net()
        if percentage_net >= Thresholds.sentiment:
            return Reading.bullish
        elif percentage_net <= -Thresholds.sentiment:
            return Reading.bearish
        return Reading.neutral