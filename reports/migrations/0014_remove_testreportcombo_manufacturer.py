# Generated by Django 4.0.6 on 2022-10-25 08:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0013_remove_testreportpart_contents_testreportpart_part_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testreportcombo',
            name='manufacturer',
        ),
    ]
