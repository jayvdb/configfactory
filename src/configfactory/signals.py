from django.dispatch import Signal

group_created = Signal(providing_args=['group'])
group_updated = Signal(providing_args=['group', 'old_data'])
group_deleted = Signal(providing_args=['group'])

user_created = Signal(providing_args=['user'])
user_updated = Signal(providing_args=['user', 'old_data'])
user_deleted = Signal(providing_args=['user'])

environment_created = Signal(providing_args=['environment'])
environment_updated = Signal(providing_args=['environment', 'old_data'])
environment_deleted = Signal(providing_args=['environment'])

component_created = Signal(providing_args=['component'])
component_updated = Signal(providing_args=['component', 'old_data'])
component_alias_changed = Signal(providing_args=['component', 'old_alias', 'new_alias'])
component_deleted = Signal(providing_args=['component', 'user'])

settings_updated = Signal(providing_args=['component', 'environment', 'old_settings', 'new_settings'])

backup_created = Signal(providing_args=['backup'])
backup_loaded = Signal(providing_args=['backup'])
backups_cleaned = Signal()
