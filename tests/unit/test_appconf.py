# from django.test import TestCase, override_settings
#
# from configfactory.appconf import appsettings
# from configfactory.models import AppSettings
#
#
# @override_settings(APP_SETTINGS_DEFAULTS={
#     'secured_keys': ['pass', 'token'],
#     'secured_mask': '***'
# })
# class AppSettingsProxyTestCase(TestCase):
#
#     def test_default_settings(self):
#
#         assert appsettings.SECURED_KEYS == ['pass', 'token']
#         assert appsettings.SECURED_MASK == '***'
#
#     @override_settings(CACHES={
#         'default': {
#             'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         }
#     })
#     def test_update_database_app_settings(self):
#
#         settings_obj = AppSettings.objects.get()
#         settings_obj.secured_keys = ['one', 'two']
#         settings_obj.secured_mask = '**'
#         settings_obj.save()
#
#         assert appsettings.SECURED_KEYS == ['one', 'two']
#         assert appsettings.SECURED_MASK == '**'
