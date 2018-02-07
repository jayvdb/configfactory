from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Field, Layout, Submit
from django import forms
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from configfactory.forms.layout import Back


class GroupForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('name'),
            ButtonHolder(
                Submit('save', _('Save')),
                Back(reverse('groups'))
            )
        )
