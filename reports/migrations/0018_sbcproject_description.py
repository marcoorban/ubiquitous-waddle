# Generated by Django 4.0.6 on 2022-11-08 03:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0017_remove_sbcproject_trp_sbcproject_trp'),
    ]

    operations = [
        migrations.AddField(
            model_name='sbcproject',
            name='description',
            field=models.CharField(default='', max_length=512),
        ),
    ]