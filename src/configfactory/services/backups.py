from django.conf import settings
from django.core import serializers
from django.utils import timezone

from configfactory.models import Backup, Component, Config, Environment, User
from configfactory.signals import (
    backup_created,
    backup_loaded,
    backups_cleaned,
)


def create_backup(user: User = None, comment: str = None) -> Backup:

    backup = Backup()
    backup.environments = serializers.serialize('python', Environment.objects.all())
    backup.components = serializers.serialize('python', Component.objects.all())
    backup.configs = serializers.serialize('python', Config.objects.all())
    backup.user = user
    backup.comment = comment
    backup.save()

    # Notify about created backup
    backup_created.send(sender=Backup, backup=backup)

    return backup


def load_backup(backup: Backup, user: User = None):

    environments = serializers.deserialize('python', backup.environments)
    components = serializers.deserialize('python', backup.components)
    configs = serializers.deserialize('python', backup.configs)

    for environment in environments:
        environment.save()

    for component in components:
        component.save()

    for config in configs:
        config.save()

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
