from abc import ABC, abstractmethod
from typing import Any, Final

from shared.models.asset import Asset


class AssetRepository(ABC):
    """
    Interface for asset repositories.

    AssetRepositories handles storing and fetching assets.
    """
    _ASSETS_TABLE_NAME: Final[str] = "assets"

    
    @abstractmethod
    async def build_assets_table(self, assets: list[Asset]) -> None:
        """
        Builds the asset table in the database.
        
        :param assets: A list of assets.
        :type assets: list[Asset]
        """
        raise NotImplementedError("How do i build the assets table in the database?")
    
    @abstractmethod
    async def insert_assets(self, assets: list[Asset]) -> None:
        """
        Inserts the new assets into the existing assets table.
 
        :param assets: A list of assets.
        :type assets: lists[Asset] 
        """
        raise NotImplementedError("How do i append assets into the assets table?")
    
    @abstractmethod
    async def get_assets_by(
            self, 
            codes: list[str] | None = None, 
            names: list[str] | None = None,
            cftc_code: list[int] | None = None
            ) -> list[tuple[Any]]:
        """
        Fetches the requested assets either by asset codes, asset names or asset COT repor names.

        :param codes: The asset codes that are the unique identifier of the requested assets in the database.
        :type codes: list[str]
        :param names: The names of the requested assets in the database
        :type names: list[str]
        :param cot_report_names: The CFTC code of the requested assets in the database.
        :type cot_report_names: list[int]
        :raises LookUpError: If no asset was found.
        """
        raise NotImplementedError("How do i get assets from the assets table?")
