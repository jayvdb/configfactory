import abc
from typing import Dict

AllData = Dict[str, Dict[str, str]]


class ConfigStore(abc.ABC):

    @abc.abstractmethod
    def get_all_data(self) -> AllData:
        pass

    @abc.abstractmethod
    def update_data(self, environment: str, component: str, data: str):
        pass

    @abc.abstractmethod
    def delete_data(self, environment: str, component: str):
        pass
