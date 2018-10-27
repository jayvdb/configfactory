from django.contrib import messages
from django.contrib.auth import password_validation
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from configfactory.forms.user import (
    UserAccessForm,
    UserForm,
    UserSetPasswordForm,
)
from configfactory.mixins import SuperuserRequiredMixin
from configfactory.models import User
from configfactory.signals import user_created, user_deleted, user_updated
from configfactory.utils.db import model_to_dict
from configfactory.views.access import (
    APISettingsView,
    ComponentPermissionsView,
    EnvironmentPermissionsView,
)


class UserListView(SuperuserRequiredMixin, ListView):

    template_name = 'users/list.html'

    context_object_name = 'users'

    paginate_by = 25

    def get_queryset(self):
        return User.objects.exclude(
            pk=self.request.user.pk
        ).order_by('username')


class UserCreateView(SuperuserRequiredMixin, CreateView):

    template_name = 'users/create.html'

    queryset = User.objects.all()

    form_class = UserForm

    context_object_name = 'user'

    success_url = reverse_lazy('users')

    def form_valid(self, form):

        response = super().form_valid(form)

        user = self.object  # type: User

        # Notify about created user
        user_created.send(
            sender=User,
            user=user,
            fields=self.form_class.Meta.fields,
            current_user=self.request.user
        )

        messages.success(
            self.request,
            _('%(name)s user was successfully created.') % {
                'name': user,
            }
        )

        return response


class UserUpdateView(SuperuserRequiredMixin, UpdateView):

    template_name = 'users/update.html'

    queryset = User.objects.all()

    form_class = UserForm

    context_object_name = 'user'

    success_url = reverse_lazy('users')

    def form_valid(self, form):

        fields = self.form_class.Meta.fields

        old_data = model_to_dict(self.object, fields=fields)

        response = super().form_valid(form)

        user: User = self.object

        # Notify about updated user
        user_updated.send(
            sender=User,
            user=user,
            fields=fields,
            old_data=old_data,
            current_user=self.request.user
        )

        messages.success(
            self.request,
            _('%(name)s user was successfully updated.') % {
                'name': user,
            }
        )

        return response


class UserAccessUpdateView(UserUpdateView):

    template_name = 'users/update.html'

    form_class = UserAccessForm


class UserDeleteView(SuperuserRequiredMixin, DeleteView):

    template_name = 'users/delete.html'

    queryset = User.objects.all()

    context_object_name = 'user'

    success_url = reverse_lazy('users')

    def delete(self, request, *args, **kwargs):

        response = super().delete(request, *args, **kwargs)

        user = self.object  # type: User

        # Notify about deleted user
        user_deleted.send(
            sender=User,
            user=user,
            current_user=self.request.user
        )

        messages.success(
            self.request,
            _('%(name)s was successfully deleted.') % {
                'name': user,
            }
        )

        return response


class UserChangePasswordView(SuperuserRequiredMixin, UpdateView):

    template_name = 'users/change_password.html'

    queryset = User.objects.all()

    form_class = UserSetPasswordForm

    success_url = reverse_lazy('users')

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
        kwargs['user'] = self.object
        return kwargs


class UserAccessMixin:

    template_layout_name = 'users/layouts/edit.html'

    user_or_group_model = User

    user_or_group_param = 'user'


class UserEnvironmentPermissionsView(UserAccessMixin, EnvironmentPermissionsView):
    pass


class UserComponentPermissionsView(UserAccessMixin, ComponentPermissionsView):
    pass


class UserAPISettingsView(UserAccessMixin, APISettingsView):
    pass
