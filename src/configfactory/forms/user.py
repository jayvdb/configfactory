from crispy_forms.bootstrap import FormActions, Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, ButtonHolder
from django import forms
from django.contrib.auth.forms import SetPasswordForm as BaseSetPasswordForm
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from configfactory.forms.layout import Back
from configfactory.models import User


class UserForm(forms.ModelForm):

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
                Back(reverse('users'))
            )
        )


class UserAccessForm(forms.ModelForm):

    class Meta:
        model = User
        fields = (
            'is_active',
            'is_superuser',
            'groups',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('is_active'),
            Field('is_superuser'),
            Field('groups'),
            FormActions(
                Submit('save', _('Save')),
                Back(reverse('users'))
            )
        )


class UserSetPasswordForm(BaseSetPasswordForm):

    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput,
        strip=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('new_password1'),
            Field('new_password2'),
            ButtonHolder(
                Submit('change', _('Change')),
                Back(reverse('users'))
            )
        )
