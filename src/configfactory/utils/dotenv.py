from configfactory.utils import dicthelper


def dumps(obj: dict) -> str:

    obj = dicthelper.flatten(obj)

    def _process(value, key):
        path = '_'.join(key).upper().replace('.', '_')
        return f'{path}={value}'

    return'\n'.join(
        dicthelper.traverse(obj, _process).values()
    )
