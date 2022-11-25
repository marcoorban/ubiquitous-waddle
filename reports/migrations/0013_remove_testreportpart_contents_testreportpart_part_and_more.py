# Generated by Django 4.0.6 on 2022-10-21 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0012_rename_pid_bombike_report'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testreportpart',
            name='contents',
        ),
        migrations.AddField(
            model_name='testreportpart',
            name='part',
            field=models.ManyToManyField(related_name='trps_used_in', to='reports.part'),
        ),
        migrations.AlterField(
            model_name='testreportcombo',
            name='part',
            field=models.ManyToManyField(related_name='trcs_used_in', to='reports.part'),
        ),
        migrations.AlterField(
            model_name='testreportcombo',
            name='trp',
            field=models.ManyToManyField(related_name='trcs_used_in', to='reports.testreportpart'),
        ),
    ]
