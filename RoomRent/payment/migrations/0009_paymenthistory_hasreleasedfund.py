# Generated by Django 4.2.7 on 2024-03-31 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0008_delete_mybalance'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymenthistory',
            name='hasReleasedFund',
            field=models.BooleanField(default=False),
        ),
    ]
