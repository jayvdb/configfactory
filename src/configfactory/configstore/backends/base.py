import abc
from typing import Optional, Dict


class ConfigStoreBackend(abc.ABC):

    @abc.abstractmethod
    def all_data(self) -> Dict[str, Dict[str, str]]:
        pass

    @abc.abstractmethod
    def get_data(self, environment: str, component: str) -> Optional[dict]:
        pass

    @abc.abstractmethod
    def update_data(self, environment: str, component: str, data: str):
        pass

    @abc.abstractmethod
    def delete_data(self, environment: str, component: str):
        pass
