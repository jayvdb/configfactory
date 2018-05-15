# Generated by Django 2.0.2 on 2018-05-15 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configfactory', '0041_apisettings_is_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='backup',
            name='data_file',
            field=models.FileField(default='test', upload_to=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='backup',
            name='components_data',
            field=models.TextField(default='{}'),
        ),
        migrations.AlterField(
            model_name='backup',
            name='configs_data',
            field=models.TextField(default='{}'),
        ),
        migrations.AlterField(
            model_name='backup',
            name='environments_data',
            field=models.TextField(default='{}'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='last name'),
        ),
    ]
