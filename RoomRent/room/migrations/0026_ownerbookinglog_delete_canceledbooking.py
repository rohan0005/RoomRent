# Generated by Django 4.2.7 on 2024-04-10 13:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('room', '0025_rename_bookinglog_tenantbookinglog'),
    ]

    operations = [
        migrations.CreateModel(
            name='OwnerBookingLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bookingDate', models.DateTimeField(default=django.utils.timezone.now)),
                ('canceledDate', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(default='Cancelled', max_length=100)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='room.room')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='canceledBooking',
        ),
    ]
