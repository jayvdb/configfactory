import copy
from typing import Callable, List, T


def flatten(d: dict, parent_key='', sep='.') -> dict:
    """
    Flatten dictionary keys.
    """
    ret = {}
    for key, value in d.items():
        new_key = sep.join([parent_key, key]) if parent_key else key
        if isinstance(value, dict):
            ret.update(flatten(value, new_key, sep=sep))
        else:
            ret[new_key] = value
    return ret


def merge(d1, d2):
    """
    Merge two dictionaries.
    """

    if not isinstance(d2, dict):
        return d2

    ret = copy.deepcopy(d1)
    for key, value in d2.items():
        if key in ret and isinstance(ret[key], dict):
            ret[key] = merge(ret[key], value)
        else:
            ret[key] = copy.deepcopy(value)
    return ret


def traverse(obj: T, callback: Callable[[T, List[str]], T] = None, path: List[str] = None) -> T:
    """
    Traverse through nested dictionary.
    """

    if path is None:
        path = []

    if isinstance(obj, dict):
        value = {
            key: traverse(value, callback, path + [key])
            for key, value in obj.items()
        }
    elif isinstance(obj, list):
        value = [
            traverse(elem, callback, path + [])
            for elem in obj
        ]
    else:
        if callback is None:
            value = obj
        else:
            value = callback(obj, path)

    return value
