from src.core.yaml.yaml_loader import YamlLoader
from pydantic import BaseModel
from typing import Type
from .types import HTMLFields
from logger import Log


class HTMLYamlLoader(YamlLoader):
    '''Class used to load the YAML file consisting of the HTML elements for the program.
    
    All values of the HTML YAML file is required.
    '''
    def __init__(self, base_model: Type[BaseModel] = None, *, logger: Log = None):
        '''
        Parameters
        ----------
            base_model: Type[BaseModel]
                Any object type of BaseModel. By default it is None and will use the `HTMLFields` class.
            
            logger: Log
                A Log object. By default it is None and will use a default object.
        '''
        if base_model is None:
            base_model = HTMLFields

        super().__init__(base_model, logger=logger)