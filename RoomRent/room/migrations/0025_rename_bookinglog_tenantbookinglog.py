# Generated by Django 4.2.7 on 2024-04-10 13:12

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('room', '0024_roomfeedbacks_feedbackdate_roomfeedbacks_rating'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BookingLog',
            new_name='TenantBookingLog',
        ),
    ]
