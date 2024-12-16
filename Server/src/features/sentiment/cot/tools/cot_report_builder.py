import asyncio
import json
from typing import Any
from features.sentiment.cot.core.models.cot_report import COTReport
from features.sentiment.cot.tools.cot_report_presenter import COTReportPresenter
import pandas as pd
from shared.models.reported_assets import ReportedAssets
from shared.utils.logger import Logger
from shared.utils.util import Util


class COTReportBuilder:
    """
    Builds cot reports from text or csv files.
    """

    def __init__(self):
        self._cot_report_presenter: COTReportPresenter = COTReportPresenter()

    async def build_from_files(self, cot_report_files: list[str]) -> list[COTReport]:
        """
        Builds COT reports from the given files.
          
        :param cot_report_files: The files to build the COT reports from.
        :type cot_report_files: list[str]
        :returns list[COTReport]: A list of cot reports.
        """
        cot_reports: list[COTReport] = []
        for file in cot_report_files:
            if not (file.endswith(".txt") or file.endswith(".txt")):
                raise ValueError("Report should be a txt file or csv file")
            data: pd.DataFrame = pd.read_csv(file)
            cot_reports.extend(await self._cot_report_presenter.from_dataframe(data, suppress_error=True))
        return self.updated_multiple_cot_index(cot_reports)
    
    def cache_historical_nets(self, cot_reports: list[COTReport]) -> None:
        """
        Caches the commercial historical net positions of a COTReport. This should be the latest report for each asset
        in the reported assets.
        
        :param cot_reports: The latest COT reports of each asset in the reported assets.
        :type cot_reports: list[COTReport]
        :raises ValueError: If an assets report in the reported assets is missing in the set of COT reports.
        :raises ValueError: If the reported dates of the COT reports in the list of COT reports are different.
        """
        reported_assets_codes: set[str] = set(map(lambda asset: asset.code, ReportedAssets.all))
        asset_codes_in_the_report: set[str] = set(map(lambda report: report.asset_code, cot_reports))
        for code in reported_assets_codes:
            if code not in asset_codes_in_the_report:
                raise ValueError("The latest COT report of the asset: {code} is missing in the list of COT reports.")
        if len(set(map(lambda report: report.reported_date, cot_reports))) != 1:
            raise ValueError("The reported dates of the COT reports in the list of COT reports are different.")
        cache_file: str = f"{Util.get_root_dir()}/data/cot/cache.json"
        data: dict[str, Any] = {}
        with open(cache_file, "r") as cache:
            try:
                data = json.load(cache)
            except json.JSONDecodeError as error:
                Logger.log(
                    name=self.__class__.__name__,
                    level=Logger.ERROR,
                    message=f"Couldn't load {cache_file} because: {error}. Overriding {cache_file} instead."
                )    
            for report in cot_reports:
                jsonified_commercial_historical_nets: str = json.dumps(report.commercials.historical_net)
                data["recent_commercial_historical_nets"][report.asset_code] = jsonified_commercial_historical_nets
        with open(cache_file, "w") as cache:
            json.dump(data, cache)
    
    def updated_multiple_cot_index(self, cot_reports: list[COTReport]) -> list[COTReport]:
        """
        Groups each cot_report to their various assets, updates their COT Index and caches the latest reports historical
        net positions of their commercial traders locally (in a json cache file).

        :param cot_reports: A list COT reports of different assets.
        :type cot_reports:  
        """
        updated_reports: list[COTReport] = []
        latest_reports: list[COTReport] = []
        for asset in ReportedAssets.all:
            asset_historical_report: list[COTReport] = list(
                filter(
                    lambda report: report.asset_code == asset.code, cot_reports
                    )
                )
            updated_group: list[COTReport] = self.update_cot_index_group(asset_historical_report)
            updated_reports.extend(updated_group)
            latest_reports.append(updated_group[0])
        try:
            self.cache_historical_nets(latest_reports)
        except ValueError as error:
            Logger.log(
                name=self.__class__.__name__,
                level=Logger.ERROR,
                message=f"""
                    Failed to cache the historical reports because: {error}
                """
            )
            raise
        return updated_reports

    
    def update_cot_index_group(self, cot_reports: list[COTReport]) -> list[COTReport]:
        """
        Updates the COT Index of each reports in the group if there exists 155 historical reports after the current 
        report.

        Example:
        cot_reports: list[COTReport] = [COTReport(), COTReport(), COTReport(), ..., COTReport(), COTReport()]

        len(cot_reports) = 157

        Then only the COT Index of cot_reports in cot_reports[: 1] will be updated. 
         
        :param cot_reports: A list of COT reports of an asset
        :type cot_reports: list[COTReport]
        """
        cot_reports = sorted(cot_reports, key=lambda cot_report: cot_report.reported_date, reverse=True)
        report_group: str = cot_reports[0].asset_code
        n_weeks: int = 156
        for i in range(len(cot_reports)):
            latest_report: COTReport = cot_reports[i]
            if latest_report.asset_code != report_group:
                raise TypeError(
                    f"""
                    This report released on {latest_report.reported_date} does not belong to this 
                    group: {report_group}. It should belong in {latest_report.asset_code} group.
                    """
                )
            historical_net: list[int] = list(
                map(
                    lambda cot_report: cot_report.commercials.do_net(), 
                    cot_reports[i: i + n_weeks]
                    )
                )
            try:
                latest_report.commercials.historical_net = historical_net
            except ValueError as error:
                Logger.log(
                    name=self.__class__.__name__,
                    level=Logger.ERROR,
                    message=f"""
                        Can't update the COT index of this group: {report_group} starting from report: 
                        {cot_reports[i].reported_date}, due to error: {error}
                    """
                )
                break
        return cot_reports
    

async def main():
        cot_report_files: list[str] = []
        for i in range(4):
            cot_report_files.append(f"{Util.get_root_dir()}/data/cot/historical_reports/202{i + 1}_cot_reports.txt")
        report_builder: COTReportBuilder = COTReportBuilder()
        start = time.time()
        cot_reports: list[COTReport] = await report_builder.build_from_files(cot_report_files)
        finished = time.time() - start

        _print_reports(cot_reports)

        print(f"Finished processing in: {finished}")
    
def _print_reports(cot_reports: list[COTReport]):
    for cot_report in cot_reports:
        if cot_report.reported_date not in ("2024-11-05", "2024-10-29", "2024-10-22", "2024-10-15"):
            continue
        print(f"asset: {cot_report.asset_code}")
        print(f"reported_date: {cot_report.reported_date}")
        print(f"is historical net empty: {cot_report.commercials.historical_net == None}")
        print(f"cot_index: {cot_report.commercials.get_cot_index()}")
        print()

if __name__ == "__main__":
    import time
    asyncio.run(main())