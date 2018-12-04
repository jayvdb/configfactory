import json
import re
from collections import Mapping
from typing import Dict, List

import jsonschema
from django.core.exceptions import ValidationError

from configfactory.utils import dicthelper, json, tplparams, security


class DotEnvFormatError(Exception):
    pass


class SettingsDict(Mapping):

    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "$ref": "#/definitions/settings",
        "definitions": {
            "settings": {
                "type": "object",
                "patternProperties": {
                    "^.*$": {
                        "anyOf": [
                            {"type": "string"},
                            {"type": "number"},
                            {"type": "boolean"},
                            {"type": "integer"},
                            {"type": "null"},
                            {
                                "type": "array",
                                "items": {
                                    "type": [
                                        "string",
                                        "number",
                                        "boolean",
                                        "integer",
                                        "null"
                                    ]
                                }
                            },
                            {
                                "type": "object",
                                "$ref": "#/definitions/settings"
                            }
                        ]
                    }
                },
                "additionalProperties": False
            }
        }
    }

    separator = '.'

    def __init__(self, *args, **kwargs):
        self._data: Dict = dict(*args, **kwargs)
        self._valid = None

    def __getitem__(self, k):
        return self._data[k]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    @classmethod
    def from_json(cls, s: str) -> 'SettingsDict':
        """
        Create settings dict from JSON string.
        """
        data = json.loads(s)
        return cls(data)

    @property
    def valid(self) -> bool:
        """
        Get validation status.
        """
        if self._valid is None:
            try:
                self.validate()
            except ValidationError:
                pass
        return self._valid

    def validate(self):
        """
        Validate settings using JSON schema.
        """
        if self._valid is None:
            try:
                jsonschema.validate(self._data, schema=self.schema)
                self._valid = True
            except jsonschema.ValidationError as exc:
                self._valid = False
                raise ValidationError(exc.message)

    def flatten(self) -> 'SettingsDict':
        """
        Make Flatten settings data keys.
        """
        data = dicthelper.flatten(self._data)
        return SettingsDict(data)

    def merge(self, other: 'SettingsDict') -> 'SettingsDict':
        """
        Merge settings.
        """
        data = dicthelper.merge(self._data, other.to_dict())
        return SettingsDict(data)

    def inject(self, params: dict, strict: bool = True) -> 'SettingsDict':
        data = tplparams.inject(self._data, params=params, strict=strict)
        return SettingsDict(data)

    def cleanse(self, hidden: List[str]='password', substitute='*****') -> 'SettingsDict':

        hidden_re = re.compile('|'.join(hidden), flags=re.IGNORECASE)

        def _replace(value, key):
            path = '.'.join(key)
            if hidden_re.search(path):
                return substitute
            return value

        data = dicthelper.traverse(self._data, _replace)

        return SettingsDict(data)

    def encrypt(self) -> 'SettingsDict':
        pass

    def decrypt(self, secure_keys: List[str]) -> 'SettingsDict':
        data = security.decrypt(self._data, secure_keys=secure_keys)
        return SettingsDict(data)

    def to_dict(self) -> dict:
        """
        Dump settings to python dictionary.
        """
        return self._data

    def to_json(self, pretty: bool = True, compress: bool = False) -> str:
        """
        Dump settings to JSON format.
        """
        indent = None
        separators = None
        if pretty:
            indent = 4
        if compress:
            separators = (',', ':')
            indent = None
        return json.dumps(self._data, indent=indent, separators=separators)

    def to_dotenv(self) -> str:
        """
        Dump settings to DotEnv format.
        """
        if not self.valid:
            raise DotEnvFormatError('Cannot dump invalid settings to DotEnv format.')

        settings = self.flatten()
        rows = []

        for key, value in settings.items():

            if isinstance(value, list):
                value = ','.join(map(str, value))
            elif isinstance(value, bool):
                if value:
                    value = 'true'
                else:
                    value = 'false'

            path = key.upper().replace('.', '_')
            rows.append(f'{path}={value}')

        return '\n'.join(rows)
