# Generated by Django 4.0.6 on 2022-09-07 03:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test_lab_schedule', '0010_alter_sample_part2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='lims',
            field=models.CharField(max_length=10),
        ),
    ]
