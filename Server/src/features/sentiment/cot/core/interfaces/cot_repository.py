from abc import ABC, abstractmethod
from typing import Any, Final

from features.sentiment.cot.core.models.cot_report import COTReport


class COTRepository(ABC):
    """
    Base class for COT reports repositories.
    """
    _COT_REPORTS_TABLE_NAME: Final[str] = "cot_reports"

    @abstractmethod
    async def build_cot_report_table(self, cot_reports: list[COTReport]) -> None:
        """
        Builds a COT report table of various assets in the database.

        :param cot_reports: A list of COT reports over the last 3 years (156 weeks).
        :type cot_report_table: list[COTReport]
        :raises ValueError: If an assets code in the database is not found in the COT report. This is to ensure 
        that all assets' COT report is updated an non left behind.
        :raises ValueError: If the COT report is less than exactly 3 years (156 weeks) worth of report for each 
        asset.
        """
        raise NotImplementedError("How do i build cot report table in the database?")
    
    @abstractmethod
    async def insert_cot_reports(self, cot_reports: list[COTReport]) -> None:
        """
        Inserts the given COT reports into the existing COT report table.

        :param cot_report_table: A list of COT repports.
        :type cot_report_table: list[COTReport]
        :raises ValueError: If an assets code in the database is not found in the COT reports. This is to ensure 
        that all assets' COT report is updated an non left behind.
        :raises ValueError: If the COT reports length is more or less than the assets in the database.
        """
        raise NotImplementedError("How do i append cot reports into the cot report table?")
    
    @abstractmethod
    async def fetch_cot_reports_by(
        self, 
        asset_codes: list[str] | None = None, 
        released_dates: list[str] | None = None,
        ) -> list[tuple]:
        """
        Fetches COT reports from the COT report table. Fetching can be done using asset codes or the report's released
        dates or both. 
        Fetching by released date will be prioritised first as the fetched reports will be more specific and speed up 
        computation time than fetching by asset code as this is more generic and fetch all COT report. You can use this
        approach to narrow down the fetched result.

        :param asset_codes: The asset codes that are the unique identifier of the requested assets in the database.
        :type asset_codes: list[str]
        :param released_dates: The released date of the COT reports.
        :type released_dates: list[str]
        :returns list[tupe]: The fetched results from the database.
        :raises LookUpError: If no COT report was found.
        """
        raise NotImplementedError("How do i fetch cot reports from the cot report table?")
    