# Generated by Django 3.0.3 on 2020-07-28 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='creator',
            field=models.CharField(max_length=100),
        ),
    ]
