from .base import AllData, ConfigStore


class MemoryConfigStore(ConfigStore):

    def __init__(self):
        self._data: AllData = {}

    def get_all_data(self) -> AllData:
        return self._data

    def update_data(self, environment: str, component: str, data: str):
        if environment not in self._data:
            self._data[environment] = {}
        self._data[environment][component] = data

    def delete_data(self, environment: str, component: str):
        try:
            del self._data[environment][component]
        except KeyError:
            pass
