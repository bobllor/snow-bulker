from src.core.yaml.yaml_loader import YamlLoader
from pydantic import BaseModel
from logger import Log
from typing import Type
from .types import Config

class ConfigYamlLoader(YamlLoader):
    def __init__(self, base_model: Type[BaseModel] = None, *, logger: Log = None):
        if base_model is None:
            base_model = Config

        super().__init__(base_model, logger=logger)

    def check_empty(self, config_data: dict[str, Type[BaseModel] | str], arr: list[str] = None) -> list[str]:
        '''Checks for any values for an empty string from a dictionary recursively. 
        
        It will return a list of keys that have an empty value.

        Parameters
        ----------
            config_data: dict[str, Type[BaseModel]]
                The data to check. This is the converted Config data to a dictionary.
            
            arr: list[str]
                A list used to hold the keys with empty values. By default this is None.
                This is intended to be used with the recursive call.
        '''
        if arr is None:
            arr = []
        
        for key, val in config_data.items():
            if val == "":
                arr.append(key)
            elif isinstance(val, BaseModel):
                data: dict[str, Type[BaseModel] | str] = dict(val)

                arr.extend(self.check_empty(data))
        
        return arr