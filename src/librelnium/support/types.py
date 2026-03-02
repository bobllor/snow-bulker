from typing import Literal

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