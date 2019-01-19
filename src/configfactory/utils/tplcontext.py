import re
from typing import Any, Dict, Union

from django.utils.translation import ugettext_lazy as _

from configfactory.utils import itertool

KEY_PATTERN = r'[a-zA-Z][(\-|\.)a-zA-Z0-9_]*'
KEY_RE = re.compile(r'(?<!\$)(\$(?:{(%(n)s)}))' % ({'n': KEY_PATTERN}))
CIRCULAR_THRESHOLD = 50

Template = Union[list, dict, str, Any]


class CircularInjectError(Exception):
    pass


class InvalidKey(Exception):

    def __init__(self, message: str, key: str):
        self.message = message
        self.key = key

    def __str__(self):
        return self.message


def inject(tpl: Template, context: Dict[str, Any], strict: bool = True, calls: int = 0) -> Template:
    """
    Inject context to tpl.
    """

    # Traverse tpl values
    if isinstance(tpl, (list, dict)):
        return itertool.traverse(tpl, lambda value, key: inject(
            tpl=value,
            context=context,
            strict=strict
        ))

    # Return other types
    if not isinstance(tpl, str):
        return tpl

    result = KEY_RE.findall(tpl)

    # Increment recursive calls
    calls += 1

    # Skip parameters replace
    if not result:
        return tpl

    # Check circular injections
    if calls > CIRCULAR_THRESHOLD:
        if strict:
            raise CircularInjectError(_('Circular injections detected.'))
        return tpl

    # Replace tpl context
    for whole, key in result:
        try:
            value = inject(
                tpl=context[key],
                context=context,
                calls=calls,
                strict=strict
            )
            str_value = str(value)
            tpl = tpl.replace(whole, str_value)
            if str_value == tpl:
                return value
        except KeyError:
            if strict:
                raise InvalidKey(_('Injected key `%(key)s` does not exist.') % {'key': key}, key=key)

    return inject(
        tpl=tpl,
        context=context,
        calls=calls,
        strict=strict
    )
