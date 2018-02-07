class InjectKeyError(Exception):

    def __init__(self, message: str, key: str):
        self._message = message
        self._key = key

    @property
    def message(self):
        return self._message

    @property
    def key(self) -> str:
        return self._key

    def __str__(self):
        return self.message


class CircularInjectError(RuntimeError):
    pass


class ComponentValidationError(Exception):

    def __init__(self, message, exc=None):
        self.message = message
        self.exc = exc

    def __str__(self):
        return self.message


class ComponentDeleteError(Exception):
    pass
