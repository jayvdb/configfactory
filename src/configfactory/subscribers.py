import copy

import dictdiffer
from django.contrib.auth.models import Group
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import pre_save
from django.dispatch import receiver

from configfactory.models import Backup, Component, Environment, User
from configfactory.models.api_settings import APISettings
from configfactory.services.apisettings import generate_api_token
from configfactory.services.configsettings import get_settings, update_settings
from configfactory.services.logs import (
    log_action,
    log_create_object,
    log_delete_object,
    log_update_object,
)
from configfactory.signals import (
    backup_created,
    backup_loaded,
    backups_cleaned,
    component_alias_changed,
    component_created,
    component_deleted,
    component_updated,
    environment_created,
    environment_deleted,
    environment_updated,
    group_created,
    group_deleted,
    group_updated,
    settings_updated,
    user_created,
    user_deleted,
    user_updated,
)


@receiver(user_logged_in, sender=User)
def user_logged_in_handler(sender, request, user, **kwargs):

    log_action(action='user login', user=user)


@receiver(user_logged_out, sender=User)
def user_logged_out_handler(sender, request, user, **kwargs):

    log_action(action='user logout', user=user)


@receiver(group_created, sender=Group)
def group_created_handler(sender, group, **kwargs):

    log_create_object(
        instance=group,
        fields=kwargs.get('fields'),
        user=kwargs.get('user'),
    )


@receiver(group_updated, sender=Group)
def group_updated_handler(sender, group, old_data, **kwargs):

    log_update_object(
        instance=group,
        old_data=old_data,
        fields=kwargs.get('fields'),
        user=kwargs.get('user'),
    )


@receiver(group_deleted, sender=Group)
def group_deleted_handler(sender, group, **kwargs):

    log_delete_object(
        instance=group,
        user=kwargs.get('user'),
    )


@receiver(pre_save, sender=APISettings)
def set_api_token(instance: APISettings, **kwargs):
    if not instance.token:
        instance.token = generate_api_token()


@receiver(user_created, sender=User)
def user_created_handler(sender, user, **kwargs):

    log_create_object(
        instance=user,
        fields=kwargs.get('fields'),
        user=kwargs.get('current_user'),
    )


@receiver(user_updated, sender=User)
def user_updated_handler(sender, user, old_data, **kwargs):

    log_update_object(
        instance=user,
        old_data=old_data,
        fields=kwargs.get('fields'),
        user=kwargs.get('current_user'),
    )


@receiver(user_deleted, sender=User)
def user_deleted_handler(sender, user, **kwargs):

    log_delete_object(
        instance=user,
        user=kwargs.get('current_user'),
    )


@receiver(pre_save, sender=Environment)
def environment_pre_save_handler(sender, instance, **kwargs):
    if not instance.pk:
        environment = Environment.objects.order_by('-order').first()
        if environment and not instance.order:
            instance.order = environment.order + 1


@receiver(environment_created, sender=Environment)
def environment_created_handler(sender, environment, **kwargs):

    log_create_object(
        instance=environment,
        fields=kwargs.get('fields'),
        user=kwargs.get('user'),
    )


@receiver(environment_updated, sender=Environment)
def environment_updated_handler(sender, environment, old_data, **kwargs):

    log_update_object(
        instance=environment,
        old_data=old_data,
        fields=kwargs.get('fields'),
        user=kwargs.get('user'),
    )


@receiver(environment_deleted, sender=Environment)
def environment_deleted_handler(sender, environment, **kwargs):

    log_delete_object(
        instance=environment,
        user=kwargs.get('user'),
    )


@receiver(component_created, sender=Component)
def component_created_handler(sender, component, **kwargs):

    log_create_object(
        instance=component,
        fields=kwargs.get('fields'),
        user=kwargs.get('user'),
    )


@receiver(component_updated, sender=Component)
def component_updated_handler(sender, component, old_data, **kwargs):

    log_entry = log_update_object(
        instance=component,
        old_data=old_data,
        new_data=kwargs.get('new_data'),
        fields=kwargs.get('fields'),
        user=kwargs.get('user'),
    )

    for action, field, values in log_entry.diff_data:
        if action == dictdiffer.CHANGE and field == 'alias':
            component_alias_changed.send(
                sender=Component,
                component=component,
                old_alias=values[0],
                new_alias=values[1]
            )


@receiver(component_alias_changed, sender=Component)
def component_alias_changed_handler(sender, component: Component, old_alias: str, **kwargs):

    for environment in Environment.objects.all():

        data_copy = copy.deepcopy(get_settings(
            environment=environment,
            component=old_alias,
        ))

        update_settings(
            environment=environment,
            component=component,
            data=data_copy,
            run_validation=False
        )


@receiver(settings_updated, sender=Component)
def settings_updated_handler(sender, component, environment, old_settings: dict, new_settings: dict, **kwargs):

    log_update_object(
        instance=component,
        old_data={
            'settings': {
                environment.alias: old_settings
            }
        },
        new_data={
            'settings': {
                environment.alias: new_settings
            }
        },
        user=kwargs.get('user'),
    )


@receiver(component_deleted, sender=Component)
def component_deleted_handler(sender, component, **kwargs):

    log_delete_object(
        instance=component,
        user=kwargs.get('user'),
    )


@receiver(backup_created, sender=Backup)
def backup_created_handler(sender, backup, **kwargs):

    log_create_object(
        instance=backup,
        fields=['comment'],
        user=backup.user,
    )


@receiver(backup_loaded, sender=Backup)
def backup_loaded_handler(sender, backup, **kwargs):

    log_action(
        action='load backup',
        user=kwargs.get('user'),
        instance=backup
    )


@receiver(backups_cleaned, sender=Backup)
def backups_cleaned_handler(sender, **kwargs):

    log_action('cleanup backups')
