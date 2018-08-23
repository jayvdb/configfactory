from django.apps import AppConfig, apps
from django.db.models.signals import class_prepared, post_migrate, pre_init
from django.utils.translation import ugettext_lazy as _

from configfactory.management import create_default_users, create_default_environments
from configfactory.utils.db import set_db_table


class ConfigFactoryConfig(AppConfig):

    name = 'configfactory'
    verbose_name = _("ConfigFactory")

    def ready(self):

        self._rename_db_tables()

        post_migrate.connect(create_default_users, sender=self)
        post_migrate.connect(create_default_environments, sender=self)

        # Run project autodiscover
        self.module.autodiscover()

    def _rename_db_tables(self):
        pass

        # for model in apps.get_models():
        #     set_db_table(model)
        #
        # pre_init.connect(set_db_table)
        # class_prepared.connect(set_db_table)
