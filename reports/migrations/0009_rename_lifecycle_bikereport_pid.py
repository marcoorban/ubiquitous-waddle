# Generated by Django 4.0.6 on 2022-09-19 07:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0008_rename_pid_bikereport_lifecycle'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bikereport',
            old_name='lifecycle',
            new_name='pid',
        ),
    ]
