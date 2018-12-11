import abc
from typing import Dict


class ConfigStore(abc.ABC):

    @abc.abstractmethod
    def all(self) -> Dict[str, Dict[str, str]]:
        pass

    @abc.abstractmethod
    def update(self, environment: str, component: str, data: str):
        pass

    @abc.abstractmethod
    def delete(self, environment: str, component: str):
        pass
