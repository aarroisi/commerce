# Generated by Django 3.0.3 on 2020-07-29 12:47

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_auto_20200729_1927'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]