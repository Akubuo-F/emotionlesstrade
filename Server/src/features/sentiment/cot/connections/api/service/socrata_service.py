import asyncio
from typing import Any
from aiohttp import ClientResponseError
from features.sentiment.cot.core.interfaces.cot_repository import COTRepository
from features.sentiment.cot.connections.api.client.socrata_client import SocrataClient
from features.sentiment.cot.core.interfaces.cot_service import COTService
from features.sentiment.cot.core.models.cot_report import COTReport
from features.sentiment.cot.tools.cot_report_presenter import COTReportPresenter
from shared.connections.database.mysql_repository import MySQLRepository
from shared.models.asset import Asset
from shared.models.reported_assets import ReportedAssets
from shared.utils.logger import Logger
import urllib


class SocrataService(COTService):
    def __init__(self, cot_repository: COTRepository):
        self._client: SocrataClient = SocrataClient()
        self._cot_repository = cot_repository
        self._cot_report_presenter: COTReportPresenter = COTReportPresenter()

    async def fetch_latest_report(self, assets: list[Asset]) -> list[COTReport]:
        try:
            from_repository: list[tuple[Any]] = await self._cot_repository.fetch_cot_reports_by(
                asset_codes=list(map(lambda asset: asset.code, assets)),
                released_dates=[self.calculate_last_report_release_date()]
            )
            return self._cot_report_presenter.from_list(from_repository)
        except LookupError:
            Logger.log(
                SocrataClient.__name__, 
                level=Logger.INFO, 
                message="Local COT report is outdated, will try Fetching from Socrata API."
                )
        try:    
            assets_cftc_codes: list[str] = [f"'{asset.cftc_code}'" for asset in assets]
            query_dict: dict = {
                        "report_date_as_yyyy_mm_dd": f">= '{self.calculate_last_report_release_date()}T00:00:00.000'",
                        "cftc_contract_market_code": f"IN ({', '.join(assets_cftc_codes)})"
            }
            query: str = " AND ".join([f"{key} {value}" for key, value in query_dict.items()])
            params: dict[str, str] = {"$where": query}
            from_api: list[dict[str, Any]] = await self._client.fetch_latest_report(params=params)
            cot_reports: list[COTReport] = await self._cot_report_presenter.from_dicts(from_api)
            await self._cot_repository.insert_cot_reports(cot_reports)
            return cot_reports
        except Exception as error:
            Logger.log(
                self.__class__.__name__, 
                level=Logger.CRITICAL, 
                message=f"COT reports could not be fetched from either local repository or from Socrata API. Error: {error}"
                )
            raise
    
    async def fetch_historical_report(self, assets: list[Asset], start_date: int, n_weeks: int) -> list[COTReport]:
        raise NotImplementedError


async def main():
    service: SocrataService = SocrataService(cot_repository=MySQLRepository())
    latest_cot_reports: list[COTReport] = await service.fetch_latest_report(ReportedAssets.all)
    for report in latest_cot_reports:
        print(f"asset: {report.asset_code}")
        print(f"reported_dated: {report.reported_date}")

if __name__ == "__main__":
    asyncio.run(main())
