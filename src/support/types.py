from typing import TypedDict, TypeVar, Generic
from dataclasses import dataclass
from pathlib import Path
from src.core.yaml.config_yaml.types import Config

T = TypeVar("T")

@dataclass
class Result(Generic[T]):
    '''Class used for holding the result of an action.'''
    msg: str = ""
    err: bool = False
    content: T = None

UserInfo = TypedDict(
    "UserInfo",
    {
        "full name": str,
        "email": str,
    }
)

UserData = TypedDict(
    "UserData",
    {
        "full name": str,
        "email": str,
        "employee id": str,
    }
)

AddressData = TypedDict(
    "AddressData",
    {
        "street": str,
        "city": str,
        "country": str,
        "state": str,
        "postal": str,
        "phone": str,
    }
)

CompanyData = TypedDict(
    "CompanyData",
    {
        "operating company": str,
        "division": str,
        "desired by": str,
        "start date": str,
        "end date": str,
        "project id": str,
        "customer id": str,
        "customer name": str,
        "office id": str,
        "office name": str,
        "region": str,
    }
)

class CustomOrder(TypedDict):
    make: str
    model: str
    storage: str
    cpu: str
    ram: int
    software_needed: str
    other_specs: str

class ReturnOrder(TypedDict):
    packaging_required: bool

ReturnColumns = TypedDict(
    "ReturnColumns",
    {
        "full name": str,
        "email": str,
        "street": str,
        "city": str,
        "state": str,
        "postal": str,
        "phone": str,
        "country": str,
        "packaging required": str,
        "additional notes": str,
    }
)

class ReturnData(TypedDict):
    return_data: list[ReturnColumns]

class ExcelData(TypedDict):
    user: list[UserData]
    address: list[AddressData]
    company: list[CompanyData]

@dataclass
class BulkData:
    '''Class used for the data required to start the bulk process.'''
    excel_data: ExcelData | ReturnData
    email_cache: set[str]
    cache_path: Path
    section: str
    config: Config
    is_return_profile: bool