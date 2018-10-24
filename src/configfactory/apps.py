from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import ugettext_lazy as _

from configfactory.management import (
    create_default_environments,
    create_default_users,
)


class ConfigFactoryConfig(AppConfig):

    name = 'configfactory'

    verbose_name = _("ConfigFactory")

    def ready(self):

        # Create default models
        post_migrate.connect(create_default_users, sender=self)
        post_migrate.connect(create_default_environments, sender=self)

        # Run project autodiscover
        self.module.autodiscover()
