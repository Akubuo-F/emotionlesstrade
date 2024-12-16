import logging
import os
from typing import Final

from shared.utils.util import Util


class Logger:
    """
    Utility class for logging to help with debugging and monitoring the application's behaviour.
    """
    _LOG_DIR: Final[str] = f"{Util.get_root_dir()}/logs"
    _LOG_FORMAT: Final[str] = "From: %(name)s, time: %(asctime)s, level: %(levelname)s, message: %(message)s"
    INFO: Final[int] = logging.INFO
    WARNING: Final[int] = logging.WARNING
    ERROR: Final[int] = logging.ERROR
    CRITICAL: Final[int] = logging.CRITICAL

    @classmethod
    def configure(cls) -> None:
        """
        Configures the loggin setting.
        """
        if not os.path.exists(cls._LOG_DIR): os.makedirs(cls._LOG_DIR)
        logging.basicConfig(
            level=logging.INFO,
            format=cls._LOG_FORMAT,
            handlers=[
                logging.FileHandler(f"{cls._LOG_DIR}/logs.log"),
                logging.StreamHandler()
            ]
        )

    @classmethod
    def log(cls, name: str, level: int, message: str, to_file: bool = True, to_console: bool = True) -> None:
        """
        Logs a message.
        
        :param name: The name of the object trying to log a message.
        :type name: str
        :param level: Loggin level: INFO, WARNING, ERROR, CRITICAL.
        :type level: int 
        :param message: The log message.
        :type message: str 
        :param to_file: Specify whether to log the message to the file.
        :type to_file: bool
        :param to_console: specify whether to display the message to the file.
        :type to_console: bool
        """
        logger: logging.Logger = logging.getLogger(name)
        if not logger.hasHandlers():
            if to_file: logger.addHandler(logging.FileHandler(f"{cls._LOG_DIR}/logs.log"))
            if to_console: logger.addHandler(logging.StreamHandler())

        match level:
            case logging.INFO:
                logger.info(message)
            case logging.WARNING:
                logger.warning(message)
            case logging.ERROR:
                logger.error(message)
            case logging.CRITICAL:
                logger.critical(message)
            case _:
                logger.error(f"Invalid logging level provided: {level}")


if __name__ == "__main__":  
    Logger.configure()  
    Logger.log(Logger.__name__, logging.INFO, "This is an informational message.")  
    Logger.log(Logger.__name__, logging.ERROR, "This is an error message.") 
