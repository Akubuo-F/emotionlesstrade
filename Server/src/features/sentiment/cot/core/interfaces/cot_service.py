from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from features.sentiment.cot.core.models.cot_report import COTReport
from shared.models.asset import Asset


class COTService(ABC):
    """
    Base class for any Commitment of Traders (COT) service.

    A COT service handles tasks like fetching the COT reports from external sources.
    """

    @abstractmethod
    async def fetch_latest_report(self, assets: list[Asset]) -> list[COTReport]:
        """
        Fetches the latest COT report.

        :param assets: A list of assets.
        :type assets: list[Asset]
        :return list[COTReport]: A list of COT reports of the given assets.
        """
        raise NotImplementedError
    
    @abstractmethod
    async def fetch_historical_report(self, assets: list[Asset], start_date: int, n_weeks: int) -> list[COTReport]:
        """
        Fetches the historical report of the assets specified, from the start date going back to the specified number of
        weeks.
        
        :param assets: A list of assets.
        :type assets: list[Asset] 
        :param start_date: The starting date of the historical report.
        :type start_date: int 
        :param n_weeks: The number of past weekly reports to fetch.
        :type n_weeks: int
        :returns list[COTReport]: A list of COT reports (historical) of the given assets.
        """
        raise NotImplementedError
    
    @staticmethod
    def calculate_last_report_release_date() -> str:
        """
        :returns str: returns the last report released date.
        """
        current_date: datetime = datetime.now()
        current_weekday: int = current_date.date().weekday()
        friday_as_weekday: int = 4
        days_passed_since_recent_friday: int = current_weekday % friday_as_weekday
        if days_passed_since_recent_friday == friday_as_weekday and current_date.strftime("%H:%M") > "15:30": 
            days_passed_since_recent_friday = 7 - 1 # Should be 7 but datetime starts counting from 0.
        recent_friday_date: datetime = current_date - timedelta(days=days_passed_since_recent_friday)
        recent_cot_report_date: datetime = recent_friday_date - timedelta(days=3)
        return recent_cot_report_date.strftime("%Y-%m-%d")
    

if __name__ == "__main__":
    print(COTService.calculate_last_report_release_date())