# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-26 12:37
import json

from django.db import migrations


def set_schema_json(apps, schema_editor):

    Component = apps.get_model('configfactory', 'Component')

    for component in Component.objects.all():
        component.schema_json = json.dumps(component.schema)
        component.save(update_fields=['schema_json'])


class Migration(migrations.Migration):

    dependencies = [
        ('configfactory', '0008_component_schema_json'),
    ]

    operations = [
        migrations.RunPython(
            code=set_schema_json,
            reverse_code=migrations.RunPython.noop
        ),
    ]
