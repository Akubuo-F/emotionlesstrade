import asyncio
from concurrent.futures import ThreadPoolExecutor
import datetime
import json
from typing import Any
import pandas as pd
from features.sentiment.cot.core.models.commercial_traders import CommercialTraders
from features.sentiment.cot.core.models.cot_report import COTReport
from features.sentiment.cot.core.models.noncommercial_traders import NonCommercialTraders
from shared.models.reported_assets import ReportedAssets
from shared.utils.util import Util


class COTReportPresenter():
    """
    COT report presenter handles converting data formats that represents a COT report from and to a COTReport
    """
    _REQUIRED_DATAFRAME_COLUMNS: pd.Index = pd.Index([
        "CFTC Contract Market Code",
        "As of Date in Form YYYY-MM-DD",
        "Open Interest (All)",
        "Noncommercial Positions-Long (All)",
        "Noncommercial Positions-Short (All)",
        "Commercial Positions-Long (All)",
        "Commercial Positions-Short (All)",
        "Change in Open Interest (All)",
        "Change in Noncommercial-Long (All)",
        "Change in Noncommercial-Short (All)",
        "Change in Commercial-Long (All)",
        "Change in Commercial-Short (All)"
    ])

    @classmethod
    def from_list(cls, data: list[tuple]) -> list[COTReport]:
        """
        Converts the given data into a list of COT reports.
        
        :param data: A list of tuples that represents COT reports.
        :type data: list[tuple]
        :returns list[COTReport]:
        """
        cot_reports: list[COTReport] = []
        for record in data:
            asset_code: str = record[1]
            reported_date: str = record[2]
            report_data: dict[str, Any] = json.loads(record[3])
            commercials: CommercialTraders = CommercialTraders(
                long=report_data["commercials"]["long"],
                long_change=report_data["commercials"]["long_change"],
                short=report_data["commercials"]["short"],
                short_change=report_data["commercials"]["short_change"],
                historical_net=None,
                cot_index=report_data["commercials"]["cot_index"]
            )
            noncommercials: NonCommercialTraders = NonCommercialTraders(
                long=report_data["noncommercials"]["long"],
                long_change=report_data["noncommercials"]["long_change"],
                short=report_data["noncommercials"]["short"],
                short_change=report_data["noncommercials"]["short_change"],
            )
            report: COTReport = COTReport(
                reported_date=reported_date,
                asset_code=asset_code,
                commercials=commercials,
                noncommercials=noncommercials,
                open_interest=report_data["open_interest"],
                open_interest_change=report_data["open_interest_change"]
            )
            cot_reports.append(report)
        return cot_reports
    
    @staticmethod
    async def from_dicts(data: list[dict[str, Any]]) -> list[COTReport]:
        """
        Converts the given list of data into a list of COT reports.
        
        :param data: A dict of str that represents COT reports.
        :type data: list[dict[str, Any]]
        """
        cot_reports: list[COTReport] = []
        for record in data:
            reported_date: str = record["report_date_as_yyyy_mm_dd"].split("T")[0]
            asset_code: str = ""
            for asset in ReportedAssets.all:
                if asset.cftc_code == record["cftc_contract_market_code"]:
                    asset_code = asset.code
                    break
            commercials: CommercialTraders = CommercialTraders(
                long=record["comm_positions_long_all"],
                long_change=record["change_in_comm_long_all"],
                short=record["comm_positions_short_all"],
                short_change=record["change_in_comm_short_all"],
                historical_net=None,
            )
            commercial_historical_net: list[int] = []
            cache_file: str = f"{Util.get_root_dir()}/data/cot/cache.json"
            cache_data: dict[str, Any] = dict()
            with open(cache_file, "r") as cache:
                cache_data = json.load(cache)
                commercial_historical_net = json.loads(cache_data["recent_commercial_historical_nets"][asset_code])[: -1]
                commercial_historical_net.insert(0, commercials.do_net())
                cache_data["recent_commercial_historical_nets"][asset_code] = json.dumps(commercial_historical_net)
            with open(cache_file, "w") as cache:
                json.dump(cache_data, cache)
            commercials.historical_net = commercial_historical_net
            noncommercials: NonCommercialTraders = NonCommercialTraders(
                long=record["noncomm_positions_long_all"],
                long_change=record["change_in_noncomm_long_all"],
                short=record["noncomm_positions_short_all"],
                short_change=record["change_in_noncomm_short_all"],
            )
            report = COTReport(
                reported_date=reported_date,
                asset_code=asset_code,
                commercials=commercials,
                noncommercials=noncommercials,
                open_interest=record["open_interest_all"],
                open_interest_change=record["change_in_open_interest_all"]
            )
            cot_reports.append(report)
        return cot_reports
    
    @staticmethod
    async def to_dataframe(cot_reports: list[COTReport]) -> pd.DataFrame:
        """
        Converts the given COT reports to a data frame.
        
        :param cot_reports: A list of COT reports.
        :type cot_reports: list[COTReport]
        """
        raise NotImplementedError
    
    @classmethod
    async def from_dataframe(cls, data: pd.DataFrame, suppress_error: bool = False) -> list[COTReport]:
        """
        Converts the given data into a list of COT reports.

        :param data: A data frame that represents COT reports.
        :type data: DataFrame:
        :param suppress_error: Handles the thrown error when a market and exchange name of an asset in the data isn't 
        among the reported assets.
        :type suppress_error: bool
        """
        cls._verify_required_columns_exists(data)
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            tasks = [
                loop.run_in_executor(executor, cls._build_from_dataframe_row, row, suppress_error) 
                for _, row in data.iterrows()
                ]
            results: list[COTReport | None] = await asyncio.gather(*tasks)
            return [result for result in results if result is not None]
    
    @classmethod
    def _build_from_dataframe_row(cls, row: pd.Series, suppress_error: bool = False) -> COTReport | None:
        """
        Builds a COT report from a single data frame row.
        :param row: A data frame row.
        :type row: Series
        :param suppress_error: Catches the thrown error when the CFTC code of an asset in the data doesn't belong to 
        any asset in the reported assets. Note: This will return None.
        :type suppress_error: bool
        :returns: A COT report.
        """
        columns: list[str] = cls._REQUIRED_DATAFRAME_COLUMNS.to_list()
        asset_code: str = ""
        cftc_code: str = str(row[columns[0]])
        for asset in ReportedAssets.all:
            if asset.cftc_code == cftc_code:
                asset_code = asset.code
                break
        if asset_code == "":
            if suppress_error:
                return None
            raise ValueError(f"The CFTC contract code: {cftc_code} does not belong to any asset in the reported assets")
        
        reported_date: str = str(row[columns[1]])
        commercial_traders: CommercialTraders = CommercialTraders(
            long=int(row[columns[5]]),
            long_change=int(row[columns[-2]]),
            short=int(row[columns[6]]),
            short_change=int(row[columns[-1]]),
            historical_net=None
        )
        noncommercial_traders: NonCommercialTraders = NonCommercialTraders(
            long=int(row[columns[7]]),
            long_change=int(row[columns[-4]]),
            short=int(row[columns[8]]),
            short_change=int(row[columns[-3]])
        )
        open_interest: int = int(row[columns[2]])
        open_interest_change: int = int(row[columns[-5]])
        return COTReport(
            reported_date=reported_date,
            asset_code=asset_code,
            commercials=commercial_traders,
            noncommercials=noncommercial_traders,
            open_interest=open_interest,
            open_interest_change=open_interest_change
        )
    
    @classmethod
    def _verify_required_columns_exists(cls, data: pd.DataFrame) -> None:
        """
        Verifies if the required data frame columns are present in the given COT reports data frame.
        
        :param data: A data frame representing COT reports.
        :type data: DataFrame
        :raises ValueError: If a required column is not found in the given data's column.
        """
        difference: pd.Index[str] = cls._REQUIRED_DATAFRAME_COLUMNS.difference(data.columns)
        if difference.size > 0: raise ValueError(f"Columns {difference.tolist()} not found in the given data.") 


if __name__ == "__main__":
    import time
    presenter = COTReportPresenter()
    async def main():
        start = time.time()
        cot_reports: list[COTReport] = []
        tasks = [
                    presenter.from_dataframe(
                        data=pd.read_csv(f"{Util.get_root_dir()}/202{4-i}_cot_reports.txt"),
                        suppress_error=True
                    ) 
                    for i in range(4)
                ]
        for cot_report in await asyncio.gather(*tasks):
            cot_reports.extend(cot_report)
        finish_time = time.time() - start
        for report in cot_reports:
            print(f"reported_date = {report.reported_date}")
            print(f"asset_code = {report.asset_code}")
            print(f"open_interest = {report.open_interest}")
            print(f"open_interest_change = {report.open_interest_change}")
            print()
        print(f"Finished Processing in: {finish_time}")
    
    fetched = [(9, 'AUD', datetime.date(2024, 11, 5), '{"asset_code": "AUD", "commercials": {"net": -31759, "long": 59108, "short": 90867, "cot_index": 11, "long_change": 1301, "short_change": -4798, "percentage_net": -21.2}, "open_interest": 177416, "reported_date": "2024-11-05", "noncommercials": {"net": -4372, "long": -6561, "short": -2189, "sentiment": "neutral", "long_change": -2189, "short_change": -5649, "percentage_net": 50.0}, "open_interest_change": -6561}'), (202, 'CAD', datetime.date(2024, 11, 5), '{"asset_code": "CAD", "commercials": {"net": 180918, "long": 272938, "short": 92020, "cot_index": 91, "long_change": 6627, "short_change": -25, "percentage_net": 49.6}, "open_interest": 336467, "reported_date": "2024-11-05", "noncommercials": {"net": 7105, "long": 6522, "short": -583, "sentiment": "bullish", "long_change": -583, "short_change": 7147, "percentage_net": 119.6}, "open_interest_change": 6522}'), (403, 'CHF', datetime.date(2024, 11, 5), '{"asset_code": "CHF", "commercials": {"net": 39519, "long": 58057, "short": 18538, "cot_index": 64, "long_change": -2885, "short_change": -728, "percentage_net": 51.6}, "open_interest": 75911, "reported_date": "2024-11-05", "noncommercials": {"net": -4077, "long": -3062, "short": 1015, "sentiment": "bullish", "long_change": 1015, "short_change": -3002, "percentage_net": 199.2}, "open_interest_change": -3062}'), (583, 'EUR', datetime.date(2024, 11, 5), '{"asset_code": "EUR", "commercials": {"net": 617, "long": 381704, "short": 381087, "cot_index": 89, "long_change": -19967, "short_change": 10864, "percentage_net": 0.1}, "open_interest": 645597, "reported_date": "2024-11-05", "noncommercials": {"net": -16665, "long": -16078, "short": 587, "sentiment": "bullish", "long_change": 587, "short_change": -28064, "percentage_net": 107.6}, "open_interest_change": -16078}'), (805, 'GBP', datetime.date(2024, 11, 5), '{"asset_code": "GBP", "commercials": {"net": -55560, "long": 56459, "short": 112019, "cot_index": 39, "long_change": 7863, "short_change": -10878, "percentage_net": -33.0}, "open_interest": 219857, "reported_date": "2024-11-05", "noncommercials": {"net": 10221, "long": -1678, "short": -11899, "sentiment": "bearish", "long_change": -11899, "short_change": 9373, "percentage_net": -75.3}, "open_interest_change": -1678}'), (1006, 'MXN', datetime.date(2024, 11, 5), '{"asset_code": "MXN", "commercials": {"net": -27000, "long": 69905, "short": 96905, "cot_index": 56, "long_change": 1659, "short_change": -2916, "percentage_net": -16.2}, "open_interest": 143741, "reported_date": "2024-11-05", "noncommercials": {"net": 1827, "long": -3799, "short": -5626, "sentiment": "neutral", "long_change": -5626, "short_change": -1676, "percentage_net": -19.4}, "open_interest_change": -3799}'), (1207, 'NZD', datetime.date(2024, 11, 5), '{"asset_code": "NZD", "commercials": {"net": 9620, "long": 34368, "short": 24748, "cot_index": 73, "long_change": 6518, "short_change": 505, "percentage_net": 16.3}, "open_interest": 59800, "reported_date": "2024-11-05", "noncommercials": {"net": 6002, "long": 1780, "short": -4222, "sentiment": "bearish", "long_change": -4222, "short_change": 1810, "percentage_net": -245.8}, "open_interest_change": 1780}'), (1408, 'JPY', datetime.date(2024, 11, 5), '{"asset_code": "JPY", "commercials": {"net": 47295, "long": 135946, "short": 88651, "cot_index": 46, "long_change": 14810, "short_change": -4403, "percentage_net": 21.1}, "open_interest": 235762, "reported_date": "2024-11-05", "noncommercials": {"net": 14459, "long": 9868, "short": -4591, "sentiment": "bullish", "long_change": -4591, "short_change": 14759, "percentage_net": 274.0}, "open_interest_change": 9868}'), (1609, 'USD', datetime.date(2024, 11, 5), '{"asset_code": "USD", "commercials": {"net": -46, "long": 6004, "short": 6050, "cot_index": 94, "long_change": -122, "short_change": -1405, "percentage_net": -0.4}, "open_interest": 30825, "reported_date": "2024-11-05", "noncommercials": {"net": -218, "long": -1711, "short": -1493, "sentiment": "neutral", "long_change": -1493, "short_change": 96, "percentage_net": 6.8}, "open_interest_change": -1711}'), (1810, 'BTC', datetime.date(2024, 11, 5), '{"asset_code": "BTC", "commercials": {"net": 927, "long": 1907, "short": 980, "cot_index": 87, "long_change": -112, "short_change": 203, "percentage_net": 32.1}, "open_interest": 32011, "reported_date": "2024-11-05", "noncommercials": {"net": 77, "long": -1776, "short": -1853, "sentiment": "neutral", "long_change": -1853, "short_change": -2265, "percentage_net": -2.1}, "open_interest_change": -1776}'), (2011, 'DJI', datetime.date(2024, 11, 5), '{"asset_code": "DJI", "commercials": {"net": -17117, "long": 43814, "short": 60931, "cot_index": 13, "long_change": -4166, "short_change": 49, "percentage_net": -16.3}, "open_interest": 86343, "reported_date": "2024-11-05", "noncommercials": {"net": -4708, "long": -3631, "short": 1077, "sentiment": "bullish", "long_change": 1077, "short_change": -2229, "percentage_net": 184.3}, "open_interest_change": -3631}'), (2212, 'NDX', datetime.date(2024, 11, 5), '{"asset_code": "NDX", "commercials": {"net": -27658, "long": 144580, "short": 172238, "cot_index": 22, "long_change": -8336, "short_change": 3084, "percentage_net": -8.7}, "open_interest": 252753, "reported_date": "2024-11-05", "noncommercials": {"net": -9522, "long": -4629, "short": 4893, "sentiment": "bearish", "long_change": 4893, "short_change": -6077, "percentage_net": -3606.8}, "open_interest_change": -4629}'), (2413, 'RTY', datetime.date(2024, 11, 5), '{"asset_code": "RTY", "commercials": {"net": -23537, "long": 324134, "short": 347671, "cot_index": 10, "long_change": 10558, "short_change": 6956, "percentage_net": -3.5}, "open_interest": 448893, "reported_date": "2024-11-05", "noncommercials": {"net": 9003, "long": 10832, "short": 1829, "sentiment": "bullish", "long_change": 1829, "short_change": 4980, "percentage_net": 71.1}, "open_interest_change": 10832}'), (2614, 'SPX', datetime.date(2024, 11, 5), '{"asset_code": "SPX", "commercials": {"net": -233202, "long": 1448167, "short": 1681369, "cot_index": 8, "long_change": -28284, "short_change": 27310, "percentage_net": -7.5}, "open_interest": 2140451, "reported_date": "2024-11-05", "noncommercials": {"net": -35878, "long": -27912, "short": 7966, "sentiment": "bullish", "long_change": 7966, "short_change": -42776, "percentage_net": 179.9}, "open_interest_change": -27912}'), (2815, 'TNX', datetime.date(2024, 11, 5), '{"asset_code": "TNX", "commercials": {"net": 707726, "long": 3519123, "short": 2811397, "cot_index": 65, "long_change": -64329, "short_change": 18355, "percentage_net": 11.2}, "open_interest": 4566389, "reported_date": "2024-11-05", "noncommercials": {"net": -58652, "long": -36325, "short": 22327, "sentiment": "bullish", "long_change": 22327, "short_change": -60586, "percentage_net": 419.0}, "open_interest_change": -36325}'), (3016, 'WTI', datetime.date(2024, 11, 5), '{"asset_code": "WTI", "commercials": {"net": -211226, "long": 706922, "short": 918148, "cot_index": 85, "long_change": -32798, "short_change": 2741, "percentage_net": -13.0}, "open_interest": 1746717, "reported_date": "2024-11-05", "noncommercials": {"net": -33937, "long": -5019, "short": 28918, "sentiment": "bearish", "long_change": 28918, "short_change": -15293, "percentage_net": -142.0}, "open_interest_change": -5019}'), (3217, 'XAG', datetime.date(2024, 11, 5), '{"asset_code": "XAG", "commercials": {"net": -74243, "long": 30347, "short": 104590, "cot_index": 12, "long_change": 123, "short_change": -7846, "percentage_net": -55.0}, "open_interest": 151126, "reported_date": "2024-11-05", "noncommercials": {"net": 475, "long": -5194, "short": -5669, "sentiment": "neutral", "long_change": -5669, "short_change": 1416, "percentage_net": -4.4}, "open_interest_change": -5194}'), (3418, 'XAU', datetime.date(2024, 11, 5), '{"asset_code": "XAU", "commercials": {"net": -283059, "long": 73287, "short": 356346, "cot_index": 20, "long_change": 4352, "short_change": -16260, "percentage_net": -65.9}, "open_interest": 558034, "reported_date": "2024-11-05", "noncommercials": {"net": 8386, "long": -21434, "short": -29820, "sentiment": "neutral", "long_change": -29820, "short_change": -6496, "percentage_net": -16.4}, "open_interest_change": -21434}'), (3619, 'XCU', datetime.date(2024, 11, 5), '{"asset_code": "XCU", "commercials": {"net": -34211, "long": 82982, "short": 117193, "cot_index": 41, "long_change": -2308, "short_change": -2336, "percentage_net": -17.1}, "open_interest": 251994, "reported_date": "2024-11-05", "noncommercials": {"net": -868, "long": 4284, "short": 5152, "sentiment": "neutral", "long_change": 5152, "short_change": 5221, "percentage_net": -9.2}, "open_interest_change": 4284}'), (3820, 'XPD', datetime.date(2024, 11, 5), '{"asset_code": "XPD", "commercials": {"net": 2591, "long": 8128, "short": 5537, "cot_index": 23, "long_change": 235, "short_change": -720, "percentage_net": 19.0}, "open_interest": 18297, "reported_date": "2024-11-05", "noncommercials": {"net": 667, "long": 487, "short": -180, "sentiment": "bullish", "long_change": -180, "short_change": 1034, "percentage_net": 217.3}, "open_interest_change": 487}'), (4021, 'XPT', datetime.date(2024, 11, 5), '{"asset_code": "XPT", "commercials": {"net": -35774, "long": 14515, "short": 50289, "cot_index": 13, "long_change": 1189, "short_change": -4488, "percentage_net": -55.2}, "open_interest": 85562, "reported_date": "2024-11-05", "noncommercials": {"net": 938, "long": -782, "short": -1720, "sentiment": "neutral", "long_change": -1720, "short_change": 4782, "percentage_net": -37.5}, "open_interest_change": -782}')]
    start = time.time()
    cot_reports: list[COTReport] = presenter.from_list(fetched)
    finish_time = time.time() - start
    for report in cot_reports:
        print(f"asset: {report.asset_code}")
        print(f"reported_dated: {report.reported_date}")
    print(f"Finished Processing in: {finish_time}")

    #asyncio.run(main())