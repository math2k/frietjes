# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-05-25 19:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0035_notificationrequest_all_outings'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodProviderType',
            fields=[
                ('name', models.CharField(choices=[(b'takeaway', b'Takeaway'), (b'restaurant', b'Restaurant'), (b'shop', b'Shop')], max_length=50, primary_key=True, serialize=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='foodprovider',
            name='type',
        ),
        migrations.AddField(
            model_name='foodprovider',
            name='type',
            field=models.ManyToManyField(to='app.FoodProviderType'),
        ),
    ]
