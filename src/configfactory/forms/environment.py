from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Field, Layout, Submit
from django import forms
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from configfactory.forms.layout import Back
from configfactory.models import Environment


class EnvironmentForm(forms.ModelForm):

    order = forms.IntegerField(min_value=0, required=False)

    class Meta:
        model = Environment
        fields = ('name', 'alias', 'is_active', 'fallback', 'order')

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        fallback_queryset = Environment.objects.non_base()

        environment = kwargs.get('instance')  # type: Environment

        if environment:
            fallback_queryset = fallback_queryset.exclude(pk=environment.pk)
            self.fields['order'].required = True

        self.fields['fallback'].queryset = fallback_queryset

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('name'),
            Field('alias'),
            Field('is_active'),
            Field('fallback'),
            Field('order'),
            ButtonHolder(
                Submit('save', _('Save')),
                Back(reverse('environments'))
            )
        )
