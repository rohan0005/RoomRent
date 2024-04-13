# Generated by Django 4.2.7 on 2024-04-13 05:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('room', '0029_room_isundermaintenance'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomIssuesOrMaintenance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issuedDate', models.DateTimeField(default=django.utils.timezone.now)),
                ('type', models.CharField(max_length=100)),
                ('message', models.TextField()),
                ('status', models.CharField(max_length=100)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='room.room')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
