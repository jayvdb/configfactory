from typing import Dict

from .base import ConfigStore


class MemoryConfigStore(ConfigStore):

    def __init__(self):
        self._data: Dict[str, Dict[str, str]] = {}

    def all(self) -> Dict[str, Dict[str, str]]:
        return self._data

    def update(self, environment: str, component: str, data: str):
        if environment not in self._data:
            self._data[environment] = {}
        self._data[environment][component] = data

    def delete(self, environment: str, component: str):
        try:
            del self._data[environment][component]
        except KeyError:
            pass
