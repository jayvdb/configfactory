from django.contrib import messages
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from configfactory.forms.group import GroupForm
from configfactory.mixins import SuperuserRequiredMixin
from configfactory.signals import group_created, group_deleted, group_updated
from configfactory.utils.db import model_to_dict
from configfactory.views.access import (
    APISettingsView,
    ComponentPermissionsView,
    EnvironmentPermissionsView,
)


class GroupListView(SuperuserRequiredMixin, ListView):

    template_name = 'groups/list.html'

    queryset = Group.objects.order_by('name')

    context_object_name = 'groups'

    paginate_by = 25


class GroupCreateView(SuperuserRequiredMixin, CreateView):

    template_name = 'groups/create.html'

    queryset = Group.objects.all()

    form_class = GroupForm

    context_object_name = 'group'

    success_url = reverse_lazy('groups')

    def form_valid(self, form):

        response = super().form_valid(form)
        group = self.object  # type: Group

        # Notify about created group
        group_created.send(
            sender=Group,
            group=group,
            fields=self.form_class.Meta.fields,
            user=self.request.user
        )

        messages.success(
            self.request,
            _('%(name)s group was successfully created.') % {
                'name': group.name,
            }
        )

        return response


class GroupUpdateView(SuperuserRequiredMixin, UpdateView):

    template_name = 'groups/update.html'

    queryset = Group.objects.all()

    form_class = GroupForm

    context_object_name = 'group'

    success_url = reverse_lazy('groups')

    def form_valid(self, form):

        fields = self.form_class.Meta.fields

        old_data = model_to_dict(self.object, fields=fields)

        response = super().form_valid(form)

        group = self.object  # type: Group

        # Notify about updated group
        group_updated.send(
            sender=Group,
            group=group,
            fields=fields,
            old_data=old_data,
            user=self.request.user
        )

        messages.success(
            self.request,
            _('%(name)s group was successfully updated.') % {
                'name': group.name,
            }
        )

        return response


class GroupDeleteView(SuperuserRequiredMixin, DeleteView):

    template_name = 'groups/delete.html'

    queryset = Group.objects.all()

    context_object_name = 'group'

    success_url = reverse_lazy('groups')

    def delete(self, request, *args, **kwargs):

        response = super().delete(request, *args, **kwargs)

        group = self.object

        # Notify about deleted group
        group_deleted.send(
            sender=Group,
            group=group,
            user=self.request.user
        )

        messages.success(
            self.request,
            _('%(name)s group was successfully deleted.') % {
                'name': group.name,
            }
        )

        return response


class GroupEnvironmentPermissionsView(EnvironmentPermissionsView):
    pass


class GroupComponentPermissionsView(ComponentPermissionsView):
    pass


class GroupAPISettingsView(APISettingsView):
    pass
