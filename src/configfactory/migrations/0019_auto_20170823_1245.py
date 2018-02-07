# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-23 12:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configfactory', '0018_auto_20170823_0633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='config',
            name='data',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='config',
            unique_together=set([('environment', 'component')]),
        ),
    ]
