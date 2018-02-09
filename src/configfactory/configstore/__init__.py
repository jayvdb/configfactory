from configfactory.configstore.base import ConfigStore

from .base import ConfigStore

# Set default config store
_instance = ConfigStore.configure()
backend = _instance.backend
cachecontext = _instance.cachecontext
all_data = _instance.all
env = _instance.env
get = _instance.get
update = _instance.update
delete = _instance.delete
normalize = _instance.normalize
ikeys = _instance.ikeys
