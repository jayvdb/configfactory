from django.conf import settings
from django.conf.urls import include, url

from configfactory.views.auth import LoginView, LogoutView
from configfactory.views.backups import (
    BackupCreateView,
    BackupDeleteView,
    BackupExportView,
    BackupImportView,
    BackupListView,
    BackupLoadView,
)
from configfactory.views.components import (
    ComponentCreateView,
    ComponentDeleteView,
    ComponentSchemaUpdateView,
    ComponentSettingsRedirectView,
    ComponentSettingsUpdateView,
    ComponentSettingsView,
    ComponentUpdateView,
)
from configfactory.views.default import DashboardView
from configfactory.views.environments import (
    EnvironmentCreateView,
    EnvironmentDeleteView,
    EnvironmentListView,
    EnvironmentUpdateView,
)
from configfactory.views.groups import (
    GroupComponentPermissionsView,
    GroupCreateView,
    GroupDeleteView,
    GroupEnvironmentPermissionsView,
    GroupListView,
    GroupUpdateView,
    GroupAPISettingsView)
from configfactory.views.logs import LogEntryDetailView, LogEntryListView
from configfactory.views.profile import (
    ProfileChangePasswordView,
    ProfileUpdateView,
)
from configfactory.views.users import (
    UserChangePasswordView,
    UserCreateView,
    UserDeleteView,
    UserListView,
    UserUpdateView,
)

urlpatterns = [

    url(r'^$',
        view=DashboardView.as_view(),
        name='dashboard'),

    url(r'^login/$',
        view=LoginView.as_view(),
        name='login'),

    url(r'^logout/$',
        view=LogoutView.as_view(),
        name='logout'),

    url(r'^profile/$',
        view=ProfileUpdateView.as_view(),
        name='profile'),

    url(r'^profile/change_password/$',
        view=ProfileChangePasswordView.as_view(),
        name='change_password'),

    url(r'^environments/$',
        view=EnvironmentListView.as_view(),
        name='environments'),

    url(r'^environments/create/$',
        view=EnvironmentCreateView.as_view(),
        name='create_environment'),

    url(r'^environments/(?P<alias>[-\w\d]+)/$',
        view=EnvironmentUpdateView.as_view(),
        name='update_environment'),

    url(r'^environments/(?P<alias>[-\w\d]+)/delete/$',
        view=EnvironmentDeleteView.as_view(),
        name='delete_environment'),

    url(r'^components/create/$',
        view=ComponentCreateView.as_view(),
        name='create_component'),

    url(r'^components/(?P<alias>[-\w\d]+)/$',
        view=ComponentSettingsRedirectView.as_view(),
        name='component'),

    url(r'^components/(?P<alias>[-\w\d]+)/edit/$',
        view=ComponentUpdateView.as_view(),
        name='edit_component'),

    url(r'^components/(?P<alias>[-\w\d]+)/edit/schema/$',
        view=ComponentSchemaUpdateView.as_view(),
        name='edit_component_schema'),

    url(r'^components/(?P<alias>[-\w\d]+)/delete/$',
        view=ComponentDeleteView.as_view(),
        name='delete_component'),

    url(r'^components/(?P<alias>[-\w\d]+)/(?P<environment>[-\w\d]+)/$',
        view=ComponentSettingsView.as_view(),
        name='component_settings'),

    url(r'^components/(?P<alias>[-\w\d]+)/(?P<environment>[-\w\d]+)/edit/$',
        view=ComponentSettingsUpdateView.as_view(),
        name='update_component_settings'),

    url(r'^backups/$',
        view=BackupListView.as_view(),
        name='backups'),

    url(r'^backups/dump/$',
        view=BackupCreateView.as_view(),
        name='dump_backup'),

    url(r'^backups/import/$',
        view=BackupImportView.as_view(),
        name='import_backup'),

    url(r'^backups/(?P<pk>\d+)/load/$',
        view=BackupLoadView.as_view(),
        name='load_backup'),

    url(r'^backups/(?P<pk>\d+)/export/$',
        view=BackupExportView.as_view(),
        name='export_backup'),

    url(r'^backups/(?P<pk>\d+)/delete/$',
        view=BackupDeleteView.as_view(),
        name='delete_backup'),

    url(r'^logs/$',
        view=LogEntryListView.as_view(),
        name='logs'),

    url(r'^logs/(?P<pk>\d+)/$',
        view=LogEntryDetailView.as_view(),
        name='log'),

    url(r'^users/$',
        view=UserListView.as_view(),
        name='users'),

    url(r'^users/create/$',
        view=UserCreateView.as_view(),
        name='create_user'),

    url(r'^users/(?P<pk>\d+)/$',
        view=UserUpdateView.as_view(),
        name='update_user'),

    url(r'^users/(?P<pk>\d+)/change_password/$',
        view=UserChangePasswordView.as_view(),
        name='change_user_password'),

    url(r'^users/(?P<pk>\d+)/delete/$',
        view=UserDeleteView.as_view(),
        name='delete_user'),

    url(r'^groups/$',
        view=GroupListView.as_view(),
        name='groups'),

    url(r'^groups/create/$',
        view=GroupCreateView.as_view(),
        name='create_group'),

    url(r'^groups/(?P<pk>\d+)/$',
        view=GroupUpdateView.as_view(),
        name='update_group'),

    url(r'^groups/(?P<pk>\d+)/delete/$',
        view=GroupDeleteView.as_view(),
        name='delete_group'),

    url(r'^groups/(?P<pk>\d+)/environments/$',
        view=GroupEnvironmentPermissionsView.as_view(),
        name='group_environments'),

    url(r'^groups/(?P<pk>\d+)/components/$',
        view=GroupComponentPermissionsView.as_view(),
        name='group_components'),

    url(r'^groups/(?P<pk>\d+)/api_settings/$',
        view=GroupAPISettingsView.as_view(),
        name='group_api_settings'),

    url(r'^api/', include('configfactory.api.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
