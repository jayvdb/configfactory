from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Field, Layout, Submit
from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


from configfactory.forms.layout import Back


class BackupImportForm(forms.Form):

    file = forms.FileField(help_text=_('Select exported .json file.'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('file'),
            ButtonHolder(
                Submit('import', _('Import')),
                Back(reverse('backups'))
            )
        )

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file.content_type != 'application/json':
            raise ValidationError(_('Please, select a valid json file.'))
        return file
