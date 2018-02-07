from django.contrib import messages
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import assign_perm, remove_perm

from configfactory.forms.api_settings import APISettingsForm
from configfactory.forms.group import GroupForm
from configfactory.mixins import SuperuserRequiredMixin
from configfactory.models import APISettings, Component, Environment
from configfactory.signals import group_created, group_deleted, group_updated
from configfactory.utils.db import model_to_dict


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


@method_decorator(csrf_exempt, name='dispatch')
class GroupPermissionsView(SuperuserRequiredMixin, View):

    template_name = 'groups/permissions.html'

    object_model = None  # type: Model

    paginate_by = 25

    perm_view = None

    perm_change = None

    perm_delete = None

    def get_obj_queryset(self):
        if self.object_model:
            return self.object_model.objects.all()
        raise ImproperlyConfigured(
            "%(cls)s is missing a QuerySet. Define "
            "%(cls)s.object_model, or override "
            "%(cls)s.get_obj_queryset()." % {
                'cls': self.__class__.__name__
            }
        )

    def get(self, request, **kwargs):

        group = get_object_or_404(Group, pk=kwargs['pk'])
        queryset = self.get_obj_queryset()

        search = None
        if 'search' in self.request.GET:
            search = self.request.GET['search']
            queryset = queryset.filter(name__icontains=search)

        paginator = Paginator(queryset, self.paginate_by)

        page = request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        object_list = page_obj.object_list

        perm_checker = ObjectPermissionChecker(group)
        perm_checker.prefetch_perms(object_list)

        return render(request, self.template_name, {
            'group': group,
            'object_model': self.object_model,
            'object_name': self.object_model._meta.verbose_name,
            'object_name_plural': self.object_model._meta.verbose_name_plural,
            'object_list': object_list,
            'page_obj': page_obj,
            'perm_checker': perm_checker,
            'perm_view': self.perm_view,
            'perm_change': self.perm_change,
            'perm_delete': self.perm_delete,
            'search': search
        })

    def post(self, request, **kwargs):

        success = False
        object_id = None
        perm = None
        action = None
        group = get_object_or_404(Group, pk=kwargs['pk'])
        queryset = self.get_obj_queryset()

        try:
            object_id = int(request.POST['object_id'])
            action = request.POST['action']
            perm = request.POST['perm']
        except (KeyError, ValueError):
            pass

        if object_id and action in ['add', 'remove']:

            obj = get_object_or_404(queryset, pk=object_id)
            content_type = ContentType.objects.get_for_model(queryset.model)

            # Get or create permission
            try:
                permission = Permission.objects.get(content_type=content_type, codename=perm)
            except Permission.DoesNotExist:
                name = perm.replace('_', '').title()
                permission = Permission.objects.create(
                    name=name,
                    content_type=content_type,
                    codename=perm
                )

            if action == 'add':
                assign_perm(permission, group, obj)
            else:
                remove_perm(permission, group, obj)
            success = True

        return JsonResponse(data={
            'success': success
        })


class GroupEnvironmentPermissionsView(GroupPermissionsView):

    object_model = Environment

    perm_view = 'view_environment'

    perm_change = 'change_environment'

    perm_delete = 'delete_environment'


class GroupComponentPermissionsView(GroupPermissionsView):

    object_model = Component

    perm_view = 'view_component'

    perm_change = 'change_component'

    perm_delete = 'delete_component'


class GroupAPISettingsView(SuperuserRequiredMixin, UpdateView):

    template_name = 'groups/api_settings.html'

    form_class = APISettingsForm

    success_url = '.'

    @cached_property
    def group(self):
        return get_object_or_404(Group, pk=self.kwargs['pk'])

    def get_object(self, queryset=None):
        try:
            return self.group.api_settings
        except APISettings.DoesNotExist:
            api_settings = APISettings()
            api_settings.group = self.group
            api_settings.save()
            return api_settings

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'group': self.group
        })
        return context

    def form_valid(self, form):

        response = super().form_valid(form)

        if form.has_changed():

            messages.success(
                self.request,
                _('%(name)s group API settings was successfully updated.') % {
                    'name': self.group.name,
                }
            )

        return response
