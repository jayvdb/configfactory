# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-25 12:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configfactory', '0004_auto_20170724_1421'),
    ]

    operations = [
        migrations.AddField(
            model_name='component',
            name='settings_json',
            field=models.TextField(blank=True, default='{}', null=True),
        ),
    ]
