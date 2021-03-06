from typing import Type, Union

from django.contrib import messages
from django.contrib.auth import get_permission_codename
from django.contrib.auth.models import Group
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView

from configfactory.forms.api_settings import APISettingsForm
from configfactory.mixins import SuperuserRequiredMixin
from configfactory.models import APISettings, Component, Environment, User
from configfactory.services.permissions import (
    get_permissions,
    update_permission,
)


class UserOrGroupAccessMixin:

    template_layout_name = None

    user_or_group_model: Type[Union[Group, User]] = None

    user_or_group_param: str = None


@method_decorator(csrf_exempt, name='dispatch')
class PermissionsView(UserOrGroupAccessMixin, SuperuserRequiredMixin, View):

    template_name = 'access/permissions.html'

    object_model: Model = None

    paginate_by = 25

    def dispatch(self, request, *args, **kwargs):
        if isinstance(self.user_or_group, User) and self.user_or_group.is_superuser:
            return redirect('update_user', pk=self.user_or_group.pk)
        return super().dispatch(request, *args, **kwargs)

    @cached_property
    def user_or_group(self) -> Union[User, Group]:
        return get_object_or_404(self.user_or_group_model, pk=self.kwargs['pk'])

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

        user_or_group = self.user_or_group
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

        permissions = get_permissions(user_or_group, page_obj.object_list)

        opts = self.object_model._meta
        perm_view = get_permission_codename('view', opts)
        perm_change = get_permission_codename('change', opts)
        perm_delete = get_permission_codename('delete', opts)

        return render(request, self.template_name, {
            'template_layout_name': self.template_layout_name,
            self.user_or_group_param: user_or_group,
            'user_or_group': user_or_group,
            'object_name': self.object_model._meta.verbose_name,
            'object_name_plural': self.object_model._meta.verbose_name_plural,
            'page_obj': page_obj,
            'perm_view': perm_view,
            'perm_change': perm_change,
            'perm_delete': perm_delete,
            'permissions': permissions,
            'search': search
        })

    def post(self, request, **kwargs):

        success = False
        object_id = None
        perm = None
        action = None
        queryset = self.get_obj_queryset()

        try:
            object_id = int(request.POST['object_id'])
            action = request.POST['action']
            perm = request.POST['perm']
        except (KeyError, ValueError):
            pass

        obj = get_object_or_404(queryset, pk=object_id)

        if action in ['assign', 'remove']:

            update_permission(
                user_or_group=self.user_or_group,
                obj=obj,
                perm=perm,
                action=action
            )

            success = True

        return JsonResponse(data={
            'success': success
        })


class EnvironmentPermissionsView(PermissionsView):

    object_model = Environment


class ComponentPermissionsView(PermissionsView):

    object_model = Component


class APISettingsView(UserOrGroupAccessMixin, SuperuserRequiredMixin, UpdateView):

    template_name = 'access/api_settings.html'

    form_class = APISettingsForm

    success_url = '.'

    @cached_property
    def user_or_group(self):
        return get_object_or_404(self.user_or_group_model, pk=self.kwargs['pk'])

    def get_object(self, queryset=None):
        try:
            return self.user_or_group.api_settings
        except APISettings.DoesNotExist:
            api_settings = APISettings()
            if isinstance(self.user_or_group, User):
                api_settings.user = self.user_or_group
            else:
                api_settings.group = self.user_or_group
            api_settings.save()
            return api_settings

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'template_layout_name': self.template_layout_name,
            'user_or_group': self.user_or_group,
            self.user_or_group_param: self.user_or_group
        })
        return context

    def form_valid(self, form):

        response = super().form_valid(form)

        if form.has_changed():

            messages.success(
                self.request,
                _('%(name)s API settings was successfully updated.') % {
                    'name': str(self.user_or_group),
                }
            )

        return response
