# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-22 11:31
from __future__ import unicode_literals

from django.db import migrations


def create_config_db_store(apps, schema_editor):

    Component = apps.get_model('configfactory', 'Component')
    Config = apps.get_model('configfactory', 'Config')

    for component in Component.objects.all():
        config, created = Config.objects.get_or_create(component=component.alias)
        config.settings_json = component.settings_json
        config.save()


class Migration(migrations.Migration):

    dependencies = [
        ('configfactory', '0013_config'),
    ]

    operations = [
        migrations.RunPython(
            code=create_config_db_store,
            reverse_code=migrations.RunPython.noop
        ),
    ]
