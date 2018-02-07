from django.conf.urls import url

from configfactory.api.views import (
    ComponentsAPIView,
    ComponentSettingsAPIView,
    EnvironmentsAPIView,
)

urlpatterns = [

    url(r'^$',
        view=EnvironmentsAPIView.as_view(),
        name='api_environments'),

    url(r'^(?P<environment>\w+)/$',
        view=ComponentsAPIView.as_view(),
        name='api_components'),

    url(r'^(?P<environment>\w+)/(?P<alias>[-\w\d]+)/$',
        view=ComponentSettingsAPIView.as_view(),
        name='api_component_settings'),
]
