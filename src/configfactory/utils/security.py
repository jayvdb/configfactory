import abc
import base64
import re
from typing import Any, List

from cryptography.fernet import Fernet
from django.conf import settings
from django.utils.functional import cached_property

from configfactory.utils import dicthelper, json


class Encryptor(abc.ABC):

    @abc.abstractmethod
    def encrypt(self, data: bytes) -> bytes:
        pass

    @abc.abstractmethod
    def decrypt(self, data: bytes) -> bytes:
        pass


class FernetDataEncryptor(Encryptor):

    def __init__(self, encode_key: str):
        self.encode_key = encode_key

    @cached_property
    def _fernet(self):
        key = base64.urlsafe_b64encode(
            self.encode_key[:32].encode()
        )
        return Fernet(key)

    def encrypt(self, data: bytes) -> bytes:
        return self._fernet.encrypt(data)

    def decrypt(self, data: bytes) -> bytes:
        return self._fernet.decrypt(data)


class DummyDataEncryptor(Encryptor):

    def encrypt(self, data: bytes) -> bytes:
        return data

    def decrypt(self, data: bytes) -> bytes:
        return data


class DataEncryptor:

    @property
    def _encryptor(self) -> Encryptor:
        if not settings.ENCRYPT_ENABLED:
            return DummyDataEncryptor()
        else:
            return FernetDataEncryptor(settings.ENCRYPT_TOKEN)

    def encrypt(self, data: str) -> str:
        return self._encryptor.encrypt(data.encode()).decode()

    def decrypt(self, data: str) -> str:
        return self._encryptor.decrypt(data.encode()).decode()


encryptor = DataEncryptor()

# Public API helpers
encrypt_data = encryptor.encrypt
decrypt_data = encryptor.decrypt


def is_encrypted(value: Any) -> bool:
    return isinstance(value, str) and value.startswith(settings.ENCRYPT_PREFIX)


def encrypt(data: dict, secure_keys: List[str]) -> dict:

    if not secure_keys:
        return data

    hidden_re = re.compile('|'.join(secure_keys), flags=re.IGNORECASE)

    def _process(value: Any, key: List[str]) -> str:

        if not is_encrypted(value):
            path = '.'.join(key)
            if hidden_re.search(path):
                encrypted_data = encrypt_data(json.dumps({
                    'value': value
                }))
                return f'{settings.ENCRYPT_PREFIX}{encrypted_data}'

        return value

    return dicthelper.traverse(data, _process)


def decrypt(data: dict, secure_keys: List[str]) -> dict:

    hidden_re = re.compile('|'.join(secure_keys), flags=re.IGNORECASE)

    def _process(value: Any, key: List[str]) -> Any:

        if is_encrypted(value):
            path = '.'.join(key)
            if hidden_re.search(path):
                encrypted_data = value.split(settings.ENCRYPT_PREFIX, maxsplit=1)[-1]
                obj = decrypt_data(encrypted_data)
                return json.loads(obj)['value']

        return value

    return dicthelper.traverse(data, _process)


def cleanse(data: dict, hidden='password', substitute='*****'):

    if isinstance(hidden, str):
        hidden = hidden.split()

    hidden_re = re.compile('|'.join(hidden), flags=re.IGNORECASE)

    def _replace(value, key):
        path = '.'.join(key)
        if hidden_re.search(path):
            return substitute
        return value

    return dicthelper.traverse(data, _replace)
