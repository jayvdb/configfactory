# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-17 06:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('alias', models.CharField(max_length=64, unique=True)),
                ('settings', models.TextField(default='{}')),
                ('settings_development', models.TextField(default='{}')),
                ('settings_staging', models.TextField(default='{}')),
                ('settings_production', models.TextField(default='{}')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
    ]
