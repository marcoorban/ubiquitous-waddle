# Generated by Django 4.0.6 on 2022-09-07 06:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('test_lab_schedule', '0014_project_delete_projects'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='test_lab_schedule.project'),
        ),
    ]
