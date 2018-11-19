from django.urls import path

from configfactory.api.views import EnvironmentsAPIView, SettingsAPIView

app_name = 'api'

urlpatterns = [

    path('',
         view=EnvironmentsAPIView.as_view(),
         name='environments'),

    path('<environment>/',
         view=SettingsAPIView.as_view(),
         name='settings'),

    path('<environment>.<format>',
         view=SettingsAPIView.as_view(),
         name='settings_format'),
]
