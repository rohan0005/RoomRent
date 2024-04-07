# Generated by Django 4.2.7 on 2024-04-07 12:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0023_delete_electricityunitdetail'),
    ]

    operations = [
        migrations.AddField(
            model_name='roomfeedbacks',
            name='feedbackDate',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='roomfeedbacks',
            name='rating',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
