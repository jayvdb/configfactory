import re
from typing import Any, Dict, Union, Set

from django.utils.translation import ugettext_lazy as _

from configfactory.utils import iterutil

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


def inject(template: Template, context: Dict[str, Any], strict: bool = True, calls: int = 0) -> Template:
    """
    Inject context to template.
    """

    # Traverse template values
    if isinstance(template, (list, dict)):
        return iterutil.traverse(template, lambda v, k: inject(
            template=v,
            context=context,
            strict=strict
        ))

    # Return other types
    if not isinstance(template, str):
        return template

    result = KEY_RE.findall(template)

    # Increment recursive calls
    calls += 1

    # Skip parameters replace
    if not result:
        return template

    # Check circular injections
    if calls > CIRCULAR_THRESHOLD:
        if strict:
            raise CircularInjectError(_('Circular injections detected.'))
        return template

    # Replace template context
    for whole, key in result:
        try:
            value = inject(
                template=context[key],
                context=context,
                calls=calls,
                strict=strict
            )
            str_value = str(value)
            template = template.replace(whole, str_value)
            if str_value == template:
                return value
        except KeyError:
            if strict:
                raise InvalidKey(_('Injected key `%(key)s` does not exist.') % {'key': key}, key=key)

    return inject(
        template=template,
        context=context,
        calls=calls,
        strict=strict
    )


def findkeys(s: str) -> Set[str]:
    """
    Find injected keys.
    """
    return {match[1] for match in KEY_RE.findall(s)}
