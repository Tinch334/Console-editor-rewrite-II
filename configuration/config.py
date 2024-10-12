import os.path
from typing import Optional
from yaml import safe_load

#The configuration class, uses a singleton pattern to only load the configuration file once and to make it accessible without needing a reference
#to the "Config" class.
class Config(object):
    _CONFIG: Optional[dict] = None

    def __init__(self, config_file: str) -> None:
        if not os.path.exists(config_file):
            raise FileNotFoundError("The configuration file doesn't exist")

        if Config._CONFIG is None:
            with open(config_file, "r") as file:
                Config._CONFIG = safe_load(file)

    @staticmethod
    def get_config() -> Optional[dict]:
        return Config._CONFIG