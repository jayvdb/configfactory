from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from configfactory.forms.environment import EnvironmentForm
from configfactory.mixins import SuperuserRequiredMixin
from configfactory.models import Environment
from configfactory.signals import (
    environment_created,
    environment_deleted,
    environment_updated,
)
from configfactory.utils.db import model_to_dict


class EnvironmentListView(SuperuserRequiredMixin, ListView):

    template_name = 'environments/list.html'

    queryset = Environment.objects.all()

    context_object_name = 'environments'

    paginate_by = 25


class EnvironmentCreateView(SuperuserRequiredMixin, CreateView):

    template_name = 'environments/create.html'

    queryset = Environment.objects.all()

    form_class = EnvironmentForm

    success_url = reverse_lazy('environments')

    def form_valid(self, form):

        response = super().form_valid(form)
        environment = self.object  # type: Environment

        # Notify about created environment
        environment_created.send(
            sender=Environment,
            environment=environment,
            fields=self.form_class.Meta.fields,
            user=self.request.user
        )

        messages.success(
            self.request,
            _('%(name)s environment was successfully created.') % {
                'name': environment.name,
            }
        )

        return response


class EnvironmentUpdateView(SuperuserRequiredMixin, UpdateView):

    template_name = 'environments/update.html'

    queryset = Environment.objects.non_base()

    form_class = EnvironmentForm

    slug_url_kwarg = 'alias'

    slug_field = 'alias'

    success_url = reverse_lazy('environments')

    def form_valid(self, form):

        fields = self.form_class.Meta.fields

        old_data = model_to_dict(self.object, fields=fields)

        response = super().form_valid(form)

        environment = self.object  # type: Environment

        # Notify about updated environment
        environment_updated.send(
            sender=Environment,
            environment=environment,
            fields=fields,
            old_data=old_data,
            user=self.request.user
        )

        messages.success(
            self.request,
            _('%(name)s environment was successfully updated.') % {
                'name': environment.name,
            }
        )

        return response


class EnvironmentDeleteView(SuperuserRequiredMixin, DeleteView):

    template_name = 'environments/delete.html'

    queryset = Environment.objects.non_base()

    slug_url_kwarg = 'alias'

    slug_field = 'alias'

    success_url = reverse_lazy('environments')

    def delete(self, request, *args, **kwargs):

        response = super().delete(request, *args, **kwargs)

        environment = self.object  # type: Environment

        # Notify about deleted environment
        environment_deleted.send(
            sender=Environment,
            environment=environment,
            user=self.request.user
        )

        messages.success(
            self.request,
            _('%(name)s environment was successfully deleted.') % {
                'name': environment.name,
            }
        )

        return response
