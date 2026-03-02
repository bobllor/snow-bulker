from pydantic import BaseModel, RootModel
from typing import Literal, Any

type Profile = Literal["dell i5", "dell i7", "dell i7 big", "custom", "return"]
type OperatingSystems = Literal["windows 11", "windows 10", "no operating system"]

type HardwareOptions = Literal[
    "laptop bag", 
    "cable lock",
    "docking station",
    "surface pro dock",
    "wireless combo",
    "lifechat",
    "monitor 20",
    "monitor 22",
    "monitor 24",
    "monitor 20 2nd",
    "monitor 22 2nd",
    "monitor 24 2nd",
    "apple keyboard",
    "apple mouse"
]

type SoftwareOptions = Literal[
    "microsoft office web apps",
    "microsoft office desktop apps",
    "microsoft exchange",
    "microsoft project",
    "microsoft visio",
    "symantec",
    "adobe creative cloud",
    "power bi",
    "office timeline",
    "adobe photoshop",
    "adobe illustrator",
    "adobe indesign",
    "adobe xd",
    "adobe acrobat pro",
    "adobe acrobat standard",
    "adobe dreamweaver",
    "adobe captivate",
]

class CustomOrder(BaseModel):
    cpu: str = ""
    model: str = ""
    make: str = ""
    ram: Any = ""
    storage: Any = ""
    other_specs: str = "N/A"
    software_needed: str = "N/A"

class DataYaml(BaseModel):
    '''The data from the data YAML file. 
    
    To access this data, the RootData object must be used.'''
    account_manager_email: str
    profile: Profile
    data_file: str
    email_cache: str = "default_cache.txt"
    hardware: list[HardwareOptions] = [] # changes to HardwareOptions need to be also be changed in HTML types
    software: list[SoftwareOptions] = [] # changes to SoftwareOptions need to be also be changed in HTML types
    ignore: bool = False
    desired_software: str = ""
    os_type: OperatingSystems = "windows 11"
    custom_order: CustomOrder = CustomOrder()

class RootData(RootModel):
    '''A dictionary with dynamic keys and its value DataYaml.'''
    root: dict[str, DataYaml]