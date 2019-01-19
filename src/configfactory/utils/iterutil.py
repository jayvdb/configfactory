from typing import Callable, List, Union, Any

Iter = Union[list, dict, Any]
IterPath = List[Union[int, str]]


def traverse(obj: Iter, callback: Callable[[Iter, IterPath], Iter], path: IterPath = None) -> Iter:
    """
    Traverse through nested dict or list.
    """

    path = path or []

    if isinstance(obj, dict):
        return {
            key: traverse(value, callback, path + [key])
            for key, value in obj.items()
        }
    elif isinstance(obj, list):
        return [
            traverse(elem, callback, path + [index])
            for index, elem in enumerate(obj)
        ]

    return callback(obj, path)
