# Generated by Django 4.0.6 on 2022-08-24 07:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0005_bikereport_bombike_delete_bike'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bikereport',
            name='ebike',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='bikereport',
            name='first_prod_date',
            field=models.DateField(default=datetime.date(1974, 1, 1)),
        ),
        migrations.AlterField(
            model_name='bikereport',
            name='has_attachment',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='testreportcombo',
            name='created_date',
            field=models.DateField(default=datetime.date(1974, 1, 1)),
        ),
        migrations.AlterField(
            model_name='testreportpart',
            name='created_date',
            field=models.DateField(default=datetime.date(1974, 1, 1)),
        ),
    ]
