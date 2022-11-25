# Generated by Django 4.0.6 on 2022-09-07 03:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test_lab_schedule', '0004_reporter_email'),
    ]

    operations = [
        migrations.RenameField(
            model_name='labtestinfo',
            old_name='test_name',
            new_name='test_full_name',
        ),
        migrations.AddField(
            model_name='labtestinfo',
            name='test_acronym',
            field=models.CharField(default='test', max_length=32),
            preserve_default=False,
        ),
    ]
