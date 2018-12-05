from django import forms
from django.core.exceptions import ValidationError
from django.forms import fields

from configfactory.utils import json


class JSONObjectField(fields.CharField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', forms.Textarea())
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
                if isinstance(value, list):
                    raise ValidationError("JSON must be an object.")
            except json.JSONLoadError:
                raise ValidationError("Enter valid JSON.")
        return value

    def prepare_value(self, value):
        if isinstance(value, dict):
            return json.dumps(value, indent=4)
        return value
