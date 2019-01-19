from django.core.exceptions import ValidationError


class InvalidSettingsError(ValidationError):
    pass


class ComponentDeleteError(Exception):
    pass
