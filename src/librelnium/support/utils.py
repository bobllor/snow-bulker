from typing import Iterable, Any

def is_list_tuple(arg: Iterable) -> bool:
    '''Checks if an arg is a list or tuple.'''
    if not isinstance(arg, tuple) and not isinstance(arg, list):
        return False
    
    return True

def is_type(arg: Any, type_: type) -> bool:
    '''Checks if an arg is a given type.'''
    if not isinstance(arg, type_):
        return False
    
    return True