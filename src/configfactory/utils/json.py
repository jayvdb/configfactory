import json
from collections import OrderedDict

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


def loads(s):
    if not s:
        return {}
    try:
        return json.loads(s, object_pairs_hook=OrderedDict)
    except Exception as e:
        raise JSONLoadError(
            'Invalid JSON: {}.'.format(e)
        )
