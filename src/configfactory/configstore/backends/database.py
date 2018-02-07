from typing import Optional

from configfactory.models import Config

from .base import ConfigStoreBackend


class DatabaseConfigStore(ConfigStoreBackend):

    def all_data(self) -> dict:
        settings = {}
        for config in Config.objects.all():
            if config.environment not in settings:
                settings[config.environment] = {}
            settings[config.environment][config.component] = config.data
        return settings

    def get_data(self, environment: str, component: str) -> Optional[dict]:
        try:
            config = Config.objects.get(
                component=component,
                environment=environment
            )
            return config.data
        except Config.DoesNotExist:
            return None

    def update_data(self, environment: str, component: str, data: dict):
        config, created = Config.objects.get_or_create(
            environment=environment,
            component=component,
        )
        config.data = data
        config.save(update_fields=['data'])

    def delete_data(self, environment: str, component: str):
        Config.objects.filter(
            environment=environment,
            component=component
        ).delete()
