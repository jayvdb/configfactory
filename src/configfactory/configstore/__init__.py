from configfactory.configstore.base import ConfigStore

from .base import ConfigStore

# Set default config store
instance = ConfigStore.configure()
backend = instance.backend
cachecontext = instance.cachecontext
all = instance.all
env_settings = instance.env
get = instance.get
update = instance.update
delete = instance.delete
ikeys = instance.ikeys
