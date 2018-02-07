from typing import Optional

from .base import ConfigStoreBackend


class MemoryConfigStore(ConfigStoreBackend):

    def __init__(self):
        self._settings = {}

    def all_data(self) -> dict:
        return self._settings

    def get_data(self, environment: str, component: str) -> Optional[dict]:
        try:
            return self._settings[environment][component]
        except KeyError:
            return None

    def update_data(self, environment: str, component: str, data: dict):
        if environment not in self._settings:
            self._settings[environment] = {}
        self._settings[environment][component] = data

    def delete_data(self, environment: str, component: str):
        try:
            del self._settings[environment][component]
        except KeyError:
            pass
