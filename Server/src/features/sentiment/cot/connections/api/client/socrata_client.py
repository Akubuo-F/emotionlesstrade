import asyncio
from typing import Any
import aiohttp
from shared.utils.util import Util


class SocrataClient:
    """
    Socrata client communicates with the socrata api through HTTPS requests.
    """
    def __init__(self):
        self._app_token: str = Util.get_env_variables(["SOCRATA_APP_TOKEN"])[0]
        self.base_url: str = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"
    
    async def fetch_latest_report(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        """
        :returns list[dict[str, Any]]: returns the response containing the latest report from the socrata api.
        :raises aiohttp.ClientResponseError:
        """
        headers: dict[str, Any] = {
            "X-App-Token": self._app_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, headers=headers, params=params) as response:
                if response.status != 200:
                    response.raise_for_status()
                return await response.json()
    
async def main():
    client = SocrataClient()
    try:
        query: str = " ".join(
            [
                "report_date_as_yyyy_mm_dd >= '2024-11-05T00:00:00.000'",
                "AND market_and_exchange_names = 'AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE'"
            ]
        )
        params = { "$where": query }
        latest_report = await client.fetch_latest_report(params=params)
        print(latest_report)
    except Exception as e:
        print(f"An error occured: {e}")

if __name__ == "__main__":
    asyncio.run(main())