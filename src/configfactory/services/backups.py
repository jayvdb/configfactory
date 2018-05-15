from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone

from configfactory import configstore
from configfactory.models import Backup, Component, Environment, User
from configfactory.signals import (
    backup_created,
    backup_loaded,
    backups_cleaned,
)
from configfactory.utils import json


def create_backup(user: User = None, comment: str = None) -> Backup:

    data = {
        'environments': [],
        'components': [],
        'configs': configstore.all_data(),
    }

    for environment in Environment.objects.order_by('pk'):

        if environment.fallback_id:
            fallback = environment.fallback.alias
        else:
            fallback = None

        data['environments'].append({
            'id': environment.pk,
            'name': environment.name,
            'alias': environment.alias,
            'order': environment.order,
            'fallback': fallback,
            'is_active': environment.is_active,
            'created_at': environment.created_at,
            'updated_at': environment.updated_at,
        })

    for component in Component.objects.all():

        data['components'].append({
            'id': component.pk,
            'name': component.name,
            'alias': component.alias,
            'settings_json': component.settings_json,
            'schema_json': component.schema_json,
            'is_global': component.is_global,
            'require_schema': component.require_schema,
            'strict_keys': component.strict_keys,
            'is_active': component.is_active,
            'created_at': component.created_at,
            'updated_at': component.updated_at,
        })

    backup = Backup()
    backup.data_file.save(
        name=f'configfactory-backup-{timezone.now()}.json',
        content=ContentFile(json.dumps(data, indent=4))
    )
    backup.user = user
    backup.comment = comment
    backup.save()

    # Notify about created backup
    backup_created.send(sender=Backup, backup=backup)

    return backup


def load_backup(backup: Backup, user: User = None):

    with backup.data_file.open() as fp:
        data = json.loads(fp.read())

    environments = data.get('environments', [])

    for item in environments:

        environment_id = item['id']
        alias = item['alias']

        try:
            environment = Environment.objects.get(pk=environment_id)
        except Environment.DoesNotExist:
            environment = Environment(pk=environment_id)

        if environment.alias != alias:
            Environment.objects.filter(alias=alias).delete()

        environment.alias = alias
        environment.name = item['name']
        environment.order = item.get('order', 0)
        environment.is_active = item.get('is_active', True)
        environment.created_at = item['created_at']
        environment.updated_at = item['updated_at']
        environment.save()

    for item in environments:

        environment_id = item['id']
        environment = Environment.objects.get(pk=environment_id)

        fallback_alias = item['fallback']

        if not fallback_alias:
            continue

        try:
            fallback = Environment.objects.get(alias=fallback_alias)
        except Environment.DoesNotExist:
            continue

        environment.fallback = fallback
        environment.save(update_fields=['fallback'])

    components = data.get('components', [])

    for item in components:

        component_id = item['id']
        alias = item['alias']

        try:
            component = Component.objects.get(pk=component_id)
        except Component.DoesNotExist:
            component = Component(pk=component_id)

        if component.alias != alias:
            Component.objects.filter(alias=alias).delete()

        component.alias = alias
        component.name = item['name']
        component.schema_json = item['schema_json']
        component.is_global = item['is_global']
        component.require_schema = item['require_schema']
        component.strict_keys = item['strict_keys']
        component.is_active = item['is_active']
        component.created_at = item['created_at']
        component.updated_at = item['updated_at']
        component.save()

    for environment, component_data in data.get('configs', {}).items():
        for component, data in component_data.items():
            configstore.update(environment, component, data=data)

    # Notify about loaded backup
    backup_loaded.send(sender=Backup, backup=backup, user=user)


def clean_backups():

    threshold = timezone.now() - timezone.timedelta(seconds=settings.BACKUPS_CLEAN_THRESHOLD)

    Backup.objects.auto().filter(created_at__lt=threshold).delete()

    # Notify about cleaned backups
    backups_cleaned.send(sender=Backup)
