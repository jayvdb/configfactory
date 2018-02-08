from django.urls import path

from configfactory.api.views import (
    ComponentsAPIView,
    ComponentSettingsAPIView,
    EnvironmentsAPIView,
)

urlpatterns = [

    path('',
         view=EnvironmentsAPIView.as_view(),
         name='api_environments'),

    path('<environment>/',
         view=ComponentsAPIView.as_view(),
         name='api_components'),

    path('<environment>/<alias>/',
         view=ComponentSettingsAPIView.as_view(),
         name='api_component_settings'),
]
