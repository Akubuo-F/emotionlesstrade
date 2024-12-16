import asyncio
from features.sentiment.cot.connections.api.service.socrata_service import SocrataService
from features.sentiment.cot.core.interfaces.cot_repository import COTRepository
from features.sentiment.cot.core.interfaces.cot_service import COTService
from features.sentiment.cot.core.models.cot_report import COTReport
from shared.connections.database.mysql_repository import MySQLRepository
from shared.models.asset import Asset
from shared.models.reported_assets import ReportedAssets


class ViewDefaultLatestCOTReportsEvent:
    """
    View the default version of the latest COT report which contains the data about the open interest, position of 
    commercial and non commercial traders and changes from the previous week report.
    """

    def __init__(self, cot_service: COTService) -> None:
        self._cot_service = cot_service

    async def execute(self, assets: list[Asset]) -> None:
        latest_reports: list[COTReport] = await self._cot_service.fetch_latest_report(assets)
        for report in latest_reports:
            report_description: str = report.describe(verbose=True, enhanced=False)
            print(report_description, end="\n"*2)


async def main():
    cot_repository: COTRepository = MySQLRepository()
    cot_service: COTService = SocrataService(cot_repository=cot_repository)
    event: ViewDefaultLatestCOTReportsEvent = ViewDefaultLatestCOTReportsEvent(cot_service=cot_service)
    await event.execute(ReportedAssets.all)

if __name__ == "__main__":
    asyncio.run(main())
