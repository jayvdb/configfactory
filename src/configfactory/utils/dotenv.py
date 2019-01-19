from configfactory.utils import dictutil, iterutil


def dumps(obj: dict) -> str:

    obj = dictutil.flatten(obj)

    def _process(value, key):
        path = '_'.join(key).upper().replace('.', '_')
        return f'{path}={value}'

    return'\n'.join(
        iterutil.traverse(obj, _process).values()
    )
