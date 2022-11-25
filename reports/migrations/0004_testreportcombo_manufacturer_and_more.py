# Generated by Django 4.0.6 on 2022-08-12 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_testreportcombo_created_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='testreportcombo',
            name='manufacturer',
            field=models.CharField(default='N/A', max_length=512),
        ),
        migrations.AddField(
            model_name='testreportpart',
            name='manufacturer',
            field=models.CharField(default='N/A', max_length=512),
        ),
    ]