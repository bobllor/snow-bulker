from pydantic import RootModel
from src.core.yaml.yaml_loader import YamlLoader
from typing import Type
from .types import CustomOrder, RootData
from logger import Log

class DataYamlLoader(YamlLoader):
    '''Class for reading the data YAML file.
    
    The file is expected to be dictionaries and can dynamically handle multiple at once.
    The return will be a `dict[str, DataYaml]` of root.
    '''
    def __init__(self, base_model: Type[RootModel] = None, *, logger: Log = None):
        if base_model is None:
            base_model = RootData
        super().__init__(base_model, logger=logger)
    
    def validate_custom_order(self, data: CustomOrder) -> bool:
        '''Validates the required values of CustomOrder for empty values.
        
        If any empty values are found, then it will return False.
        '''
        # i could of just iterated over a dict but i wanted to be explicit
        # not pythonic!
        values: list[str] = [
            data.cpu, 
            data.make, 
            data.model,
            data.ram,
            data.storage,
        ]

        return all([val.strip() != "" for val in values])