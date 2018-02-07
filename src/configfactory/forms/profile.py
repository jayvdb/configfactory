from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Field, Layout, Submit
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from configfactory.forms.layout import Back
from configfactory.models import User


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username'),
            Field('email'),
            Field('first_name'),
            Field('last_name'),
            FormActions(
                Submit('save', _('Save')),
                Back(reverse('dashboard'))
            )
        )


class ProfilePasswordChangeForm(PasswordChangeForm):

    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput,
        strip=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('old_password'),
            Field('new_password1'),
            Field('new_password2'),
            ButtonHolder(
                Submit('change', _('Change')),
                Back(reverse('dashboard'))
            )
        )
