import asyncio
from features.sentiment.cot.connections.api.service.socrata_service import SocrataService
from features.sentiment.cot.core.interfaces.cot_repository import COTRepository
from features.sentiment.cot.core.interfaces.cot_service import COTService
from features.sentiment.cot.core.models.cot_report import COTReport
from shared.connections.database.mysql_repository import MySQLRepository
from shared.models.asset import Asset
from shared.models.reported_assets import ReportedAssets


class ViewEnhancedLatestCOTReportsEvent:
    """
    View the enhanced version of the latest released COT report with more informed data such as the COT Indes, net positions, and
    the all-time highs and lows of each market participant.
    """

    def __init__(self, cot_service: COTService):
        self._cot_service = cot_service

    async def execute(self, assets: list[Asset]) -> None:
        latest_reports: list[COTReport] = await self._cot_service.fetch_latest_report(assets)
        for report in latest_reports:
            report_description: str = report.describe(verbose=False, enhanced=True)
            print(report_description, end="\n"*2)

async def main():
    cot_repository: COTRepository = MySQLRepository()
    cot_service: COTService = SocrataService(cot_repository=cot_repository)
    event: ViewEnhancedLatestCOTReportsEvent = ViewEnhancedLatestCOTReportsEvent(cot_service=cot_service)
    await event.execute(ReportedAssets.all)

if __name__ == "__main__":
    asyncio.run(main())