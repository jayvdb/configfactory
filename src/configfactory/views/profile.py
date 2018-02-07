from django.contrib import messages
from django.contrib.auth import password_validation
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _
from django.views.generic import UpdateView

from configfactory.forms.profile import ProfileForm, ProfilePasswordChangeForm


class ProfileUpdateView(LoginRequiredMixin, UpdateView):

    template_name = 'profile/update.html'

    form_class = ProfileForm

    success_url = '.'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Your profile was successfully updated.'))
        return response


class ProfileChangePasswordView(LoginRequiredMixin, UpdateView):

    template_name = 'profile/change_password.html'

    form_class = ProfilePasswordChangeForm

    success_url = '.'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        password_info = password_validation.password_validators_help_text_html()
        context.update({
            'password_info': password_info
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop('instance')
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Your password was successfully changed.'))
        return response
