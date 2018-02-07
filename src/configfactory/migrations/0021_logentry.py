# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-15 12:57
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('configfactory', '0020_auto_20170911_1857'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.IntegerField(blank=True, null=True, verbose_name='object id')),
                ('object_repr', models.CharField(blank=True, max_length=128, null=True, verbose_name='object repr')),
                ('action', models.CharField(choices=[('create', 'create'), ('update', 'update'), ('delete', 'delete')], db_index=True, max_length=128, verbose_name='action')),
                ('action_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='action time')),
                ('old_data_json', models.TextField(blank=True, verbose_name='old data JSON')),
                ('new_data_json', models.TextField(blank=True, verbose_name='new data JSON')),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType', verbose_name='content type')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'ordering': ('-action_time',),
            },
        ),
    ]
