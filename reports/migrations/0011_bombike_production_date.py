# Generated by Django 4.0.6 on 2022-10-19 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0010_remove_bombike_model_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='bombike',
            name='production_date',
            field=models.DateField(null=True),
        ),
    ]
