from typing import Literal, TypedDict

Locator = Literal[
    "id", 
    "xpath", 
    "link text", 
    "partial link text", 
    "name", 
    "tag name", 
    "class name", 
    "css selector"
]

class Options(TypedDict):
    headless: bool
    silent: bool