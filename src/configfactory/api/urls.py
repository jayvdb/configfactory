from django.urls import path

from configfactory.api import views

app_name = 'api'

urlpatterns = [

    path('',
         view=views.EnvironmentsAPIView.as_view(),
         name='environments'),

    path('<environment>/',
         view=views.SettingsJsonAPIView.as_view(),
         name='settings'),

    path('<environment>/json/',
         view=views.SettingsJsonAPIView.as_view(),
         name='settings_json'),

    path('<environment>/dotenv/',
         view=views.SettingsDotEnvAPIView.as_view(),
         name='settings_dotenv'),
]
