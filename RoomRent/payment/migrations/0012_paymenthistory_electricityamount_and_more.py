# Generated by Django 4.2.7 on 2024-05-17 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0011_paymenthistory_trashcharge_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymenthistory',
            name='electricityAmount',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='paymenthistory',
            name='electricityUnit',
            field=models.IntegerField(default=0),
        ),
    ]
