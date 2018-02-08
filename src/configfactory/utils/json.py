import json

from django.core.serializers.json import DjangoJSONEncoder


class JSONLoadError(Exception):
    pass


def dumps(obj, indent=None, compress=False):
    separators = None
    if compress:
        separators = (',', ':')
    return json.dumps(
        obj=obj,
        indent=indent,
        separators=separators,
        cls=DjangoJSONEncoder
    )


def loads(s: str):
    if not s:
        return {}
    try:
        return json.loads(s)
    except Exception as exc:
        raise JSONLoadError(f'Invalid JSON: {exc}.')
