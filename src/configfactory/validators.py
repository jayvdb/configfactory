from typing import Any

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _

from configfactory.utils import dictutil


@deconstructible
class SettingsFormatValidator:

    def __call__(self, data: dict):
        data = dictutil.flatten(data)
        for key, value in data.items():
            self.validate_type(key, value)

    def validate_type(self, key: str, value: Any):
        if isinstance(value, list):
            self.validate_list(key, value)
        elif not isinstance(value, (int, str, float, bool)) and value is not None:
            raise ValidationError(_('Invalid `%(key)s` type.') % {'key': key})

    def validate_list(self, key: str, value: list):
        for index, el in enumerate(value):
            self.validate_type('.'.join([key, str(index)]), el)


def validate_settings_format(value: dict) -> None:
    validate = SettingsFormatValidator()
    validate(value)
