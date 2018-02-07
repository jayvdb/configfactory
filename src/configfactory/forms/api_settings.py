from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Field, Layout, Submit
from django import forms
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from configfactory.forms.layout import Back
from configfactory.models import APISettings


class APISettingsForm(forms.ModelForm):

    token = forms.CharField(label=_('Token'), disabled=True, required=False)

    reset_token = forms.BooleanField(label=_('Reset token'), required=False)

    class Meta:
        model = APISettings
        fields = ('is_enabled', 'token',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('is_enabled'),
            Field('token'),
            Field('reset_token'),
            ButtonHolder(
                Submit('save', _('Save')),
                Back(reverse('groups'))
            )
        )

    def clean(self):
        data = self.cleaned_data
        reset_token = data['reset_token']
        if reset_token:
            data['token'] = None
        return data
