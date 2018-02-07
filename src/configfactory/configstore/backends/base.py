import abc
from typing import Optional


class ConfigStoreBackend(abc.ABC):

    @abc.abstractmethod
    def all_data(self) -> dict:
        pass

    @abc.abstractmethod
    def get_data(self, environment: str, component: str) -> Optional[dict]:
        pass

    @abc.abstractmethod
    def update_data(self, environment: str, component: str, data: dict):
        pass

    @abc.abstractmethod
    def delete_data(self, environment: str, component: str):
        pass
