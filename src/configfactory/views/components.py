from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    RedirectView,
    UpdateView,
)
from guardian.core import ObjectPermissionChecker

from configfactory.exceptions import ComponentDeleteError
from configfactory.forms.component import (
    ComponentForm,
    ComponentSchemaForm,
    ComponentSettingsForm,
)
from configfactory.mixins import ConfigStoreCachedMixin
from configfactory.models import Component
from configfactory.services.components import delete_component
from configfactory.services.configsettings import (
    get_settings,
    inject_settings_params,
    update_settings,
)
from configfactory.shortcuts import get_base_environment
from configfactory.signals import (
    component_created,
    component_updated,
    settings_updated,
)
from configfactory.utils import dicthelper, security
from configfactory.utils.db import model_to_dict


class ComponentCreateView(LoginRequiredMixin, ConfigStoreCachedMixin, CreateView):

    template_name = 'components/create.html'

    queryset = Component.objects.all()

    form_class = ComponentForm

    success_url = reverse_lazy('components')

    def get_success_url(self):
        return reverse('component', kwargs={
            'alias': self.object.alias
        })

    def form_valid(self, form):

        response = super().form_valid(form)

        component = self.object  # type: Component

        component_created.send(
            sender=Component,
            component=component,
            fields=self.form_class.Meta.fields,
            user=self.request.user
        )

        messages.success(
            self.request,
            _('%(name)s component was successfully created.') % {
                'name': component.name,
            }
        )

        return response


class ComponentUpdateView(LoginRequiredMixin, ConfigStoreCachedMixin, UpdateView):

    template_name = 'components/update.html'

    form_class = ComponentForm

    slug_field = 'alias'

    slug_url_kwarg = 'alias'

    context_object_name = 'component'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_data = {}

    def get_queryset(self):
        return self.request.components

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        self.old_data = model_to_dict(obj, fields=self.form_class.Meta.fields)
        return obj

    def get_success_url(self):
        component: Component = self.object
        return reverse('component', kwargs={
            'alias': component.alias
        })

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):

        fields = self.form_class.Meta.fields

        response = super().form_valid(form)

        component: Component = self.object

        component_updated.send(
            sender=Component,
            component=component,
            old_data=self.old_data,
            user=self.request.user,
            fields=fields
        )

        messages.success(
            self.request,
            _('%(name)s component was successfully updated.') % {
                'name': component.name,
            }
        )

        return response


class ComponentSchemaUpdateView(LoginRequiredMixin, UpdateView):

    template_name = 'components/update_schema.html'

    form_class = ComponentSchemaForm

    slug_field = 'alias'

    slug_url_kwarg = 'alias'

    context_object_name = 'component'

    success_url = '.'

    def get_queryset(self):
        return self.request.components

    def get_form_kwargs(self):
        component: Component = self.object
        kwargs = super().get_form_kwargs()
        kwargs.pop('instance')
        kwargs['initial'] = {
            'schema': component.schema
        }
        return kwargs

    def form_valid(self, form):

        component: Component = self.object

        old_data = {
            'schema': component.schema
        }

        component.schema = form.cleaned_data['schema']
        component.save()

        component_updated.send(
            sender=Component,
            component=component,
            old_data=old_data,
            new_data={
                'schema': component.schema
            },
            user=self.request.user
        )

        messages.success(
            self.request,
            _('%(name)s component schema was successfully updated.') % {
                'name': component.name,
            }
        )

        return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form):
        messages.error(
            self.request,
            form.errors.as_text(),
            extra_tags=' alert-danger'
        )
        return super().form_invalid(form)


class ComponentDeleteView(LoginRequiredMixin, ConfigStoreCachedMixin, DeleteView):

    template_name = 'components/delete.html'

    slug_field = 'alias'

    slug_url_kwarg = 'alias'

    context_object_name = 'component'

    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        return self.request.components

    def delete(self, request, *args, **kwargs):

        component = self.get_object()

        try:
            delete_component(component, user=request.user)
        except ComponentDeleteError as e:
            messages.error(request, str(e), extra_tags=' alert-danger')
            return HttpResponseRedirect(
                reverse(
                    'delete_component',
                    kwargs={
                        'alias': component.alias
                    }
                )
            )

        messages.success(
            self.request,
            _('%(name)s component was successfully deleted.') % {
                'name': component.name,
            }
        )

        return HttpResponseRedirect(self.success_url)


class ComponentSettingsRedirectView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse('component_settings', kwargs={
            'alias': kwargs['alias'],
            'environment': get_base_environment()
        })


class ComponentSettingsView(LoginRequiredMixin, ConfigStoreCachedMixin, DetailView):

    template_name = 'components/settings.html'

    slug_field = 'alias'

    slug_url_kwarg = 'alias'

    context_object_name = 'component'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return response

    def get_queryset(self):
        return self.request.components

    def get_context_data(self, **kwargs):

        data = super().get_context_data(**kwargs)

        component = self.object  # type: Component
        environment = get_object_or_404(
            klass=self.request.view_environments,
            alias=self.kwargs['environment']
        )

        settings_dict = security.cleanse(
            data=get_settings(
                environment=environment,
                component=component,
            ),
            hidden=settings.SECURE_KEYS,
        )

        settings_dict = dicthelper.flatten(settings_dict)
        settings_dict = inject_settings_params(
            environment=environment,
            data=settings_dict,
            components=self.request.components,
            strict=False
        )

        form = ComponentSettingsForm(
            component=component,
            environment=environment,
            initial={
                'settings': settings_dict
            }
        )

        checker = ObjectPermissionChecker(self.request.user)
        component_perms = checker.get_perms(component)
        environment_perms = checker.get_perms(environment)

        data.update({
            'current_environment': environment,
            'settings': settings_dict,
            'form': form,
            'component_perms': component_perms,
            'environment_perms': environment_perms
        })

        return data


class ComponentSettingsUpdateView(LoginRequiredMixin, ConfigStoreCachedMixin, UpdateView):

    template_name = 'components/update_settings.html'

    form_class = ComponentSettingsForm

    slug_field = 'alias'

    slug_url_kwarg = 'alias'

    context_object_name = 'component'

    success_url = '.'

    def get_queryset(self):
        return self.request.components

    @cached_property
    def environment(self):
        return get_object_or_404(
            klass=self.request.change_environments,
            alias=self.kwargs['environment']
        )

    @cached_property
    def settings_dict(self):
        return get_settings(
            environment=self.environment,
            component=self.object,
        )

    def get_context_data(self, **kwargs):

        data = super().get_context_data(**kwargs)

        checker = ObjectPermissionChecker(self.request.user)
        component_perms = checker.get_perms(self.object)
        environment_perms = checker.get_perms(self.environment)

        data.update({
            'current_environment': self.environment,
            'settings': self.settings_dict,
            'component_perms': component_perms,
            'environment_perms': environment_perms,
        })

        return data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop('instance')
        kwargs.update({
            'component': self.object,
            'environment': self.environment,
            'initial': {
                'settings': self.settings_dict
            }
        })
        return kwargs

    def form_valid(self, form):

        component: Component = self.object

        old_settings = get_settings(
            environment=self.environment,
            component=component,
        )

        new_settings = form.cleaned_data['settings']

        # Update store settings
        update_settings(
            environment=self.environment,
            component=component,
            data=new_settings,
            validate=False
        )

        # Notify about updated component settings
        settings_updated.send(
            sender=Component,
            component=component,
            environment=self.environment,
            old_settings=old_settings,
            new_settings=new_settings,
            user=self.request.user
        )

        messages.success(
            self.request,
            _("Component %(component)s settings successfully updated.") % {
                'component': component.name
            }
        )

        return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, form.errors.as_text(), extra_tags=' alert-danger')
        return response
