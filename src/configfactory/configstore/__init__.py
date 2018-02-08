from configfactory.configstore.base import ConfigStore

from .base import ConfigStore

# Set default config store
instance = ConfigStore.configure()
backend = instance.backend
cachecontext = instance.cachecontext
all_settings = instance.all_settings
env_settings = instance.env_settings
get_settings = instance.get_settings
update_settings = instance.update_settings
delete_settings = instance.delete_settings
inject_keys = instance.inject_keys
