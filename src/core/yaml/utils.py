from typing import Any, get_args

def return_string(value: Any, default: str = "") -> str:
    '''Checks if the given value is a string and return a default string.'''
    if isinstance(value, str):
        return value
    
    return default

def return_bool(value: Any, default: bool = True) -> bool:
    '''Checks if the given value is a type `bool` and return a default `bool`.'''
    if isinstance(value, bool):
        return value
    
    return default

def return_list(value: Any) -> list[Any]:
    '''Checks if the given value is a type `list` and return the value.
    
    If it is not a `list`, then return an empty list as the default value.
    '''
    if isinstance(value, list):
        return value

    emp: list[Any] = [] 
    return emp

def return_literal(value: Any, literal: Any, default: str):
    '''Checks if the given value is of type `literal`. If not, then return
    the given default value.
    '''
    if value in get_args(literal):
        return value
    
    return default