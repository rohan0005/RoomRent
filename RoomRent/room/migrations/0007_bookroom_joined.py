# Generated by Django 4.2.2 on 2024-02-27 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0006_rename_book_bookroom'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookroom',
            name='joined',
            field=models.BooleanField(default=False),
        ),
    ]
