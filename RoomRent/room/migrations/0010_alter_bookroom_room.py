# Generated by Django 4.2.7 on 2024-03-05 14:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0009_alter_bookroom_room'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookroom',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='room.room'),
        ),
    ]
