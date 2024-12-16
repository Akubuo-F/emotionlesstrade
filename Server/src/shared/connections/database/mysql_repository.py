import asyncio  
import json  
from typing import Any, Coroutine, Final  
import aiomysql  
from features.sentiment.cot.core.interfaces.cot_repository import COTRepository  
from features.sentiment.cot.core.models.cot_report import COTReport  
from features.sentiment.cot.tools.cot_report_builder import COTReportBuilder  
import pymysql
from shared.interfaces.assets_repository import AssetRepository  
from shared.models.asset import Asset  
from shared.models.currency import ReportedCurrencies
from shared.models.reported_assets import ReportedAssets  
from shared.utils.logger import Logger  
from shared.utils.util import Util  


class MySQLRepository(AssetRepository, COTRepository):  
    """  
    Handles storing and fetching COT reports   
    """  
    _CREATE_ASSET_TABLE_QUERY: Final[str] = f"""  
        CREATE TABLE IF NOT EXISTS {AssetRepository._ASSETS_TABLE_NAME} (  
            code VARCHAR(255) PRIMARY KEY,  
            name VARCHAR(255) NOT NULL,  
            cftc_code VARCHAR(255) NOT NULL,
            UNIQUE (code, cftc_code)
        )  
    """    
    _CREATE_COT_REPORTS_TABLE_QUERY: Final[str] = f"""  
        CREATE TABLE IF NOT EXISTS {COTRepository._COT_REPORTS_TABLE_NAME} (  
            report_id INT AUTO_INCREMENT PRIMARY KEY,  
            asset_code VARCHAR(255),  
            report_date DATE,  
            report_data JSON,  
            FOREIGN KEY (asset_code) REFERENCES {AssetRepository._ASSETS_TABLE_NAME}(code),
            UNIQUE (asset_code, report_date)  
        )  
    """    

    def __init__(self):  
        """  
        Initializes the MySQLRepository with a database connection.

        Make sure to close the database connection when done with all operations by calling disconnect(). 
        """  
        super().__init__()  
        self._pool: aiomysql.Pool | None = None  

    async def _initialize_pool(self):  
        """  
        Initializes the connection pool to the MySQL database.  
        """  
        if self._pool is None:  
            try:  
                config: list[Any] = Util.get_env_variables(  
                    ["MYSQL_HOST", "MYSQL_PORT", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE"]  
                )  
                self._pool = await aiomysql.create_pool(  
                    host=config[0],  
                    port=int(config[1]),  
                    user=config[2],  
                    password=config[3],  
                    db=config[4],  
                    maxsize=100  
                )  
            except Exception as e:  
                Logger.log(  
                    name=self.__class__.__name__,  
                    level=Logger.CRITICAL,  
                    message=f"Failed to initialize database connection pool: {e}"  
                )  
                raise 
    async def _connect(self) -> aiomysql.Connection:  
        """  
        Establishes a connection to the MySQL database.  
        """  
        if self._pool is None:  
            await self._initialize_pool()  
        if self._pool is None:  
            raise RuntimeError("Connection pool is not initialized.")  
        return await self._pool.acquire()  
    
    async def _release(self, connection: aiomysql.Connection):  
        """  
        Releases the database connection back to the pool.  
        """  
        if self._pool:  
            self._pool.release(connection)  

    async def disconnect(self):  
        """  
        Closes the database connection pool.  
        """  
        if self._pool:  
            self._pool.close()  
            await self._pool.wait_closed()  

    async def build_assets_table(self, assets: list[Asset]) -> None:  
        connection: aiomysql.Connection = await self._connect()  
        try:  
            async with connection.cursor() as cursor:  
                await cursor.execute(self._CREATE_ASSET_TABLE_QUERY)  
                await connection.commit()  
                
            tasks: list[Coroutine] = [self._put_asset(asset) for asset in assets]  
            await asyncio.gather(*tasks)  
        except Exception as error:  
            Logger.log(  
                name=self.__class__.__name__,  
                level=Logger.CRITICAL,  
                message=f"Error while building assets table: Error Type: {type(error)}"  
            )  
            raise  
        finally:  
            await self._release(connection)  
    
    async def _put_asset(self, asset: Asset) -> None:  
        """  
        Puts a single asset into the database.  
        """  
        connection: aiomysql.Connection = await self._connect()  
        try:  
            async with connection.cursor() as cursor:  
                await cursor.execute(  
                    f"""  
                        INSERT INTO {self._ASSETS_TABLE_NAME} (code, name, cftc_code)  
                        VALUES (%s, %s, %s)  
                    """,  
                    (asset.code, asset.name, asset.cftc_code)  
                )  
                await connection.commit()  
        except aiomysql.IntegrityError:  
            message: str = f"Asset with code {asset.code} already exists. Skipping insertion of this asset."  
            Logger.log(  
                name=self.__class__.__name__,  
                level=Logger.WARNING,  
                message=message  
            )  
        except Exception as error:  
            Logger.log(  
                name=self.__class__.__name__,  
                level=Logger.ERROR,  
                message=f"Failed to insert asset {asset.code}: Error Type: {type(error)}"  
            )  
            raise  
        finally:  
            await self._release(connection)  

    async def build_cot_report_table(self, cot_reports: list[COTReport]) -> None:  
        connection: aiomysql.Connection = await self._connect()  
        try:  
            async with connection.cursor() as cursor:  
                await cursor.execute(self._CREATE_COT_REPORTS_TABLE_QUERY)  
                await connection.commit()  
            
            tasks: list[Coroutine] = [self._put_cot_report(report) for report in cot_reports]  
            await asyncio.gather(*tasks)  
        except Exception as error:  
            Logger.log(  
                name=self.__class__.__name__,  
                level=Logger.CRITICAL,  
                message=f"Failed to build COT report table: Error Type: {type(error)}"  
            )  
            raise  
        finally:  
            await self._release(connection)  

    async def _put_cot_report(self, report: COTReport) -> None:  
        connection: aiomysql.Connection = await self._connect()  
        retries = 3
        for attempt in range(retries):  
            try:  
                async with connection.cursor() as cursor:  
                    # Check if the report already exists  
                    await cursor.execute(  
                        f"""  
                            SELECT COUNT(*) FROM {COTRepository._COT_REPORTS_TABLE_NAME}  
                            WHERE asset_code = %s AND report_date = %s  
                        """,  
                        (report.asset_code, report.reported_date)  
                    )  
                    exists = await cursor.fetchone()  
                    if exists[0] > 0:  
                        Logger.log(  
                            name=self.__class__.__name__,  
                            level=Logger.INFO,  
                            message=f"COT report for asset {report.asset_code} on date {report.reported_date} already exists. Skipping insertion."  
                        )  
                        return  # Skip insertion if it already exists  

                    # Proceed to insert if it does not exist  
                    report_data = json.dumps(report.to_dict(verbose=True, enhanced=True))  
                    await cursor.execute(  
                        f"""  
                            INSERT INTO {COTRepository._COT_REPORTS_TABLE_NAME} (asset_code, report_date, report_data)  
                            VALUES (%s, %s, %s)  
                        """,  
                        (report.asset_code, report.reported_date, report_data)  
                    )  
                    await connection.commit()  
                break  # Exit loop if successful  
            except pymysql.err.OperationalError as e:  
                if e.args[0] == 1213:  # Deadlock error code  
                    Logger.log(  
                        name=self.__class__.__name__,  
                        level=Logger.WARNING,  
                        message=f"Deadlock detected. Retrying... (Attempt {attempt + 1}/{retries})"  
                    )  
                    await asyncio.sleep(1)  # Wait before retrying  
                    continue  # Retry the operation  
                else:  
                    Logger.log(  
                        name=self.__class__.__name__,  
                        level=Logger.ERROR,  
                        message=f"Failed to insert COT report for asset {report.asset_code}: Error Type: {e}"  
                    )  
                    raise  
            finally:  
                await self._release(connection)  

    async def insert_cot_reports(self, cot_reports: list[COTReport]) -> None:  
        connection: aiomysql.Connection = await self._connect() 
        try:
            cursor: aiomysql.Cursor
            async with connection.cursor() as cursor:
                for report in cot_reports:
                    await cursor.execute(
                        f"""
                            INSERT INTO {COTRepository._COT_REPORTS_TABLE_NAME} (asset_code, report_date, report_data)
                            VALUES (%s, %s, %s)
                        """,
                        (report.asset_code, report.reported_date, json.dumps(report.to_dict()))
                    )
                    await connection.commit()
        except Exception as error:
            Logger.log(  
                name=self.__class__.__name__,  
                level=Logger.ERROR,  
                message=f"Failed to insert COT reports: Error Type: {error}"  
            )  
            raise error
        finally:
            await self._release(connection) 

    async def fetch_cot_reports_by(
            self, asset_codes: list[str] | None = None, 
            released_dates: list[str] | None = None
        ) -> list[tuple]:
        results: list[tuple] = []  
        connection: aiomysql.Connection = await self._connect()
        try:
            cursor: aiomysql.Cursor
            async with connection.cursor() as cursor:
                if released_dates:
                    await cursor.execute(
                        f"""
                        SELECT * FROM {COTRepository._COT_REPORTS_TABLE_NAME} WHERE report_date = 
                        {" OR report_date = ".join(["%s"] * len(released_dates))}
                        """,
                        released_dates
                    )
                    results = await cursor.fetchall()
                if asset_codes:
                    results = list(filter(lambda record: record[1] in asset_codes, results))
            if len(results) == 0:
                raise LookupError("No report was found.")
            return results
        except Exception as error:
            raise error
        finally:
            await self._release(connection)

    async def insert_assets(self, assets: list[Asset]) -> None:  
        raise NotImplementedError  

    async def get_assets_by(self, codes: list[str] | None = None, names: list[str] | None = None, cftc_code: list[int] | None = None) -> list[tuple[Any]]:  
        raise NotImplementedError  


async def main():  
    repo: MySQLRepository = MySQLRepository()  
    
    async def build_assets():  
        start = time.time()  
        await repo.build_assets_table(ReportedAssets.all)  
        finish_time = time.time() - start  
        print(f"Finished building assets in: {finish_time}")  

    async def build_cot_reports():  
        start = time.time()  
        """ presenter = COTReportPresenter() 
        cot_reports: list[COTReport] = []  
        tasks = [  
            presenter.from_dataframe(  
                data=pd.read_csv(f"{Util.get_root_dir()}/data/cot/historical_reports/202{4-i}_cot_reports.txt"),  
                suppress_error=True  
            )   
            for i in range(4)  
        ]  
        for cot_report in await asyncio.gather(*tasks):  
            cot_reports.extend(cot_report) """
        cot_reports: list[COTReport] = await COTReportBuilder().build_from_files(
            [f"{Util.get_root_dir()}/data/202{4 - i}_cot_reports.txt" for i in range(4)]
        ) 
        await repo.build_cot_report_table(cot_reports)  
        finish_time = time.time() - start  
        print(f"Finished building reports in: {finish_time}")  
    
    async def fetch_cot_reports():
        start = time.time()
        asset_codes: list[str] = list(map(lambda asset: asset.code, [ReportedCurrencies.aud]))
        dates: list[str] = ["2024-11-12"]
        fetched_results: list[tuple] = await repo.fetch_cot_reports_by(asset_codes=asset_codes, released_dates=dates)
        finish_time = time.time() - start 
        print(fetched_results)
        print(f"Finished fetching reports in: {finish_time}")

    #await build_assets()  
    #await build_cot_reports()
    await fetch_cot_reports()
    await repo.disconnect()

if __name__ == "__main__":  
    import time  
    asyncio.run(main())
