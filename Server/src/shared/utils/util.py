import os
from typing import Any

from dotenv import load_dotenv


class Util:
    """
    Utility class for server.
    """
    @staticmethod
    def get_root_dir() -> str:
        """
        :return str: Returns the root directory using the src folder as the target folder.
        """
        current_dir: str = os.path.dirname(os.path.abspath(__file__))
        while current_dir != os.path.dirname(current_dir):
            if "src" in os.listdir(current_dir):
                return current_dir
            current_dir = os.path.dirname(current_dir)
        raise FileNotFoundError("The 'src' folder was not found in the directory hierarchy.")

    @staticmethod
    def get_env_variables(variables: list[str]) -> list[Any]:
        env_file: str = os.path.join(Util.get_root_dir(), "secrets/.env")
        load_dotenv(env_file)
        values: list[Any] = []
        for variable in variables:
            value: Any = os.getenv(variable)
            if value == None:
                raise ValueError(f"The environment variable {variable} does not exist.")
            values.append(value)
        return values