# Generated by Django 4.2.7 on 2023-12-27 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_userprofilepicture_image_userdocument'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdocument',
            name='image',
            field=models.ImageField(upload_to='Owner Citizenship'),
        ),
    ]
