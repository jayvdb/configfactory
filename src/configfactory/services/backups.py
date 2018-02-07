import base64
import zlib

from django.conf import settings
from django.utils import timezone

from configfactory import configstore
from configfactory.models import Backup, Component, Environment
from configfactory.signals import (
    backup_created,
    backup_loaded,
    backups_cleaned,
)
from configfactory.utils import json


def create_backup(user=None, comment=None):

    environments_data = []
    components_data = []
    configs_data = []

    for environment in Environment.objects.all():
        environments_data.append({
            'name': environment.name,
            'alias': environment.alias,
            'order': environment.order,
            'fallback_id': environment.fallback_id,
            'is_active': environment.is_active,
            'created_at': environment.created_at,
            'updated_at': environment.updated_at,
        })

    for component in Component.objects.all():
        components_data.append({
            'name': component.name,
            'alias': component.alias,
            'schema_json': component.schema_json,
            'is_global': component.is_global,
            'require_schema': component.require_schema,
            'strict_keys': component.strict_keys,
            'created_at': component.created_at,
            'updated_at': component.updated_at,
        })

    for environment in Environment.objects.all():
        for component in Component.objects.all():
            configs_data.append({
                'environment': environment.alias,
                'component': component.alias,
                'settings': configstore.backend.get_data(
                    environment=environment.alias,
                    component=component.alias
                ),
            })

    backup = Backup()
    backup.environments_data = _encode_data(environments_data)
    backup.components_data = _encode_data(components_data)
    backup.configs_data = _encode_data(configs_data)
    backup.user = user
    backup.comment = comment
    backup.save()

    # Notify about created backup
    backup_created.send(sender=Backup, backup=backup)

    return backup


def load_backup(backup, user=None):

    environments = _decode_data(backup.environments_data)
    components = _decode_data(backup.components_data)
    configs = _decode_data(backup.configs_data)

    for data in environments:

        alias = data['alias']
        name = data['name']
        order = data['order']
        fallback_id = data['fallback_id']
        is_active = data['is_active']
        created_at = data['created_at']
        updated_at = data['updated_at']

        try:
            environment = Environment.objects.get(alias=alias)
        except Environment.DoesNotExist:
            environment = Environment(alias=alias)

        environment.name = name
        environment.order = order
        environment.fallback_id = fallback_id
        environment.is_active = is_active
        environment.created_at = created_at
        environment.updated_at = updated_at
        environment.save()

    for data in components:

        alias = data['alias']
        name = data['name']
        schema_json = data['schema_json']
        is_global = data['is_global']
        require_schema = data['require_schema']
        strict_keys = data['strict_keys']
        created_at = data['created_at']
        updated_at = data['updated_at']

        try:
            component = Component.objects.get(alias=alias)
        except Component.DoesNotExist:
            component = Component(alias=alias)

        component.name = name
        component.schema_json = schema_json
        component.is_global = is_global
        component.require_schema = require_schema
        component.strict_keys = strict_keys
        component.created_at = created_at
        component.updated_at = updated_at
        component.save()

    for data in configs:

        environment = data['environment']
        component = data['component']
        settings_data = data['settings']

        configstore.update_settings(
            environment=environment,
            component=component,
            settings=settings_data
        )

    # Notify about loaded backup
    backup_loaded.send(sender=Backup, backup=backup, user=user)


def clean_backups():

    threshold = timezone.now() - timezone.timedelta(
        seconds=settings.BACKUPS_CLEAN_THRESHOLD
    )

    Backup.objects.auto().filter(
        created_at__lt=threshold
    ).delete()

    # Notify about cleaned backups
    backups_cleaned.send(sender=Backup)


def _encode_data(data):
    data = json.dumps(data, compress=True)
    return base64.b64encode(
        zlib.compress(data.encode())
    ).decode()


def _decode_data(data):
    data = zlib.decompress(
        base64.b64decode(data)
    ).decode()
    return json.loads(data)
