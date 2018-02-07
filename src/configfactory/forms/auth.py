from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _


class LoginForm(AuthenticationForm):

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {
            'autocomplete': 'off'
        }
        self.helper.form_show_errors = False
        login_button = Submit('login', _('Login'))
        login_button.field_classes = 'btn btn-primary btn-block'
        self.helper.layout = Layout(
            Field('username', autocomplete='off'),
            Field('password', autocomplete='off'),
            login_button,
        )
