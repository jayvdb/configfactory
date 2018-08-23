from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Field, Layout, Submit
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from configfactory.exceptions import InvalidSettingsError
from configfactory.forms.fields import JSONField
from configfactory.forms.layout import Back
from configfactory.models import Component
from configfactory.services.configsettings import validate_settings
from configfactory.shortcuts import back_url


class ComponentForm(forms.ModelForm):

    class Meta:
        model = Component
        fields = (
            'name',
            'alias',
            'is_global',
            'require_schema',
            'strict_keys',
            'is_active',
        )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('name'),
            Field('alias'),
            Field('is_global'),
            Field('require_schema'),
            Field('strict_keys'),
            Field('is_active'),
            ButtonHolder(
                Submit('save', _('Save')),
                Back(back_url('dashboard', request=request))
            )
        )


class ComponentSchemaForm(forms.Form):

    schema = JSONField(required=False, widget=forms.Textarea(attrs={
        'rows': 32,
        'style': 'width: 100%'
    }))


class ComponentSettingsForm(forms.Form):

    def __init__(self, component, environment, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.component = component
        self.environment = environment

    settings = JSONField(required=False, widget=forms.Textarea(attrs={
        'rows': 32,
        'style': 'width: 100%'
    }))

    def clean_settings(self):

        data = self.cleaned_data['settings']

        try:
            validate_settings(
                environment=self.environment,
                component=self.component,
                data=data,
            )
        except InvalidSettingsError as exc:
            raise ValidationError(str(exc))

        return data
