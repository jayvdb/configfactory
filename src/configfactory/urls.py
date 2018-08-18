from django.conf import settings
from django.urls import include, path

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
    GroupAPISettingsView,
    GroupComponentPermissionsView,
    GroupCreateView,
    GroupDeleteView,
    GroupEnvironmentPermissionsView,
    GroupListView,
    GroupUpdateView,
)
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

    path('',
         view=DashboardView.as_view(),
         name='dashboard'),

    path('login/',
         view=LoginView.as_view(),
         name='login'),

    path('logout/',
         view=LogoutView.as_view(),
         name='logout'),

    path('profile/',
         view=ProfileUpdateView.as_view(),
         name='profile'),

    path('profile/change_password/',
         view=ProfileChangePasswordView.as_view(),
         name='change_password'),

    path('environments/',
         view=EnvironmentListView.as_view(),
         name='environments'),

    path('environments/create/',
         view=EnvironmentCreateView.as_view(),
         name='create_environment'),

    path('environments/<alias>/',
         view=EnvironmentUpdateView.as_view(),
         name='update_environment'),

    path('environments/<alias>/delete/',
         view=EnvironmentDeleteView.as_view(),
         name='delete_environment'),

    path('components/create/',
         view=ComponentCreateView.as_view(),
         name='create_component'),

    path('components/<alias>/',
         view=ComponentSettingsRedirectView.as_view(),
         name='component'),

    path('components/<alias>/edit/',
         view=ComponentUpdateView.as_view(),
         name='edit_component'),

    path('components/<alias>/edit/schema/',
         view=ComponentSchemaUpdateView.as_view(),
         name='edit_component_schema'),

    path('components/<alias>/delete/',
         view=ComponentDeleteView.as_view(),
         name='delete_component'),

    path('components/<alias>/<environment>/',
         view=ComponentSettingsView.as_view(),
         name='component_settings'),

    path('components/<alias>/<environment>/edit/',
         view=ComponentSettingsUpdateView.as_view(),
         name='update_component_settings'),

    path('backups/',
         view=BackupListView.as_view(),
         name='backups'),

    path('backups/dump/',
         view=BackupCreateView.as_view(),
         name='dump_backup'),

    path('backups/import/',
         view=BackupImportView.as_view(),
         name='import_backup'),

    path('backups/<int:pk>/load/',
         view=BackupLoadView.as_view(),
         name='load_backup'),

    path('backups/<int:pk>/export/',
         view=BackupExportView.as_view(),
         name='export_backup'),

    path('backups/<int:pk>/delete/',
         view=BackupDeleteView.as_view(),
         name='delete_backup'),

    path('logs/',
         view=LogEntryListView.as_view(),
         name='logs'),

    path('logs/<int:pk>/',
         view=LogEntryDetailView.as_view(),
         name='log'),

    path('users/',
         view=UserListView.as_view(),
         name='users'),

    path('users/create/',
         view=UserCreateView.as_view(),
         name='create_user'),

    path('users/<int:pk>/',
         view=UserUpdateView.as_view(),
         name='update_user'),

    path('users/<int:pk>/change_password/',
         view=UserChangePasswordView.as_view(),
         name='change_user_password'),

    path('users/<int:pk>/delete/',
         view=UserDeleteView.as_view(),
         name='delete_user'),

    path('groups/',
         view=GroupListView.as_view(),
         name='groups'),

    path('groups/create/',
         view=GroupCreateView.as_view(),
         name='create_group'),

    path('groups/<int:pk>/',
         view=GroupUpdateView.as_view(),
         name='update_group'),

    path('groups/<int:pk>/delete/',
         view=GroupDeleteView.as_view(),
         name='delete_group'),

    path('groups/<int:pk>/environments/',
         view=GroupEnvironmentPermissionsView.as_view(),
         name='group_environments'),

    path('groups/<int:pk>/components/',
         view=GroupComponentPermissionsView.as_view(),
         name='group_components'),

    path('groups/<int:pk>/api_settings/',
         view=GroupAPISettingsView.as_view(),
         name='group_api_settings'),

    path('api/', include('configfactory.api.urls')),
]

if settings.DEBUG:

    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls))
    ] + urlpatterns
