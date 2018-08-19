import re

from configfactory.exceptions import CircularInjectError, InjectKeyError
from configfactory.utils import dicthelper

param_pattern = r'[a-zA-Z][(\-|\.)a-zA-Z0-9_]*'
param_re = re.compile(r'(?<!\$)(\$(?:{param:(%(n)s)}))' % ({'n': param_pattern}))
circular_threshold = 100


def inject(data, params, strict=True, calls=0):
    """
    Inject params to data.
    """

    # Travers data values
    if isinstance(data, (list, dict)):
        return dicthelper.traverse(data, lambda value, key: inject(
            data=value,
            params=params,
            strict=strict
        ))

    # Return other types
    if not isinstance(data, str):
        return data

    result = param_re.findall(data)

    # Increment recursive calls
    calls += 1

    # Skip parameters replace
    if not result:
        return data

    # Check circular injections
    if calls > circular_threshold:
        if strict:
            raise CircularInjectError('Circular injections detected.')
        return data

    # Replace data params
    for whole, key in result:
        try:
            value = inject(
                data=params[key],
                params=params,
                calls=calls,
                strict=strict
            )
            str_value = str(value)
            data = data.replace(whole, str_value)
            if str_value == data:
                return value
        except KeyError:
            if strict:
                raise InjectKeyError(f'Injection key `{key}` does not exist.', key=key)

    return inject(
        data=data,
        params=params,
        calls=calls,
        strict=strict
    )
