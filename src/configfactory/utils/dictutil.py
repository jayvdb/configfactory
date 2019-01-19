import copy


def merge(d1: dict, d2: dict) -> dict:
    """
    Merge two dictionaries.
    """
    ret = copy.deepcopy(d1)
    for key, value in d2.items():
        if key in ret and isinstance(ret[key], dict):
            ret[key] = merge(ret[key], value)
        else:
            ret[key] = copy.deepcopy(value)
    return ret


def flatten(d: dict, parent: str = '', sep: str = '.') -> dict:
    """
    Flatten dictionary keys.
    """
    ret = {}
    for key, value in d.items():
        new_key = sep.join([parent, key]) if parent else key
        if isinstance(value, dict):
            ret.update(flatten(value, new_key, sep=sep))
        else:
            ret[new_key] = value
    return ret
