# Generated by Django 4.2.2 on 2024-02-23 13:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0002_room_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='listed_date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='room',
            name='amenities',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='room',
            name='detailedRoomAddress',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='room',
            name='roomDescription',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='room',
            name='rules',
            field=models.TextField(default='No Rules are added to this room'),
        ),
    ]
