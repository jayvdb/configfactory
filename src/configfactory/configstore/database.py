from configfactory.models import Config

from .base import AllData, ConfigStore


class DatabaseConfigStore(ConfigStore):

    def get_all_data(self) -> AllData:
        data: AllData = {}
        for config in Config.objects.all():
            if config.environment not in data:
                data[config.environment] = {}
            data[config.environment][config.component] = config.data
        return data

    def update_data(self, environment: str, component: str, data: str):
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
