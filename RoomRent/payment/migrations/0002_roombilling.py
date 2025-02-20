# Generated by Django 4.2.7 on 2024-03-12 18:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0015_electricityunitdetail'),
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomBilling',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('electricityUnit', models.IntegerField()),
                ('electricityAmount', models.IntegerField()),
                ('totalRoomRentAmount', models.IntegerField()),
                ('bookedRoom', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='room.bookroom')),
            ],
        ),
    ]
