from typing import Any, Type, Literal, TypedDict
from pydantic import BaseModel, ValidationError, RootModel
from pydantic_core import ErrorDetails
from src.support.types import Result
from src.core.yaml.html_yaml.types import HTMLFields
from src.core.yaml.data_yaml.types import RootData
from src.core.yaml.config_yaml.types import Config
from logger import Log
from pathlib import Path
import yaml

class YamlLoader:
    '''Class used to load YAML files.'''
    def __init__(self, base_class: Type[BaseModel | RootModel], *, logger: Log = None):
        '''Initialize a YamlLoader class.
        
        Parameters
        ----------
            base_class: Type[BaseModel | RootModel]
                Any object that uses the BaseModel or RootModel.
            
            logger: Log
                The Log object for logging. By default it is None and will use its default
                configuration.
        '''
        self.logger: Log = logger or Log()
        self.base_class: Type[BaseModel | RootModel] = base_class

    def read(self, file: str | Path, *, lower: bool = False) -> dict[str, Any]:
        '''Reads a YAML file and returns the contents of the dictionary.
        
        This returns the exact contents from the file.

        Parameters
        ----------
            file: str | Path
                The string or Path of the target file to read.

            lower: bool
                If `True`, then lowercase all keys and values. By default it is
                `False`.
        '''
        with open(file, "r") as file:
            yaml_data: dict[str, Any] = yaml.safe_load(file)

        return self.to_lower(yaml_data) if lower else yaml_data

    def validate(self, data: dict[str, Any]) -> Result:
        '''Validates the data dictionary. It will return a Result object with the
        base model in `content`.

        If the validation fails or another exception occurs, then an error will be returned
        with the message.        

        Parameters
        ----------
            data: dict[str, Any]
                The dictionary being validated to the BaseModel.
        '''
        res: Result = Result(
            msg="Successfully validated YAML",
            err=False,
            content=None,
        )

        try:
            model: type[BaseModel | RootModel] = self.base_class(**data)

            res.content = model
        except ValidationError as ve:
            err: ErrorDetails = ve.errors()[0]
            err_dict: dict[str, Any] = {
                "type": err["type"],
                "location": ">".join([str(ele) for ele in err["loc"]]),
                "input": err["input"],
                "msg": err["msg"],
            }

            msg: str = f"Failed to validate data: {err_dict}"

            res.msg = msg
            res.err = True

            return res
        
        return res
    
    def to_lower(self, data: dict[str, Any]) -> dict[str, Any]:
        '''Lowercases all keys and values of a `dict` if applicable recursively.'''
        data_copy: dict[str, Any] = data.copy()

        for key, val in data_copy.items():
            if isinstance(val, dict):
                temp_val: dict[str, Any] = self.to_lower(val)

                val = temp_val

            data_copy[key.lower()] = val.lower() if isinstance(val, str) else val
        
        return data_copy

type ParsedYamlKeys = Literal["excel_root", "html_fields", "config"]

class YamlStarter(TypedDict):
    '''Object used to get a parsed YAML data.'''
    yaml_loader: Type[YamlLoader]
    data_file: str
    parsed_key: ParsedYamlKeys

class ParsedYaml(TypedDict):
    '''Parsed YAML as an object.'''
    excel_root: RootData
    html_fields: HTMLFields
    config: Config