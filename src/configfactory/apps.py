from django.apps import AppConfig, apps
from django.db.models.signals import class_prepared, post_migrate, pre_init
from django.utils.translation import ugettext_lazy as _

from configfactory.management import (
    create_default_environments,
    create_default_users,
)
from configfactory.utils.db import rename_db_table


class ConfigFactoryConfig(AppConfig):

    name = 'configfactory'

    verbose_name = _("ConfigFactory")

    def ready(self):

        # Rename tables if it possible
        self._rename_db_tables()

        # Create default models
        post_migrate.connect(create_default_users, sender=self)
        post_migrate.connect(create_default_environments, sender=self)

        # Run project autodiscover
        self.module.autodiscover()

    @staticmethod
    def _rename_db_tables():

        for model in apps.get_models():
            rename_db_table(model)

        pre_init.connect(rename_db_table)
        class_prepared.connect(rename_db_table)
