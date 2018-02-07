from django.contrib.auth.views import (
    LoginView as BaseLoginView,
    LogoutView as BaseLogoutView,
)

from configfactory.forms.auth import LoginForm


class LoginView(BaseLoginView):

    template_name = 'login.html'

    form_class = LoginForm

    redirect_authenticated_user = True


class LogoutView(BaseLogoutView):
    next_page = 'login'
